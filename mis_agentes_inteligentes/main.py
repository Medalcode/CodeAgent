"""
Pipeline de agentes con smolagents de HuggingFace.
El LLM usa CodeAgent para generar código Python y llamar herramientas.
Compatible de forma nativa y robusta con modelos locales de 7B (como Qwen-Coder).
"""
import time
from agents import get_model, route_prompt, crear_agente
import tools as mis_herramientas

# ─────────────────────────────────────────────────────────────────────────────
# MAPEO DE HERRAMIENTAS
# ─────────────────────────────────────────────────────────────────────────────
TOOLS_MAP = {
    "Base de Datos (Eventos)": mis_herramientas.consultar_db,
    "Github": [mis_herramientas.consultar_github, mis_herramientas.leer_repositorio_github, mis_herramientas.leer_archivo_github],
    "Archivos Locales": [mis_herramientas.listar_directorio_local, mis_herramientas.leer_archivo_local, mis_herramientas.escribir_archivo_local, mis_herramientas.editar_archivo_search_replace],
    "Terminal Integrada": mis_herramientas.ejecutar_comando_terminal,
    "Búsqueda Web": mis_herramientas.buscar_en_internet,
    "Git": [mis_herramientas.git_status, mis_herramientas.git_diff, mis_herramientas.git_add, mis_herramientas.git_commit, mis_herramientas.git_push]
}

def get_herramientas(nombres_seleccionados):
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

# ─────────────────────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────
def ejecutar_agentes(user_prompt: str, provider: str, model_name: str, api_key: str,
                     agent_type: str, selected_tools: list) -> tuple[str, dict]:
    """
    Pipeline principal usando smolagents.
    """
    start_time = time.time()
    
    # ── Enrutador automático ─────────────────────────────────────────────────
    if agent_type == "Auto (Enrutador Automático) 🌟":
        agent_type = route_prompt(user_prompt)

    # ── Forzar herramientas según el agente y prompt ─────────────────────────
    if not selected_tools:
        if agent_type in ("Ingeniero de Software Local", "python-pro", "frontend-developer", "code-reviewer", "security-auditor"):
            selected_tools = ["Archivos Locales", "Terminal Integrada", "Git"]
        elif agent_type == "Analista de Código (Experto Github)" or "ghp_" in user_prompt or "github.com/" in user_prompt:
            selected_tools = ["Github"]
            agent_type = "Analista de Código (Experto Github)"

    # ── Configurar modelo y herramientas ─────────────────────────────────────
    model = get_model(provider, model_name, api_key)
    herramientas = get_herramientas(selected_tools)

    metricas = {
        "tiempo_segundos": 0,
        "agentes_usados": f"CodeAgent ({agent_type})",
        "herramientas_activas": len(herramientas)
    }

    # ── Modo Conversación: sin herramientas ──────────────────────────────────
    if not herramientas or agent_type == "Asistente General":
        agente = crear_agente(agent_type, model, [])
        resultado = agente.run(user_prompt)
        metricas["tiempo_segundos"] = round(time.time() - start_time, 2)
        return str(resultado), metricas

    # ── Ejecutar CodeAgent ───────────────────────────────────────────────────
    try:
        agente = crear_agente(agent_type, model, herramientas)
        resultado = agente.run(user_prompt)
        resultado_str = str(resultado)
    except Exception as e:
        resultado_str = f"❌ Ocurrió un error en la ejecución del agente:\n{e}"

    metricas["tiempo_segundos"] = round(time.time() - start_time, 2)
    return resultado_str, metricas
