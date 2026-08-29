"""
CodeAgent Desktop Runner (v3.5)
Lanza CodeAgent y Ollama automáticamente en una ventana nativa de escritorio independiente.
"""
import contextlib
import os
import subprocess
import sys
import time
import urllib.request

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

import atexit
import json
import socket
import threading
from mis_agentes_inteligentes.version import CODEAGENT_VERSION

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_URL = "http://localhost:8000/localcode_claude_ui.html"
HEALTH_URL = "http://localhost:8000/api/health"
SHUTDOWN_URL = "http://localhost:8000/api/server/shutdown"
OLLAMA_API_URL = "http://localhost:11434/api/tags"

_SERVER_PROCESS: subprocess.Popen | None = None
_CURRENT_BACKEND_PORT: int = 0
_EXPECTED_INSTANCE_ID: str = ""
_STOPPING_LOCK = threading.Lock()
_IS_STOPPING = False


def _safe_print(*args, **kwargs):
    """Imprime texto de forma segura sin crash por UnicodeEncodeError en Windows cp1252."""
    msg = " ".join(str(a) for a in args)
    try:
        print(msg, **kwargs)
    except UnicodeEncodeError:
        safe_msg = msg.encode("ascii", errors="ignore").decode("ascii")
        print(safe_msg, **kwargs)


def get_process_creation_time(pid: int) -> float:
    """Retorna el timestamp de creación del proceso en segundos (Windows API / native)."""
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


def find_free_port() -> int:
    """Encuentra un puerto TCP disponible en localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        s.listen(1)
        return s.getsockname()[1]


def check_ollama_running() -> bool:
    """Verifica si el servicio Ollama está activo en el puerto 11434."""
    try:
        req = urllib.request.Request(OLLAMA_API_URL, headers={"User-Agent": "CodeAgent-Desktop"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def launch_ollama_bg():
    """Inicia el servicio Ollama ('ollama serve') en segundo plano si no está activo."""
    _safe_print("🦙 Auto-iniciando Servidor Ollama (Local LLM)...")
    try:
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        subprocess.Popen(
            ["ollama", "serve"],
            cwd=BASE_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )
        for i in range(12):
            time.sleep(1)
            if check_ollama_running():
                _safe_print("✅ Servicio Ollama listo en http://localhost:11434")
                return True
            _safe_print(f"⏳ Esperando arranque de Ollama ({i+1}/12s)...")
    except Exception as e:
        _safe_print(f"⚠️ Advertencia: No se pudo auto-iniciar Ollama automáticamente: {e}")
    return False


def verify_backend_identity(url: str = HEALTH_URL) -> dict | None:
    """Verifica si en la URL dada responde un backend de CodeAgent retornando su diccionario de identidad."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CodeAgent-Desktop-Check"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("service") == "codeagent-backend":
                    return data
    except Exception:
        pass
    return None


def is_backend_compatible(identity: dict | None) -> bool:
    """Comprueba pertenencia exclusiva de un backend al proceso Desktop actual."""
    if not identity:
        return False
    server_base = identity.get("base_dir", "")
    server_version = identity.get("version", "")
    parent_pid = identity.get("parent_pid", 0)
    parent_ctime = identity.get("parent_creation_time", 0.0)
    instance_id = identity.get("instance_id", "")

    same_base = os.path.normpath(server_base).lower() == os.path.normpath(BASE_DIR).lower()
    same_version = (server_version == CODEAGENT_VERSION)
    same_parent = (parent_pid == os.getpid())
    same_instance = (not _EXPECTED_INSTANCE_ID or instance_id == _EXPECTED_INSTANCE_ID)

    curr_ctime = get_process_creation_time(os.getpid())
    same_ctime = (parent_ctime > 0 and curr_ctime > 0 and abs(parent_ctime - curr_ctime) < 1.5) or (parent_ctime == 0.0)

    return same_base and same_version and same_parent and same_instance and same_ctime


