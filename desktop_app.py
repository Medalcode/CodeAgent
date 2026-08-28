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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_URL = "http://localhost:8000/localcode_claude_ui.html"
OLLAMA_API_URL = "http://localhost:11434/api/tags"


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
    print("🦙 Auto-iniciando Servidor Ollama (Local LLM)...")
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
                print("✅ Servicio Ollama listo en http://localhost:11434")
                return True
            print(f"⏳ Esperando arranque de Ollama ({i+1}/12s)...")
    except Exception as e:
        print(f"⚠️ Advertencia: No se pudo auto-iniciar Ollama automáticamente: {e}")
    return False


def check_server_running(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def launch_server_bg():
    print("🚀 Iniciando Servidor Proxy Backend CodeAgent...")
    server_script = os.path.join(BASE_DIR, "mis_agentes_inteligentes", "localcode_server.py")
    python_exe = sys.executable
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    env = os.environ.copy()
    sub_module = os.path.join(BASE_DIR, "mis_agentes_inteligentes")
    env["PYTHONPATH"] = os.pathsep.join([BASE_DIR, sub_module, env.get("PYTHONPATH", "")])
    env["PYTHONIOENCODING"] = "utf-8"
    env["NO_BROWSER"] = "1"

    subprocess.Popen(
        [python_exe, server_script],
        cwd=BASE_DIR,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
    )
    for i in range(20):
        time.sleep(0.5)
        if check_server_running(SERVER_URL):
            print("✅ Servidor Backend de CodeAgent listo en http://localhost:8000")
            return True
        if i % 4 == 0:
            print("⏳ Esperando arranque del backend (puerto 8000)...")

    print("⚠️ Advertencia: El servidor backend tardó más de lo esperado en responder.")
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
                from tools import set_active_workspace
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
        with contextlib.suppress(Exception):
            sys.exit(0)


def main():
    print("===================================================")
    print("💻 Lanzando CodeAgent Desktop IDE All-In-One v5.0")
    print("===================================================\n")

    # 1. Auto-iniciar Ollama si no está activo
    if not check_ollama_running():
        launch_ollama_bg()
    else:
        print("✅ Servidor Ollama ya está activo en http://localhost:11434")

    # 2. Auto-iniciar Backend de CodeAgent si no está activo
    if not check_server_running(SERVER_URL):
        launch_server_bg()
    else:
        print("✅ Servidor Backend CodeAgent ya está activo en http://localhost:8000")

    # 3. Lanzar Ventana de Aplicación de Escritorio
    try:
        import webview
        print("📱 Abriendo CodeAgent en Ventana Nativa de Escritorio...")
        api_instance = DesktopIDEApi()
        webview.create_window(
            title="CodeAgent Desktop IDE v5.0 - Professional Agentic Workspace",
            url=SERVER_URL,
            js_api=api_instance,
            width=1440,
            height=900,
            resizable=True
        )
        webview.start()
        return
    except ImportError:
        pass

    # Fallback: Modo App de Chrome/Edge
    print("🌐 Lanzando CodeAgent en Modo App de Escritorio...")
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
