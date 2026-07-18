"""
Pipeline de agentes con smolagents de HuggingFace.
El LLM usa CodeAgent para generar código Python y llamar herramientas.
Compatible de forma nativa y robusta con modelos locales de 7B (como Qwen-Coder).
"""
import os
import time

import tools as mis_herramientas
from agents import crear_agente, get_model, route_prompt

# ─────────────────────────────────────────────────────────────────────────────
# MAPEO DE HERRAMIENTAS
# ─────────────────────────────────────────────────────────────────────────────
TOOLS_MAP = {
    "Base de Datos (Eventos)": mis_herramientas.consultar_db,
    "Github": [
        mis_herramientas.consultar_github,
        mis_herramientas.leer_repositorio_github,
        mis_herramientas.leer_archivo_github,
    ],
    "Archivos Locales": [
        mis_herramientas.listar_directorio_local,
        mis_herramientas.leer_archivo_local,
        mis_herramientas.escribir_archivo_local,
        mis_herramientas.editar_archivo_search_replace,
    ],
    "Terminal Integrada": mis_herramientas.ejecutar_comando_terminal,
    "Búsqueda Web": mis_herramientas.buscar_en_internet,
    "Git": [
        mis_herramientas.git_status,
        mis_herramientas.git_diff,
        mis_herramientas.git_add,
        mis_herramientas.git_commit,
        mis_herramientas.git_push,
    ],
}


def get_herramientas(nombres_seleccionados: list) -> list:
    """Convierte los nombres del UI en la lista de funciones @tool."""
    herramientas_activas = []
    for nombre in nombres_seleccionados:
        if nombre in TOOLS_MAP:
            tools = TOOLS_MAP[nombre]
            if isinstance(tools, list):
                herramientas_activas.extend(tools)
            else:
                herramientas_activas.append(tools)

    # Siempre añadir la herramienta de memoria base
    herramientas_activas.append(mis_herramientas.guardar_reporte)
    return herramientas_activas


def _construir_contexto_workspace() -> str:
    """
    Genera un bloque de contexto del workspace actual para inyectar en el system_prompt.
    Informa al agente en qué directorio está y qué estructura de proyecto tiene.
    """
    cwd = os.getcwd()
    contexto = "## Contexto del Workspace\n"
    contexto += f"- **Directorio de trabajo actual:** `{cwd}`\n"

    try:
        items = os.listdir(cwd)
        archivos_py = [f for f in items if f.endswith(".py")]
        carpetas = [f for f in items if os.path.isdir(os.path.join(cwd, f)) and not f.startswith(".")]
        contexto += f"- **Archivos Python en raíz:** {', '.join(archivos_py[:10]) or 'ninguno'}\n"
        contexto += f"- **Subcarpetas:** {', '.join(carpetas[:10]) or 'ninguna'}\n"
    except Exception:
        pass

    return contexto


# ─────────────────────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────
def ejecutar_agentes(
    user_prompt: str,
    provider: str,
    model_name: str,
    api_key: str,
    agent_type: str,
    selected_tools: list,
    _step_callback=None,
) -> tuple[str, dict]:
    """
    Pipeline principal usando smolagents.
    FIX: el historial ya no se manda como prompt — eso lo maneja app.py.
    NUEVO: acepta step_callback para streaming de pasos en la UI.
    """
    start_time = time.time()

    # ── Enrutador automático ─────────────────────────────────────────────────
    if agent_type == "Auto (Enrutador Automático) 🌟":
        agent_type = route_prompt(user_prompt)

    # ── Forzar herramientas según el agente si no se seleccionaron ───────────
    if not selected_tools:
        if agent_type in (
            "Agente de Edición de Código",
            "Arquitecto de Agentes Smolagents",
            "python-pro",
            "frontend-developer",
            "code-reviewer",
            "security-auditor",
        ):
            selected_tools = ["Archivos Locales", "Terminal Integrada", "Git"]
        elif agent_type == "Analista de Código (Experto Github)" \
                or "ghp_" in user_prompt \
                or "github.com/" in user_prompt:
            selected_tools = ["Github"]
            agent_type = "Analista de Código (Experto Github)"

    # ── Configurar modelo y herramientas ─────────────────────────────────────
    model = get_model(provider, model_name, api_key)
    herramientas = get_herramientas(selected_tools)

    metricas = {
        "tiempo_segundos": 0,
        "agentes_usados": f"CodeAgent ({agent_type})",
        "herramientas_activas": len(herramientas),
        "proveedor": provider,
        "modelo": model_name,
    }

    # ── Contexto de workspace dinámico ───────────────────────────────────────
    workspace_context = _construir_contexto_workspace()

    # ── Modo Conversación: sin herramientas ──────────────────────────────────
    if not herramientas or agent_type == "Asistente General":
        agente = crear_agente(agent_type, model, [], workspace_context)
        resultado = agente.run(user_prompt)
        metricas["tiempo_segundos"] = round(time.time() - start_time, 2)
        return str(resultado), metricas

    # ── Ejecutar CodeAgent ───────────────────────────────────────────────────
    try:
        agente = crear_agente(agent_type, model, herramientas, workspace_context)
        resultado = agente.run(user_prompt)
        resultado_str = str(resultado)
    except Exception as e:
        import traceback
        resultado_str = (
            f"❌ Error en la ejecución del agente:\n```\n{e}\n```\n\n"
            f"**Traza completa:**\n```\n{traceback.format_exc()[-1500:]}\n```"
        )

    metricas["tiempo_segundos"] = round(time.time() - start_time, 2)
    return resultado_str, metricas