def shutdown_remote_backend(shutdown_url: str = SHUTDOWN_URL) -> bool:
    """Solicita al backend en ejecución un cierre seguro mediante POST /api/server/shutdown."""
    try:
        req = urllib.request.Request(
            shutdown_url,
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def check_server_running(url: str = HEALTH_URL) -> bool:
    """Comprueba si un servidor backend compatible y propio responde en la URL de health."""
    identity = verify_backend_identity(url)
    return is_backend_compatible(identity)


def stop_server():
    """Detiene el proceso hijo del servidor backend registrado de forma idempotente."""
    global _SERVER_PROCESS, _IS_STOPPING, _CURRENT_BACKEND_PORT
    with _STOPPING_LOCK:
        if _IS_STOPPING:
            return
        _IS_STOPPING = True

    proc = _SERVER_PROCESS
    _SERVER_PROCESS = None

    if proc is None:
        return

    _safe_print("🛑 Deteniendo backend dedicado de CodeAgent Desktop...")

    port = _CURRENT_BACKEND_PORT
    if port > 0:
        shutdown_url = f"http://localhost:{port}/api/server/shutdown"
        try:
            req = urllib.request.Request(
                shutdown_url,
                data=b"{}",
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=1):
                pass
        except Exception:
            pass

    try:
        proc.wait(timeout=2)
    except Exception:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except Exception:
            with contextlib.suppress(Exception):
                proc.kill()
                proc.wait(timeout=1)


atexit.register(stop_server)


def launch_server_bg(target_port: int = 0) -> bool:
    global _SERVER_PROCESS, _CURRENT_BACKEND_PORT, _EXPECTED_INSTANCE_ID, _IS_STOPPING
    _IS_STOPPING = False

    if target_port <= 0:
        port = find_free_port()
    else:
        port = target_port

    _CURRENT_BACKEND_PORT = port
    import uuid
    _EXPECTED_INSTANCE_ID = str(uuid.uuid4())

    _safe_print(f"🚀 Iniciando Servidor Proxy Backend dedicado en puerto {port}...")

    server_script = os.path.join(BASE_DIR, "mis_agentes_inteligentes", "localcode_server.py")
    python_exe = sys.executable
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    env = os.environ.copy()
    sub_module = os.path.join(BASE_DIR, "mis_agentes_inteligentes")
    env["PYTHONPATH"] = os.pathsep.join([BASE_DIR, sub_module, env.get("PYTHONPATH", "")])
    env["PYTHONIOENCODING"] = "utf-8"
    env["NO_BROWSER"] = "1"
    env["CODEAGENT_PORT"] = str(port)
    env["CODEAGENT_INSTANCE_ID"] = _EXPECTED_INSTANCE_ID
    env["CODEAGENT_PARENT_PID"] = str(os.getpid())
    env["CODEAGENT_PARENT_CREATION_TIME"] = str(get_process_creation_time(os.getpid()))

    _SERVER_PROCESS = subprocess.Popen(
        [python_exe, server_script, "--port", str(port)],
        cwd=BASE_DIR,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
    )

    health_url = f"http://localhost:{port}/api/health"

    for i in range(20):
        time.sleep(0.5)
        ident = verify_backend_identity(health_url)
        if ident and is_backend_compatible(ident):
            _safe_print(f"✅ Backend dedicado de CodeAgent listo en http://localhost:{port} (PID {ident.get('process_id')})")
            return True
        if i % 4 == 0:
            _safe_print(f"⏳ Esperando arranque del backend en puerto {port}...")

    _safe_print(f"⚠️ Advertencia: El servidor backend en puerto {port} tardó más de lo esperado.")
    return False


CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if os.name == "nt" else 0

def _ps_file_dialog(title: str = "Abrir Archivo") -> str | None:
    ps_cmd = f"[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null; $f = New-Object System.Windows.Forms.OpenFileDialog; $f.Title = '{title}'; $f.Filter = 'Todos los archivos (*.*)|*.*'; if($f.ShowDialog() -eq 'OK'){{ $f.FileName }}"
    try:
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=60, creationflags=CREATE_NO_WINDOW)
        path = res.stdout.strip()
        return path if path and os.path.exists(path) else None
    except Exception as e:
        print(f"Error en _ps_file_dialog: {e}")
        return None

def _ps_folder_dialog(title: str = "Abrir Carpeta de Proyecto") -> str | None:
    ps_cmd = f"[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null; $f = New-Object System.Windows.Forms.FolderBrowserDialog; $f.Description = '{title}'; if($f.ShowDialog() -eq 'OK'){{ $f.SelectedPath }}"
    try:
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=60, creationflags=CREATE_NO_WINDOW)
        path = res.stdout.strip()
        return path if path and os.path.exists(path) else None
    except Exception as e:
        print(f"Error en _ps_folder_dialog: {e}")
        return None

def _ps_save_dialog(title: str = "Guardar Archivo Como", default_filename: str = "Untitled.py") -> str | None:
    ps_cmd = f"[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null; $f = New-Object System.Windows.Forms.SaveFileDialog; $f.Title = '{title}'; $f.FileName = '{default_filename}'; if($f.ShowDialog() -eq 'OK'){{ $f.FileName }}"
    try:
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=60, creationflags=CREATE_NO_WINDOW)
        path = res.stdout.strip()
        return path if path else None
    except Exception as e:
        print(f"Error en _ps_save_dialog: {e}")
        return None

