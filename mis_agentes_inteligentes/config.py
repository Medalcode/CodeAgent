"""
Módulo de Configuración Centralizado para CodeAgent
Define variables de entorno, puertos y parámetros del sistema con fallbacks seguros.
"""
import os

# Contexto de LLM y Ollama
OLLAMA_NUM_CTX = int(os.environ.get("OLLAMA_NUM_CTX", "8192"))
OLLAMA_TARGET = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")

# Red y Servidor HTTP
SERVER_PORT = int(os.environ.get("PORT", "8000"))

# Seguridad y Sandboxing de Terminal
STRICT_SANDBOX = os.environ.get("STRICT_SANDBOX", "0") == "1"
ALLOWED_COMMANDS = {
    "git", "dir", "ls", "pytest", "python", "python3",
    "cat", "type", "echo", "pwd", "cd", "which", "where",
    "ruff", "uv", "node", "npm"
}

# Timeouts de API Externa
GITHUB_API_TIMEOUT = int(os.environ.get("GITHUB_API_TIMEOUT", "15"))
