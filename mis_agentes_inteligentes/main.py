"""
Pipeline de agentes con smolagents de HuggingFace.
El LLM usa CodeAgent para generar código Python y llamar herramientas.
Compatible de forma nativa y robusta con modelos locales de 7B (como Qwen-Coder).
"""
import time
import traceback

import rag_tools
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
    "Memoria RAG": [
        rag_tools.indexar_directorio_local,
        rag_tools.preguntar_a_repositorio,
    ],
}


def get_herramientas(nombres_seleccionados: list) -> list:
    """Convierte los nombres del UI en la lista de funciones @tool."""
    herramientas_activas = []
    for nombre in nombres_seleccionados:
        if nombre in TOOLS_MAP:
            tools = TOOLS_MAP[nombre]
            if isinstance(tools, list):
                for t in tools:
                    if t not in herramientas_activas:
                        herramientas_activas.append(t)
            else:
                if tools not in herramientas_activas:
                    herramientas_activas.append(tools)

    # Siempre añadir la herramienta de memoria base si no está presente
    if mis_herramientas.guardar_reporte not in herramientas_activas:
        herramientas_activas.append(mis_herramientas.guardar_reporte)
    return herramientas_activas



def _construir_contexto_workspace() -> str:
    """
    Genera un bloque de contexto del workspace actual para inyectar en el system_prompt.
    Reutiliza la implementación centralizada de tools.py (DRY).
    """
    return mis_herramientas.obtener_contexto_workspace()


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
            "CodeAgent Developer",
            "Agente de Edición de Código",
            "Arquitecto de Agentes Smolagents",
            "python-pro",
            "frontend-developer",
            "code-reviewer",
            "security-auditor",
        ):
            selected_tools = ["Archivos Locales", "Terminal Integrada", "Git", "Github"]
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

    # ── Ejecutar CodeAgent v3.0 con AgentPipeline ─────────────────────────────
    try:
        agente = crear_agente(agent_type, model, herramientas, workspace_context)

        def _runner(prompt_enriquecido):
            if _step_callback is not None:
                res_last = None
                for step in agente.run(prompt_enriquecido, stream=True):
                    if callable(_step_callback):
                        _step_callback(step)
                    res_last = step
                return str(res_last) if res_last is not None else str(agente.run(prompt_enriquecido))
            else:
                return str(agente.run(prompt_enriquecido))

        try:
            from agent_pipeline import AgentPipeline
            pipeline = AgentPipeline()
            resultado_str, p_metrics = pipeline.run_pipeline(user_prompt, agent_runner=_runner)
            metricas.update(p_metrics)
        except Exception:
            resultado_str = _runner(user_prompt)

    except Exception as e:
        resultado_str = (
            f"❌ Error en la ejecución del agente:\n```\n{e}\n```\n\n"
            f"**Traza completa:**\n```\n{traceback.format_exc()[-1500:]}\n```"
        )

    metricas["tiempo_segundos"] = round(time.time() - start_time, 2)
    return resultado_str, metricas