class DesktopIDEApi:
    """API nativa expuesta al frontend de Javascript a través de PyWebView."""

    def __init__(self):
        pass

    def open_file_dialog(self) -> dict[str, str] | None:
        """Abre el diálogo nativo del SO para seleccionar un archivo y devuelve su ruta y contenido."""
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now_str}] [NATIVE_UI] open_file_dialog CALLED")
        filepath = _ps_file_dialog("Abrir Archivo — CodeAgent IDE")
        if filepath and os.path.exists(filepath):
            try:
                with open(filepath, encoding="utf-8", errors="replace") as f:
                    content = f.read(200000)
                return {
                    "path": filepath,
                    "filename": os.path.basename(filepath),
                    "content": content
                }
            except Exception as e:
                print(f"Error leyendo archivo en open_file_dialog: {e}")
        return None

    def open_folder_dialog(self) -> dict[str, str] | None:
        """Abre el diálogo nativo del SO para seleccionar una carpeta y cambiar el workspace."""
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now_str}] [NATIVE_UI] open_folder_dialog CALLED")
        folderpath = _ps_folder_dialog("Abrir Carpeta de Proyecto — CodeAgent IDE")
        if folderpath and os.path.exists(folderpath):
            try:
                from mis_agentes_inteligentes.tools import set_active_workspace
                set_active_workspace(folderpath)
                return {
                    "path": folderpath,
                    "folder_name": os.path.basename(folderpath)
                }
            except Exception as e:
                print(f"Error ajustando workspace en open_folder_dialog: {e}")
        return None

    def save_file_dialog(self, content: str = "", default_filename: str = "Untitled.py") -> dict[str, str] | None:
        """Abre el diálogo nativo de Guardar Como para escribir contenido en disco."""
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now_str}] [NATIVE_UI] save_file_dialog CALLED (default: {default_filename})")
        filepath = _ps_save_dialog("Guardar Archivo Como — CodeAgent IDE", default_filename)
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                return {
                    "path": filepath,
                    "filename": os.path.basename(filepath)
                }
            except Exception as e:
                print(f"Error en save_file_dialog: {e}")
        return None

    def write_file(self, path: str, content: str) -> bool:
        """Guarda directamente el contenido del buffer en una ruta existente."""
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now_str}] [AUTOSAVE] write_file CALLED for path={path}")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error escribiendo archivo {path}: {e}")
            return False

    def new_window(self) -> bool:
        """Inicia una nueva ventana de la aplicación de escritorio (DESACTIVADA POR POLÍTICA DE INSTANCIA ÚNICA)."""
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now_str}] [NATIVE_UI] new_window CALLED (BLOCKED by single-instance policy)")
        return False

    def exit_app(self) -> None:
        """Finaliza el proceso de la ventana y la aplicación."""
        stop_server()
        with contextlib.suppress(Exception):
            sys.exit(0)


def main():
    global SERVER_URL, HEALTH_URL, SHUTDOWN_URL
    _safe_print("===================================================")
    _safe_print("💻 Lanzando CodeAgent Desktop IDE All-In-One v5.0")
    _safe_print("===================================================\n")

    # 1. Auto-iniciar Ollama si no está activo
    if not check_ollama_running():
        launch_ollama_bg()
    else:
        _safe_print("✅ Servidor Ollama ya está activo en http://localhost:11434")

    # 2. Auto-iniciar Backend de CodeAgent dedicado
    if not launch_server_bg():
        _safe_print("❌ Error: No se pudo iniciar el backend dedicado de CodeAgent.")
        sys.exit(1)

    port = _CURRENT_BACKEND_PORT
    SERVER_URL = f"http://localhost:{port}/localcode_claude_ui.html"
    HEALTH_URL = f"http://localhost:{port}/api/health"
    SHUTDOWN_URL = f"http://localhost:{port}/api/server/shutdown"

    # 3. Lanzar Ventana de Aplicación de Escritorio
    if os.environ.get("NO_BROWSER") == "1":
        _safe_print("🤖 Modo Headless / NO_BROWSER activo. Manteniendo proceso Desktop...")
        try:
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            stop_server()
        return

    try:
        import webview
        _safe_print("📱 Abriendo CodeAgent en Ventana Nativa de Escritorio...")
        api_instance = DesktopIDEApi()
        window = webview.create_window(
            title="CodeAgent Desktop IDE v5.0 - Professional Agentic Workspace",
            url=SERVER_URL,
            js_api=api_instance,
            width=1440,
            height=900,
            resizable=True
        )
        window.events.closed += stop_server
        webview.start()
        return
    except ImportError:
        pass

    # Fallback: Modo App de Chrome/Edge
    _safe_print("🌐 Lanzando CodeAgent en Modo App de Escritorio...")
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]

    browser_exe = next((p for p in chrome_paths if os.path.exists(p)), None)
    if browser_exe:
        subprocess.Popen([browser_exe, f"--app={SERVER_URL}"])
    else:
        import webbrowser
        webbrowser.open(SERVER_URL)


if __name__ == "__main__":
    main()
