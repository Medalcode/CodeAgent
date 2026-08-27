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
import sys
import time
import traceback
import urllib.parse
import urllib.request
import webbrowser
import zipfile

PORT = 8000
OLLAMA_TARGET = "http://localhost:11434"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER_START_TIME = time.time()
METRICS_COUNTERS = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0
}


def _safe_print(*args, **kwargs):
    """Imprime texto de forma segura sin crash por UnicodeEncodeError en Windows cp1252."""
    msg = " ".join(str(a) for a in args)
    try:
        print(msg, **kwargs)
    except UnicodeEncodeError:
        safe_msg = msg.encode("ascii", errors="ignore").decode("ascii")
        print(safe_msg, **kwargs)


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
        self.end_headers()

    def do_GET(self):
        METRICS_COUNTERS["total_requests"] += 1
        clean_path = self.path.split('?')[0]
        if clean_path in ("/", "", "/ui", "/app", "/index.html", "/chat", "/editor"):
            self.path = "/localcode_claude_ui.html"
            super().do_GET()
        elif clean_path.startswith("/metrics"):
            self.handle_metrics()
        elif clean_path.startswith("/api/openapi.json"):
            self.handle_openapi_spec()
        elif clean_path.startswith("/docs"):
            self.handle_docs()
        elif clean_path.startswith("/api/workspace/tree"):
            self.handle_workspace_tree()
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
                    "rutas_disponibles": ["/", "/localcode_claude_ui.html", "/docs", "/metrics", "/api/agent/chat", "/api/workspace/tree"]
                }, 404)

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
        elif self.path.startswith("/api/workspace/save"):
            self.handle_save_file()
        elif self.path.startswith("/api/agent/chat"):
            self.handle_agent_chat()
        elif self.path.startswith("/api/chat") or self.path.startswith("/api/tags"):
            self.proxy_to_ollama("POST")
        else:
            super().do_POST()

    def _send_json(self, data, code=200):
        self.send_response(code)
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

        ignore_dirs = {'.git', 'node_modules', 'venv', '.venv', '__pycache__', 'chroma_db', 'graphify-out', '.idea', '.vscode'}
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
        data = self._get_post_body()
        folder_path = data.get("path", "").strip()
        if not folder_path:
            folder_path = os.getcwd()

        folder_path = os.path.abspath(folder_path)
        if not os.path.exists(folder_path):
            self._send_json({"success": False, "error": f"La ruta especificada no existe: {folder_path}"}, 404)
            return

        files = self._scan_folder(folder_path)
        self._send_json({"success": True, "path": folder_path, "files": files})

    def handle_workspace_tree(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        folder_path = params.get("path", [os.getcwd()])[0]
        folder_path = os.path.abspath(folder_path)

        if not os.path.exists(folder_path):
            self._send_json({"success": False, "error": "Ruta no encontrada"}, 404)
            return

        files = self._scan_folder(folder_path)
        self._send_json({"success": True, "path": folder_path, "files": files})

    def handle_save_file(self):
        data = self._get_post_body()
        rel_or_abs = data.get("filePath", "").strip()
        content = data.get("content", "")

        if not rel_or_abs:
            self._send_json({"success": False, "error": "Ruta de archivo no válida"}, 400)
            return

        target_file = rel_or_abs if os.isabs(rel_or_abs) else os.path.abspath(os.path.join(os.getcwd(), rel_or_abs))
        try:
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(content)
            self._send_json({"success": True, "path": target_file})
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

    def handle_agent_chat(self):
        data = self._get_post_body()
        prompt = data.get("prompt", "").strip()
        raw_model = data.get("model") or data.get("model_name") or "qwen2.5-coder:14b"
        agent_type = data.get("agent_type", "CodeAgent Developer")

        if raw_model in ("OpenAI", "gpt-4o-mini", "gpt-4o"):
            provider = "OpenAI"
            model_name = "gpt-4o-mini"
        else:
            provider = "Ollama (Local)"
            model_name = "qwen2.5-coder:14b" if raw_model in ("Ollama (Local)", "Ollama", "") else raw_model

        try:
            from agents import DEFAULT_AGENT_TOOLS
            default_tools = DEFAULT_AGENT_TOOLS
        except ImportError:
            default_tools = ["Archivos Locales", "Terminal Integrada", "Git", "Github"]

        selected_tools = data.get("selected_tools", default_tools)

        if not prompt:
            self._send_json({"success": False, "error": "Prompt vacío"}, 400)
            return

        _safe_print(f"\n[LocalCode Server] 🚀 Petición enviada a /api/agent/chat | Agente: {agent_type} | Proveedor: {provider} | Modelo: {model_name}")
        _safe_print(f"[LocalCode Server] 🛠️ Herramientas activas: {', '.join(selected_tools)}")

        api_key = data.get("api_key", "")
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        try:
            import main as codeagent_main
            respuesta, metricas = codeagent_main.ejecutar_agentes(
                user_prompt=prompt,
                provider=provider,
                model_name=model_name,
                api_key=api_key,
                agent_type=agent_type,
                selected_tools=selected_tools
            )
            _safe_print(f"[LocalCode Server] ✅ Agente respondió con éxito en {metricas.get('tiempo_segundos', 0)}s\n")
            self._send_json({"success": True, "respuesta": respuesta, "metricas": metricas})
        except Exception as e:
            _safe_print(f"[LocalCode Server] ❌ Error en Agente: {e}\n")
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
    candidate_ports = [PORT, 8080, 8001, 8002]
    httpd = None
    selected_port = PORT

    for p in candidate_ports:
        try:
            httpd = ThreadedTCPServer(("", p), LocalCodeProxyHandler)
            selected_port = p
            break
        except OSError:
            continue

    if not httpd:
        _safe_print(f"❌ Error: No se pudo abrir el servidor en ninguno de los puertos {candidate_ports}.")
        sys.exit(1)

    url = f"http://localhost:{selected_port}/localcode_claude_ui.html"
    print("=" * 65)
    print(f"🚀 Servidor LocalCode Multihilo iniciado en: {url}")
    print(f"🔗 Proxy conector activado hacia Ollama: {OLLAMA_TARGET}")
    print("💡 Cierra esta ventana o presiona Ctrl+C para detener.")
    print("=" * 65 + "\n")
    webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido.")


if __name__ == "__main__":
    main()
