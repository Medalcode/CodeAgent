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


class DesktopIDEApi:
    """API nativa expuesta al frontend de Javascript a través de PyWebView."""

    def __init__(self):
        pass

    def open_file_dialog(self) -> dict[str, str] | None:
        """Abre el diálogo nativo del SO para seleccionar un archivo y devuelve su ruta y contenido."""
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            filepath = filedialog.askopenfilename(title="Abrir Archivo — CodeAgent IDE")
            root.destroy()

            if filepath and os.path.exists(filepath):
                with open(filepath, encoding="utf-8", errors="replace") as f:
                    content = f.read(200000)
                return {
                    "path": filepath,
                    "filename": os.path.basename(filepath),
                    "content": content
                }
        except Exception as e:
            print(f"Error en open_file_dialog: {e}")
        return None

    def open_folder_dialog(self) -> dict[str, str] | None:
        """Abre el diálogo nativo del SO para seleccionar una carpeta y cambiar el workspace."""
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            folderpath = filedialog.askdirectory(title="Abrir Carpeta de Proyecto — CodeAgent IDE")
            root.destroy()

            if folderpath and os.path.exists(folderpath):
                from tools import set_active_workspace
                set_active_workspace(folderpath)
                return {
                    "path": folderpath,
                    "folder_name": os.path.basename(folderpath)
                }
        except Exception as e:
            print(f"Error en open_folder_dialog: {e}")
        return None

    def save_file_dialog(self, content: str = "", default_filename: str = "Untitled.py") -> dict[str, str] | None:
        """Abre el diálogo nativo de Guardar Como para escribir contenido en disco."""
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            filepath = filedialog.asksaveasfilename(
                title="Guardar Archivo Como — CodeAgent IDE",
                initialfile=default_filename
            )
            root.destroy()

            if filepath:
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
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error escribiendo archivo {path}: {e}")
            return False

    def new_window(self) -> bool:
        """Inicia una nueva ventana de la aplicación de escritorio."""
        try:
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            subprocess.Popen([sys.executable, __file__], cwd=BASE_DIR, creationflags=creationflags)
            return True
        except Exception as e:
            print(f"Error abriendo nueva ventana: {e}")
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
