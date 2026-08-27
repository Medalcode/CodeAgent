"""
CodeAgent Desktop Runner (v3.5)
Lanza CodeAgent en una ventana nativa de escritorio independiente usando PyWebView o WebView2 nativo de Windows.
"""
import os
import subprocess
import sys
import time
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_URL = "http://localhost:8000/localcode_claude_ui.html"


def check_server_running(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def launch_server_bg():
    server_script = os.path.join(BASE_DIR, "mis_agentes_inteligentes", "localcode_server.py")
    python_exe = sys.executable
    subprocess.Popen([python_exe, server_script], cwd=BASE_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)


def main():
    if not check_server_running(SERVER_URL):
        print("🚀 Iniciando Servidor Backend de CodeAgent...")
        launch_server_bg()

    # Intentar importar pywebview para ventana nativa sin navegador
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

    # Fallback: Lanzar Chrome o Edge en modo Aplicación de Escritorio (--app)
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
