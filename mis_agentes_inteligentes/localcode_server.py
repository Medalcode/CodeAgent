#!/usr/bin/env python3
"""
LocalCode Proxy Server & Static Host
Servidor local en Python (0 dependencias externas) que sirve localcode_claude_ui.html
y actúa como proxy transparente hacia Ollama (http://localhost:11434),
eliminando por completo los errores de CORS / NetworkError en el navegador.
"""
import http.server
import os
import socketserver
import urllib.request
import webbrowser

PORT = 8000
OLLAMA_TARGET = "http://localhost:11434"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
        if self.path.startswith("/api/"):
            self.proxy_to_ollama("GET")
        else:
            if self.path in ("/", ""):
                self.path = "/localcode_claude_ui.html"
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            self.proxy_to_ollama("POST")
        else:
            super().do_POST()

    def proxy_to_ollama(self, method):
        target_url = f"{OLLAMA_TARGET}{self.path}"
        headers = {k: v for k, v in self.headers.items() if k.lower() not in ("host", "content-length")}

        body = None
        if method == "POST":
            content_len = int(self.headers.get("Content-Length", 0))
            if content_len > 0:
                body = self.rfile.read(content_len)

        req = urllib.request.Request(target_url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req) as resp:
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
        except Exception as e:
            self.send_response(502)
            self.end_headers()
            err_msg = f'{{"error": "No se pudo conectar a Ollama en {OLLAMA_TARGET}. Verifica que Ollama esté ejecutándose. Detalle: {e}"}}'
            self.wfile.write(err_msg.encode("utf-8"))


def main():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), LocalCodeProxyHandler) as httpd:
        url = f"http://localhost:{PORT}/localcode_claude_ui.html"
        print("=" * 65)
        print(f"🚀 Servidor LocalCode iniciado en: {url}")
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
