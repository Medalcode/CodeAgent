"""
CodeAgent Desktop Runner (v3.5)
Lanza CodeAgent y Ollama automáticamente en una ventana nativa de escritorio independiente.
"""
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
    subprocess.Popen(
        [python_exe, server_script],
        cwd=BASE_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
    )
    for _ in range(10):
        time.sleep(0.5)
        if check_server_running(SERVER_URL):
            print("✅ Servidor Backend de CodeAgent listo.")
            return True


def main():
    print("===================================================")
    print("💻 Lanzando CodeAgent Desktop IDE All-In-One v3.5")
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
        webview.create_window(
            title="CodeAgent Desktop IDE v3.5 - Autonomous Agentic Platform",
            url=SERVER_URL,
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
