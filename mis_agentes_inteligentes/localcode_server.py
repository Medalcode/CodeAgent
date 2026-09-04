#!/usr/bin/env python3
"""
LocalCode Proxy Server & Static Host
Servidor local en Python (0 dependencias externas) que sirve localcode_claude_ui.html
y actúa como proxy transparente hacia Ollama (http://localhost:11434),
eliminando por completo los errores de CORS / NetworkError en el navegador.
"""
import http.server
import io
import json
import os
import socketserver
import subprocess
import sys
import threading
import time
import traceback
import urllib.parse
import urllib.request
import webbrowser
import zipfile
from typing import Any, Tuple

if sys.platform == "win32":
    _orig_popen_init = subprocess.Popen.__init__
    def _silent_popen_init(self, *args, **kwargs):
        kwargs["creationflags"] = kwargs.get("creationflags", 0) | getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        si = kwargs.get("startupinfo")
        if si is None:
            si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = getattr(subprocess, "SW_HIDE", 0)
        kwargs["startupinfo"] = si
        _orig_popen_init(self, *args, **kwargs)
    subprocess.Popen.__init__ = _silent_popen_init

import uuid
from mis_agentes_inteligentes.version import CODEAGENT_VERSION

PORT = int(os.environ.get("CODEAGENT_PORT", "8000"))
OLLAMA_TARGET = "http://localhost:11434"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACTIVE_WORKSPACE_DIR = BASE_DIR
RECENT_WORKSPACES = [BASE_DIR]
SERVER_START_TIME = time.time()
SERVER_VERSION = CODEAGENT_VERSION
SERVER_INSTANCE_ID = os.environ.get("CODEAGENT_INSTANCE_ID") or str(uuid.uuid4())
PARENT_PID = int(os.environ.get("CODEAGENT_PARENT_PID", "0"))
PARENT_CREATION_TIME = float(os.environ.get("CODEAGENT_PARENT_CREATION_TIME", "0.0"))

METRICS_COUNTERS = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0
}


_SERVER_LOCK = threading.Lock()


def _get_process_creation_time(pid: int) -> float:
    if pid <= 0:
        return 0.0
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if not handle:
                return 0.0
            c, e, k, u = ctypes.c_ulonglong(), ctypes.c_ulonglong(), ctypes.c_ulonglong(), ctypes.c_ulonglong()
            res = kernel32.GetProcessTimes(handle, ctypes.byref(c), ctypes.byref(e), ctypes.byref(k), ctypes.byref(u))
            kernel32.CloseHandle(handle)
            if res:
                return round((c.value / 10000000.0) - 11644473600.0, 3)
        except Exception:
            return 0.0
    return 0.0


def _is_parent_alive() -> bool:
    if PARENT_PID <= 0:
        return True
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            SYNCHRONIZE = 0x0010
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = kernel32.OpenProcess(SYNCHRONIZE | PROCESS_QUERY_LIMITED_INFORMATION, False, PARENT_PID)
            if not handle:
                return False
            exit_code = ctypes.c_ulong()
            kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
            kernel32.CloseHandle(handle)
            if exit_code.value != 259:
                return False
            if PARENT_CREATION_TIME > 0:
                curr_ctime = _get_process_creation_time(PARENT_PID)
                if curr_ctime > 0 and abs(curr_ctime - PARENT_CREATION_TIME) > 1.5:
                    return False
            return True
        except Exception:
            return False
    else:
        try:
            os.kill(PARENT_PID, 0)
            return True
        except OSError:
            return False


def _start_parent_monitor():
    if PARENT_PID <= 0:
        return
    def _monitor():
        while True:
            time.sleep(2)
            if not _is_parent_alive():
                _safe_print(f"[LocalCode Server] ⚠️ Proceso padre PID {PARENT_PID} finalizado o reciclado. Cerrando backend...")
                os._exit(0)
    t = threading.Thread(target=_monitor, daemon=True)
    t.start()


def _inc_metric(key: str):
    with _SERVER_LOCK:
        METRICS_COUNTERS[key] = METRICS_COUNTERS.get(key, 0) + 1


def _safe_print(*args, **kwargs):
    """Imprime texto de forma segura sin crash por UnicodeEncodeError en Windows cp1252."""
    msg = " ".join(str(a) for a in args)
    try:
        print(msg, **kwargs)
    except UnicodeEncodeError:
        safe_msg = msg.encode("ascii", errors="ignore").decode("ascii")
        print(safe_msg, **kwargs)
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if os.name == "nt" else 0

