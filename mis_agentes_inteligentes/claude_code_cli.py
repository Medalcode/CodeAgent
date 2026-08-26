#!/usr/bin/env python3
"""
Claude Code Local CLI (OpenCode)
Interfaz de terminal para interactuar con agentes locales estilo Claude Code
conectados a modelos Ollama (qwen2.5-coder, deepseek-coder) o proveedores Cloud.
"""
import os
import sys

# Asegurar importación de módulos locales
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import ejecutar_agentes

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

# Intento de formato enriquecido de consola con rich
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    console = Console()
    HAS_RICH = True
except ImportError:
    console = None
    HAS_RICH = False


def print_banner():
    title = "💻 Claude Code Local (OpenCode CLI)"
    sub = "Conectado a Ollama (Qwen 2.5 Coder / DeepSeek Coder) y smolagents"
    if HAS_RICH:
        console.print(Panel.fit(f"[bold cyan]{title}[/bold cyan]\n[dim]{sub}[/dim]", border_style="cyan"))
    else:
        print("=" * 60)
        print(title)
        print(sub)
        print("=" * 60)


def main():
    print_banner()

    provider = os.getenv("DEFAULT_PROVIDER", "Ollama (Local)")
    model_name = os.getenv("DEFAULT_MODEL", "qwen2.5-coder:7b")
    api_key = os.getenv("OPENAI_API_KEY", "")
    agent_type = "Claude Code (Local OpenCode)"
    selected_tools = ["Archivos Locales", "Terminal Integrada", "Git"]

    print(f"🤖 Agente activo: {agent_type}")
    print(f"🧠 Modelo: {provider} / {model_name}")
    print(f"🛠️ Herramientas: {', '.join(selected_tools)}")
    print("💡 Escribe '/help' para ver comandos, '/exit' para salir.\n")

    while True:
        try:
            prompt = input("\n\033[1;32mclaude-local>\033[0m ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 ¡Hasta luego!")
            break

        if not prompt:
            continue

        cmd = prompt.lower()
        if cmd in ("/exit", "/quit"):
            print("👋 Cerrando sesión de Claude Code Local...")
            break
        elif cmd == "/help":
            help_text = (
                "**Comandos disponibles en Claude Code CLI:**\n"
                "- `/help` — Muestra esta ayuda\n"
                "- `/status` — Muestra la configuración del modelo y herramientas\n"
                "- `/model <nombre>` — Cambia el modelo (ej. /model deepseek-coder:6.7b)\n"
                "- `/explore` — Explora la estructura del proyecto actual\n"
                "- `/test` — Ejecuta la suite de pruebas unitarias del proyecto\n"
                "- `/diff` — Muestra los cambios no commiteados de Git\n"
                "- `/clear` — Limpia la consola\n"
                "- `/exit` — Sale del CLI\n"
            )
            if HAS_RICH:
                console.print(Markdown(help_text))
            else:
                print(help_text)
            continue
        elif cmd == "/clear":
            os.system('cls' if os.name == 'nt' else 'clear')
            print_banner()
            continue
        elif cmd == "/status":
            print(f"📍 Directorio: {os.getcwd()}")
            print(f"🤖 Agente: {agent_type}")
            print(f"🧠 Proveedor: {provider} | Modelo: {model_name}")
            print(f"🛠️ Herramientas: {', '.join(selected_tools)}")
            continue
        elif cmd.startswith("/model "):
            model_name = prompt.split(" ", 1)[1].strip()
            print(f"✅ Modelo actualizado a: {model_name}")
            continue
        elif cmd == "/explore":
            prompt = "@workspace Explora la estructura de archivos y tecnologías del proyecto actual."
        elif cmd == "/test":
            prompt = "Ejecuta los tests unitarios del proyecto usando ejecutar_comando_terminal y reporta los resultados."
        elif cmd == "/diff":
            prompt = "Muestra el estado de git status y git diff de los archivos modificados."

        if HAS_RICH:
            console.print(f"[dim]🧠 Pensando con {model_name}...[/dim]")
        else:
            print(f"🧠 Pensando con {model_name}...")

        respuesta, metricas = ejecutar_agentes(
            user_prompt=prompt,
            provider=provider,
            model_name=model_name,
            api_key=api_key,
            agent_type=agent_type,
            selected_tools=selected_tools,
        )

        if HAS_RICH:
            console.print(Markdown(f"\n{respuesta}\n"))
            console.print(f"[dim]⏱️ Tiempo: {metricas.get('tiempo_segundos', 0)}s | Herramientas: {metricas.get('herramientas_activas', 0)}[/dim]")
        else:
            print(f"\n{respuesta}\n")
            print(f"⏱️ Tiempo: {metricas.get('tiempo_segundos', 0)}s")


if __name__ == "__main__":
    main()