def get_sdd_health_dict() -> dict:
    status_str = "OK"
    parent_alive = False
    try:
        parent_alive = _is_parent_alive()
    except Exception:
        status_str = "DEGRADED"

    return {
        "status": status_str,
        "sdd_version": SERVER_VERSION,
        "certified_commit": "b0157240d41d3a81c0b3c68b94d2e3a46c90f874",
        "invariants_certified_count": 8,
        "parent_pid": PARENT_PID,
        "parent_alive": parent_alive,
        "pipeline_authority_active": True
    }


def handle_sse_events_dict(event: Any) -> str:
    """Serializa una instancia de Event o dict al formato Server-Sent Events (SSE)."""
    if hasattr(event, "task_id"):
        payload_dict = {
            "task_id": getattr(event, "task_id", ""),
            "event_type": getattr(event, "event_type", ""),
            "payload": getattr(event, "payload", {}),
            "timestamp": getattr(event, "timestamp", time.time()),
            "event_id": getattr(event, "event_id", None)
        }
    elif isinstance(event, dict):
        payload_dict = event
    else:
        payload_dict = {"event": str(event)}
        
    return f"data: {json.dumps(payload_dict)}\n\n"


class LocalCodeProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        _inc_metric("total_requests")
        clean_path = self.path.split('?')[0]
        if clean_path in ("/", "", "/ui", "/app", "/index.html", "/chat", "/editor", "/localcode_claude_ui.html"):
            self.path = "/mis_agentes_inteligentes/localcode_claude_ui.html"
            super().do_GET()
        elif clean_path in ("/api/health", "/api/server/health", "/api/server/identity"):
            self.handle_health()
        elif clean_path in ("/api/health/sdd", "/api/sdd/health"):
            self.handle_sdd_health()
        elif clean_path in ("/api/pipeline/events", "/api/events"):
            self.handle_sse_events()
        elif clean_path.startswith("/metrics"):
            self.handle_metrics()
        elif clean_path.startswith("/api/openapi.json"):
            self.handle_openapi_spec()
        elif clean_path.startswith("/docs"):
            self.handle_docs()
        elif clean_path.startswith("/api/workspace/tree"):
            self.handle_workspace_tree()
        elif clean_path.startswith("/api/tasks"):
            self.handle_tasks_get(clean_path)
        elif any(clean_path.startswith(p) for p in ("/api/chat", "/api/tags", "/api/version", "/api/generate", "/api/embeddings", "/v1/")):
            self.proxy_to_ollama("GET")
        else:
            # Fallback seguro para archivos estáticos existentes
            target_file = os.path.normpath(os.path.join(BASE_DIR, clean_path.lstrip("/")))
            if os.path.isfile(target_file):
                super().do_GET()
            else:
                self._send_json({
                    "error": "Ruta no encontrada (404)",
                    "path_solicitada": self.path,
                    "rutas_disponibles": ["/", "/localcode_claude_ui.html", "/docs", "/metrics", "/api/health", "/api/agent/chat", "/api/workspace/tree", "/api/tasks"]
                }, 404)

    def handle_health(self):
        self._send_json({
            "status": "ok",
            "service": "codeagent-backend",
            "version": SERVER_VERSION,
            "instance_id": SERVER_INSTANCE_ID,
            "process_id": os.getpid(),
            "parent_pid": PARENT_PID,
            "parent_creation_time": PARENT_CREATION_TIME,
            "port": PORT,
            "base_dir": os.path.abspath(BASE_DIR),
            "start_time": SERVER_START_TIME
        })

    def handle_sdd_health(self):
        _safe_print("[LocalCode Server] GET /api/health/sdd")
        self._send_json(get_sdd_health_dict())

    def handle_sse_events(self):
        """Maneja el streaming HTTP Server-Sent Events en GET /api/pipeline/events."""
        _safe_print("[LocalCode Server] SSE Client subscribed to /api/pipeline/events")
        
        target_task_id = None
        if "?" in self.path:
            query = self.path.split("?", 1)[1]
            for param in query.split("&"):
                if param.startswith("task_id="):
                    target_task_id = param.split("=", 1)[1]
                    
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        
        import queue
        q = queue.Queue(maxsize=100)
        
        def listener(ev: Any):
            if target_task_id and getattr(ev, "task_id", None) != target_task_id:
                return
            try:
                q.put_nowait(ev)
            except queue.Full:
                pass
                
        from runtime.event_bus import get_event_bus
        bus = get_event_bus()
        bus.subscribe(listener)
        
        try:
            while True:
                try:
                    ev = q.get(timeout=1.0)
                    formatted = handle_sse_events_dict(ev)
                    self.wfile.write(formatted.encode("utf-8"))
                    self.wfile.flush()
                except queue.Empty:
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
                if not _is_parent_alive():
                    break
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            bus.unsubscribe(listener)
            _safe_print("[LocalCode Server] SSE Client disconnected from /api/pipeline/events")

    def handle_server_shutdown(self):
        self._send_json({"success": True, "message": "Server shutting down"})
        def _async_exit():
            time.sleep(0.2)
            os._exit(0)
        threading.Thread(target=_async_exit, daemon=True).start()

    def handle_metrics(self):
        uptime = time.time() - SERVER_START_TIME
        metrics_text = f"""# HELP codeagent_uptime_seconds Uptime del servidor proxy localcode en segundos
# TYPE codeagent_uptime_seconds gauge
codeagent_uptime_seconds {uptime:.2f}

# HELP codeagent_requests_total Total de peticiones HTTP procesadas
# TYPE codeagent_requests_total counter
codeagent_requests_total {METRICS_COUNTERS['total_requests']}

# HELP codeagent_requests_success_total Peticiones HTTP completadas con exito
# TYPE codeagent_requests_success_total counter
codeagent_requests_success_total {METRICS_COUNTERS['successful_requests']}

# HELP codeagent_requests_failed_total Peticiones HTTP fallidas
# TYPE codeagent_requests_failed_total counter
codeagent_requests_failed_total {METRICS_COUNTERS['failed_requests']}
"""
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
        self.end_headers()
        self.wfile.write(metrics_text.encode("utf-8"))

    def handle_openapi_spec(self):
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "CodeAgent LocalCode API",
                "version": "2.4.0",
                "description": "API REST y Proxy Local para CodeAgent Developer y smolagents."
            },
            "paths": {
                "/api/agent/chat": {
                    "post": {
                        "summary": "Enviar petición al Agente CodeAgent Developer",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "prompt": {"type": "string"},
                                            "model": {"type": "string"},
                                            "agent_type": {"type": "string"},
                                            "selected_tools": {"type": "array", "items": {"type": "string"}}
                                        },
                                        "required": ["prompt"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {"description": "Respuesta del agente ejecutada con métricas"},
                            "400": {"description": "Prompt vacío"}
                        }
                    }
                },
                "/api/workspace/tree": {
                    "get": {
                        "summary": "Obtener árbol jerárquico de archivos del workspace",
                        "responses": {
                            "200": {"description": "Lista de archivos del proyecto local"}
                        }
                    }
                }
            }
        }
        self._send_json(spec)

    def handle_docs(self):
        html = """<!DOCTYPE html>
<html>
<head>
  <title>CodeAgent API Docs</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({ url: '/api/openapi.json', dom_id: '#swagger-ui' });
  </script>
</body>
</html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        if self.path.startswith("/api/workspace/open-folder"):
            self.handle_open_folder()
        elif self.path.startswith("/api/github/import"):
            self.handle_github_import()
        elif self.path.startswith("/api/workspace/save") or self.path.startswith("/api/fs/save"):
            self.handle_save_file()
        elif self.path.startswith("/api/terminal/approve"):
            self.handle_terminal_approve()
        elif self.path.startswith("/api/tasks"):
            self.handle_tasks_post(self.path.split('?')[0])
        elif self.path.startswith("/api/agent/chat"):
            self.handle_agent_chat()
        elif self.path.startswith("/api/server/shutdown"):
            self.handle_server_shutdown()
        elif self.path.startswith("/api/chat") or self.path.startswith("/api/tags"):
            self.proxy_to_ollama("POST")

    def handle_terminal_approve(self):
        data = self._get_post_body()
        comando = data.get("command", "").strip()
        approved = data.get("approved", False)

        if not comando:
            self._send_json({"success": False, "error": "Falta el comando a aprobar"}, 400)
            return

        if approved:
            try:
                from mis_agentes_inteligentes.tools import pre_approve_command
                pre_approve_command(comando)
                self._send_json({"success": True, "message": f"Comando '{comando}' pre-aprobado para ejecución."})
            except Exception as e:
                self._send_json({"success": False, "error": f"Error pre-aprobando comando: {e}"}, 500)
        else:
            self._send_json({"success": True, "message": f"Comando '{comando}' rechazado por el usuario."})

    def handle_tasks_get(self, clean_path: str):
        parts = [p for p in clean_path.split("/") if p]
        from runtime.runtime import get_runtime
        runtime = get_runtime()

        if len(parts) == 2:  # /api/tasks
            tasks = runtime.list_tasks()
            self._send_json({"success": True, "tasks": tasks})
        elif len(parts) == 3:  # /api/tasks/<task_id>
            task_id = parts[2]
            task = runtime.get_task(task_id)
            if not task:
                self._send_json({"success": False, "error": "Tarea no encontrada"}, 404)
            else:
                self._send_json({"success": True, "task": task})
        elif len(parts) == 4 and parts[3] == "events":  # /api/tasks/<task_id>/events
            task_id = parts[2]
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            since_id = int(params.get("since_id", [0])[0])
            events = runtime.get_events(task_id, since_id=since_id)
            self._send_json({"success": True, "task_id": task_id, "events": events})
        else:
            self._send_json({"error": "Ruta de tareas no válida"}, 400)

    def handle_tasks_post(self, clean_path: str):
        parts = [p for p in clean_path.split("/") if p]
        from runtime.runtime import get_runtime
        runtime = get_runtime()

        if len(parts) == 2:  # POST /api/tasks
            data = self._get_post_body()
            goal = data.get("goal", "").strip() or data.get("prompt", "").strip()
            project_path = data.get("project_path", "").strip() or ACTIVE_WORKSPACE_DIR
            if not goal:
                self._send_json({"success": False, "error": "Falta el objetivo ('goal')"}, 400)
                return
            task_id = runtime.start_task(goal=goal, project_path=project_path)
            self._send_json({"success": True, "task_id": task_id})
        elif len(parts) == 4 and parts[3] == "resume":  # POST /api/tasks/<task_id>/resume
            task_id = parts[2]
            res = runtime.resume_task(task_id)
            self._send_json({"success": res, "task_id": task_id})
        elif len(parts) == 4 and parts[3] == "pause":  # POST /api/tasks/<task_id>/pause
            task_id = parts[2]
            res = runtime.pause_task(task_id)
            self._send_json({"success": res, "task_id": task_id})
        elif len(parts) == 4 and parts[3] == "cancel":  # POST /api/tasks/<task_id>/cancel
            task_id = parts[2]
            res = runtime.cancel_task(task_id)
            self._send_json({"success": res, "task_id": task_id})
        else:
            self._send_json({"error": "Acción de tareas no válida"}, 400)

    def _send_json(self, data, code=200):
        self.send_response(code)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _get_post_body(self):
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len <= 0:
            return {}
        raw = self.rfile.read(content_len).decode("utf-8")
        try:
            return json.loads(raw)
        except Exception:
            return {}

    def _scan_folder(self, folder_path):
        files_found = []
        if not os.path.exists(folder_path):
            return files_found

        ignore_dirs = {'.git', 'node_modules', 'venv', '.venv', '__pycache__', 'chroma_db', 'graphify-out', '.idea', '.vscode', 'dist', 'build'}
        valid_exts = ('.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.json', '.md', '.txt', '.yml', '.yaml', '.toml', '.sh', '.bat', '.c', '.cpp', '.h', '.java', '.go', '.rs')

        for root, dirs, filenames in os.walk(folder_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for f in filenames:
                if f.endswith(valid_exts):
                    full = os.path.join(root, f)
                    rel = os.path.relpath(full, folder_path).replace("\\", "/")
                    try:
                        if os.path.getsize(full) <= 300000:
                            with open(full, encoding='utf-8', errors='replace') as file_obj:
                                content = file_obj.read()
                            files_found.append({"name": rel, "content": content})
                    except Exception:
                        pass
        files_found.sort(key=lambda x: x["name"])
        return files_found

    def handle_open_folder(self):
        global ACTIVE_WORKSPACE_DIR, RECENT_WORKSPACES
        data = self._get_post_body()
        folder_path = data.get("path", "").strip()
        if not folder_path:
            folder_path = ACTIVE_WORKSPACE_DIR

        folder_path = os.path.abspath(folder_path)
        if not os.path.exists(folder_path):
            self._send_json({"success": False, "error": f"La ruta especificada no existe: {folder_path}"}, 404)
            return

        ACTIVE_WORKSPACE_DIR = folder_path
        if folder_path not in RECENT_WORKSPACES:
            RECENT_WORKSPACES.insert(0, folder_path)

        try:
            from mis_agentes_inteligentes.tools import set_active_workspace
            set_active_workspace(folder_path)
        except Exception:
            pass

        files = self._scan_folder(folder_path)
        self._send_json({
            "success": True,
            "path": folder_path,
            "recent_workspaces": RECENT_WORKSPACES[:5],
            "files": files
        })

    def handle_workspace_tree(self):
        global ACTIVE_WORKSPACE_DIR
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        target = params.get("path", [ACTIVE_WORKSPACE_DIR])[0]
        folder_path = os.path.abspath(target) if target else ACTIVE_WORKSPACE_DIR

        if not os.path.exists(folder_path):
            folder_path = ACTIVE_WORKSPACE_DIR

        files = self._scan_folder(folder_path)
        self._send_json({
            "success": True,
            "path": folder_path,
            "recent_workspaces": RECENT_WORKSPACES[:5],
            "files": files
        })

    def handle_save_file(self):
        data = self._get_post_body()
        rel_or_abs = data.get("filePath", "").strip() or data.get("path", "").strip()
        content = data.get("content", "")

        if not rel_or_abs:
            self._send_json({"success": False, "error": "Ruta de archivo no válida"}, 400)
            return

        target_file = rel_or_abs if os.isabs(rel_or_abs) else os.path.abspath(os.path.join(os.getcwd(), rel_or_abs))
        try:
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(content)
            self._send_json({"success": True, "path": target_file, "filename": os.path.basename(target_file)})
        except Exception as e:
            self._send_json({"success": False, "error": str(e)}, 500)

    def handle_github_import(self):
        data = self._get_post_body()
        raw_repo = data.get("repo", "").strip()

        if not raw_repo:
            self._send_json({"success": False, "error": "Debes especificar una URL o repo"}, 400)
            return

        clean = raw_repo.replace("https://github.com/", "").replace("http://github.com/", "").strip("/")
        if clean.endswith(".git"):
            clean = clean[:-4]

        parts = clean.split("/")
        if len(parts) < 2:
            self._send_json({"success": False, "error": "Formato de repo no válido. Usa usuario/repositorio"}, 400)
            return

        owner, repo = parts[0], parts[1]
        zip_urls = [
            f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip",
            f"https://github.com/{owner}/{repo}/archive/refs/heads/master.zip"
        ]

        zip_content = None
        last_err = None
        for url in zip_urls:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "CodeAgent-LocalCode"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    zip_content = resp.read()
                    break
            except Exception as e:
                last_err = e

        if not zip_content:
            self._send_json({"success": False, "error": f"No se pudo descargar el repositorio {owner}/{repo}. Detalle: {last_err}"}, 500)
            return

        files_found = []
        valid_exts = ('.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.json', '.md', '.txt', '.yml', '.yaml', '.toml', '.sh', '.bat', '.c', '.cpp', '.h', '.java', '.go', '.rs')

        try:
            with zipfile.ZipFile(io.BytesIO(zip_content)) as zf:
                for member in zf.infolist():
                    if member.is_dir():
                        continue
                    filename = member.filename
                    parts = filename.split("/", 1)
                    rel_name = parts[1] if len(parts) > 1 else filename
                    if not rel_name or any(part.startswith(".") or part == "node_modules" for part in rel_name.split("/")):
                        continue

                    if rel_name.endswith(valid_exts) and member.file_size <= 300000:
                        try:
                            content_bytes = zf.read(member)
                            text = content_bytes.decode('utf-8', errors='replace')
                            files_found.append({"name": rel_name, "content": text})
                        except Exception:
                            pass

            files_found.sort(key=lambda x: x["name"])
            self._send_json({"success": True, "repo": f"{owner}/{repo}", "files": files_found})
        except Exception as e:
            self._send_json({"success": False, "error": f"Error al descomprimir el repositorio de GitHub: {e}"}, 500)

    def check_local_ollama_health(self) -> Tuple[bool, str]:
        """Verifica si el servicio Ollama local está activo en el endpoint configurado."""
        try:
            from config import OLLAMA_TARGET
        except ImportError:
            OLLAMA_TARGET = "http://localhost:11434"

        target_url = f"{OLLAMA_TARGET.rstrip('/')}/api/tags"
        try:
            req = urllib.request.Request(target_url, headers={"User-Agent": "CodeAgent-Server"})
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    return True, "OK"
        except Exception as e:
            return False, f"Local model runtime unavailable. Ollama is not running or cannot be reached at {OLLAMA_TARGET}."

        return False, f"Local model runtime unavailable. Ollama is not running at {OLLAMA_TARGET}."

    def handle_agent_chat(self):
        data = self._get_post_body()
        prompt = data.get("prompt", "").strip()
        agent_type = data.get("agent_type", "CodeAgent Developer")

        try:
            from config import DEFAULT_MODEL_NAME, DEFAULT_MODEL_PROVIDER
        except ImportError:
            DEFAULT_MODEL_PROVIDER = "Ollama (Local)"
            DEFAULT_MODEL_NAME = "qwen2.5-coder:14b"

        req_provider = data.get("provider") or data.get("model_provider") or ""
        req_model = data.get("model") or data.get("model_name") or ""

        # Modos Cloud estrictamente deshabilitados
        disallowed_cloud = ("openai", "anthropic", "groq", "gemini", "openrouter", "azure")
        prov_clean = str(req_provider).strip().lower()
        if any(c in prov_clean for c in disallowed_cloud):
            self._send_json({
                "success": False,
                "error": f"CodeAgent está configurado en MODO LOCAL-ONLY. El proveedor '{req_provider}' no está permitido. Utilice Ollama (Local).",
                "provider": "Ollama (Local)"
            }, 400)
            return

        provider = DEFAULT_MODEL_PROVIDER

        # Default inmutable al modelo local si no se especificó o si contenía identificadores cloud ajenos
        model_clean = str(req_model).strip().lower()
        if not req_model or any(k in model_clean for k in ("gpt-", "claude-", "gemini-", "groq/", "openrouter/", "https://", "^")):
            model_name = DEFAULT_MODEL_NAME
        else:
            model_name = req_model

        try:
            from agents import DEFAULT_AGENT_TOOLS
            default_tools = DEFAULT_AGENT_TOOLS
        except ImportError:
            default_tools = ["Archivos Locales", "Terminal Integrada", "Git", "Github"]

        selected_tools = data.get("selected_tools", default_tools)
        task_id = data.get("task_id", None)

        if not prompt:
            self._send_json({"success": False, "error": "Prompt vacío"}, 400)
            return

        # Chequeo de salud de Ollama si el proveedor es local
        if provider == "Ollama (Local)" and not os.environ.get("SKIP_OLLAMA_CHECK", ""):
            is_healthy, health_err = self.check_local_ollama_health()
            if not is_healthy:
                _safe_print(f"[LocalCode Server] ❌ {health_err}")
                self._send_json({
                    "success": False,
                    "error": health_err,
                    "provider": provider,
                    "model": model_name
                }, 503)
                return

        _safe_print(f"\n[LocalCode Server] 🚀 Petición enviada a /api/agent/chat | Agente: {agent_type} | Proveedor: {provider} | Modelo: {model_name}")
        _safe_print(f"[LocalCode Server] 🛠️ Herramientas activas: {', '.join(selected_tools)}")

        api_key = data.get("api_key", "")
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        try:
            from mis_agentes_inteligentes.tools import (
                clear_terminal_tasks_buffer,
                get_terminal_tasks_buffer,
                set_active_workspace,
            )
            set_active_workspace(ACTIVE_WORKSPACE_DIR)
            clear_terminal_tasks_buffer()
        except Exception:
            pass

        try:
            import main as codeagent_main
            _runner, metricas = codeagent_main.ejecutar_agentes(
                user_prompt=prompt,
                provider=provider,
                model_name=model_name,
                api_key=api_key,
                agent_type=agent_type,
                selected_tools=selected_tools,
                task_id=task_id,
                run_pipeline=False
            )
            
            from runtime.runtime import get_runtime
            runtime = get_runtime()
            
            # Start task asynchronously and offload execution to the daemon thread
            created_task_id = runtime.start_task(
                goal=prompt,
                project_path=ACTIVE_WORKSPACE_DIR,
                agent_runner=_runner,
                task_id=task_id
            )
            _safe_print(f"[LocalCode Server] Tarea delegada al runtime asíncrono con ID: {created_task_id}\n")
            
            import threading
            completion_event = threading.Event()
            result_data = {}
            
            def _on_event(ev):
                if ev.task_id == created_task_id:
                    if ev.event_type == "TASK_COMPLETED":
                        result_data["respuesta"] = ev.payload.get("output", "Completado.")
                        result_data["metricas"] = ev.payload.get("metrics", {})
                        completion_event.set()
                    elif ev.event_type == "TASK_CANCELLED":
                        result_data["error"] = "Tarea cancelada por el usuario."
                        completion_event.set()
                    elif ev.event_type == "TASK_FAILED":
                        result_data["error"] = ev.payload.get("error", "Fallo en pipeline.")
                        completion_event.set()
                        
            runtime.event_bus.subscribe(_on_event)
            try:
                completion_event.wait(timeout=3600)
            finally:
                runtime.event_bus.unsubscribe(_on_event)
                
            if "error" in result_data:
                _inc_metric("failed_requests")
                self._send_json({"success": False, "error": result_data["error"]}, 500)
                return
            
            _inc_metric("successful_requests")
            term_tasks = []
            try:
                from mis_agentes_inteligentes.tools import get_terminal_tasks_buffer
                term_tasks = get_terminal_tasks_buffer()
            except Exception:
                pass
                
            self._send_json({
                "success": True, 
                "respuesta": result_data.get("respuesta", "Completado"), 
                "metricas": result_data.get("metricas", metricas),
                "terminal_tasks": term_tasks
            })
        except Exception as e:
            _safe_print(f"[LocalCode Server] ❌ Error en Agente: {e}\n")
            _inc_metric("failed_requests")
            self._send_json({"success": False, "error": f"Error ejecutando Agente CodeAgent: {e}", "trace": traceback.format_exc()}, 500)

    def proxy_to_ollama(self, method):
        target_hosts = ["http://127.0.0.1:11434", "http://localhost:11434"]
        body = None
        if method == "POST":
            content_len = int(self.headers.get("Content-Length", 0))
            if content_len > 0:
                body = self.rfile.read(content_len)

        headers = {k: v for k, v in self.headers.items() if k.lower() not in ("host", "content-length")}
        last_error = None

        for host in target_hosts:
            target_url = f"{host}{self.path}"
            req = urllib.request.Request(target_url, data=body, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    self.send_response(resp.status)
                    for k, v in resp.headers.items():
                        if k.lower() not in ("transfer-encoding", "content-encoding", "access-control-allow-origin"):
                            self.send_header(k, v)
                    self.end_headers()

                    while True:
                        chunk = resp.read(8192)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        self.wfile.flush()
                return
            except Exception as e:
                last_error = e

        self.send_response(502)
        self.end_headers()
        err_msg = json.dumps({
            "error": "❌ LocalCode Proxy Server: Ollama NO disponible en http://127.0.0.1:11434.",
            "solucion": "Ejecuta 'ollama serve' en tu terminal o abre la app de Ollama desde tu menú de inicio para iniciar el servicio local.",
            "detalle": str(last_error)
        }, ensure_ascii=False)
        self.wfile.write(err_msg.encode("utf-8"))


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Servidor TCP/HTTP multihilo no bloqueante para peticiones concurrentes."""
    daemon_threads = True
    allow_reuse_address = True


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=0)
    args, _ = parser.parse_known_args()

    global PORT
    if args.port > 0:
        PORT = args.port

    _start_parent_monitor()

    try:
        httpd = ThreadedTCPServer(("", PORT), LocalCodeProxyHandler)
    except OSError as e:
        _safe_print(f"❌ Error: No se pudo abrir el servidor en el puerto asignado {PORT}: {e}")
        sys.exit(1)

    url = f"http://localhost:{PORT}/localcode_claude_ui.html"
    _safe_print("=" * 65)
    _safe_print(f"🚀 Servidor LocalCode Multihilo iniciado en: {url} (PID {os.getpid()})")
    _safe_print(f"🔗 Proxy conector activado hacia Ollama: {OLLAMA_TARGET}")
    _safe_print("💡 Cierra esta ventana o presiona Ctrl+C para detener.")
    _safe_print("=" * 65 + "\n")
    if os.environ.get("NO_BROWSER") != "1":
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        _safe_print("\n👋 Servidor detenido.")


if __name__ == "__main__":
    main()
