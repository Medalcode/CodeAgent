from crewai import Task, Crew, Process
from agents import get_llm, create_agent, route_prompt
import tools as mis_herramientas
import re
import time

# ─────────────────────────────────────────────────────────────────────────────
# MODO DIRECTO: ejecuta herramientas en Python y pasa resultados al LLM
# Bypasea CrewAI por completo — no depende de que el modelo formatee tool calls
# ─────────────────────────────────────────────────────────────────────────────
def ejecutar_modo_directo_github(user_prompt: str, llm) -> tuple[str, dict]:
    """Extrae el token y el repo del prompt, llama las herramientas directamente y pide análisis al LLM."""
    import time
    start = time.time()

    # Extraer token ghp_ del prompt
    token_match = re.search(r'ghp_[A-Za-z0-9]+', user_prompt)
    token = token_match.group(0) if token_match else ""

    if not token:
        return "No se encontró un token de GitHub válido (debe empezar por ghp_) en el mensaje.", {}

    # ── Paso 1: listar repositorios del usuario ──────────────────────────────
    repos_raw = mis_herramientas.consultar_github.run(token)

    # Intentar identificar el repo solicitado
    repo_solicitado = None
    prompt_lower = user_prompt.lower()
    # Buscar nombre de repo mencionado en el prompt
    for linea in repos_raw.splitlines():
        match = re.search(r'Nombre completo: ([^\|]+)', linea)
        if match:
            full_name = match.group(1).strip()
            repo_name = full_name.split("/")[-1].lower()
            if repo_name in prompt_lower or repo_name.replace("-", "") in prompt_lower.replace("-", ""):
                repo_solicitado = full_name
                break

    # ── Paso 2: leer el repo identificado ───────────────────────────────────
    repo_contenido = ""
    if repo_solicitado:
        repo_contenido = mis_herramientas.leer_repositorio_github.run(
            f'{{"token": "{token}", "nombres_repos": "{repo_solicitado}"}}'
        )
    else:
        repo_contenido = f"Repositorios disponibles:\n{repos_raw}\n\nNo se identificó un repositorio específico en el mensaje. Por favor especifica el nombre exacto."

    # ── Paso 3: pedir análisis al LLM con los datos reales ──────────────────
    system_msg = """Eres un experto en revisión de código y análisis de repositorios GitHub.
Se te proporcionará la estructura y el README de un repositorio. Tu trabajo es:
1. Analizar la calidad del proyecto (estructura, tecnologías, documentación)
2. Identificar fortalezas
3. Identificar debilidades y riesgos
4. Proponer mejoras concretas y accionables
Sé específico, técnico y útil. Responde en español."""

    user_msg = f"""El usuario solicitó: "{user_prompt}"

Datos reales del repositorio obtenidos de la API de GitHub:
{repo_contenido}

Por favor realiza un análisis completo y detallado."""

    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        response = llm.invoke([SystemMessage(content=system_msg), HumanMessage(content=user_msg)])
        resultado = response.content if hasattr(response, 'content') else str(response)
    except Exception:
        # Fallback si el LLM no acepta mensajes estructurados
        response = llm.invoke(f"{system_msg}\n\n{user_msg}")
        resultado = response.content if hasattr(response, 'content') else str(response)

    elapsed = round(time.time() - start, 2)
    metricas = {
        "tiempo_segundos": elapsed,
        "agentes_usados": "Modo Directo (GitHub)",
        "herramientas_activas": 2
    }
    return resultado, metricas


# ─────────────────────────────────────────────────────────────────────────────
# MODO CREWAI: para tareas locales (archivos, código, git, terminal)
# ─────────────────────────────────────────────────────────────────────────────
def ejecutar_agentes(user_prompt: str, provider: str, model_name: str, api_key: str, agent_type: str, selected_tools: list) -> tuple[str, dict]:
    """Ejecuta el equipo de agentes basándose en la configuración dinámica seleccionada en la UI."""
    
    # 1. Inicializar el Modelo de Lenguaje
    llm = get_llm(provider, model_name, api_key)
    
    # 1.5 Enrutador Swarm (Clasificador de Intenciones) y Carga de Subagentes
    from agents import load_subagents_from_disk
    subagents = load_subagents_from_disk()
    
    if agent_type == "Auto (Enrutador Automático) 🌟":
        agent_type = route_prompt(user_prompt, llm)
        
        # Auto-asignar herramientas óptimas para agentes fijos
        selected_tools = ["Búsqueda Web", "Memoria RAG"]
        if agent_type == "Ingeniero de Software Local":
            selected_tools.extend(["Archivos Locales", "Terminal Integrada", "Git"])
        elif agent_type == "Analista de Código (Experto Github)":
            selected_tools.extend(["GitHub API"])
        elif agent_type == "Asistente de Eventos y Productividad":
            selected_tools.extend(["Base de Datos (SQLite)"])

    # ── MODO DIRECTO: si hay token de GitHub, bypass CrewAI ─────────────────
    if "ghp_" in user_prompt or (agent_type == "Analista de Código (Experto Github)" and "github.com" in user_prompt):
        return ejecutar_modo_directo_github(user_prompt, llm)

    # Si el agente seleccionado es un subagente dinámico, mapeamos sus herramientas
    if agent_type in subagents:
        agent_tools_str = subagents[agent_type]["metadata"].get("tools", "")
        agent_tools = [t.strip().lower() for t in agent_tools_str.split(",")]
        
        for t in agent_tools:
            if t in ["read", "write", "glob", "grep", "edit"]:
                if "Archivos Locales" not in selected_tools:
                    selected_tools.append("Archivos Locales")
            if t in ["bash"]:
                if "Terminal Integrada" not in selected_tools:
                    selected_tools.append("Terminal Integrada")
            if t in ["webfetch", "websearch"]:
                if "Búsqueda Web" not in selected_tools:
                    selected_tools.append("Búsqueda Web")
                    
    # Auto-activar GitHub si el usuario provee un link (sin token)
    if "github.com" in user_prompt:
        if "GitHub API" not in selected_tools:
            selected_tools.append("GitHub API")
            
    # 2. Cargar las herramientas seleccionadas
    herramientas_activas = []
    if "Base de Datos (SQLite)" in selected_tools:
        herramientas_activas.append(mis_herramientas.consultar_db)
        herramientas_activas.append(mis_herramientas.guardar_reporte)
    if "GitHub API" in selected_tools:
        herramientas_activas.append(mis_herramientas.consultar_github)
        herramientas_activas.append(mis_herramientas.leer_repositorio_github)
        herramientas_activas.append(mis_herramientas.leer_archivo_github)
    if "Archivos Locales" in selected_tools:
        herramientas_activas.append(mis_herramientas.listar_directorio_local)
        herramientas_activas.append(mis_herramientas.leer_archivo_local)
        herramientas_activas.append(mis_herramientas.escribir_archivo_local)
        herramientas_activas.append(mis_herramientas.editar_archivo_search_replace)
    if "Git" in selected_tools:
        herramientas_activas.append(mis_herramientas.git_status)
        herramientas_activas.append(mis_herramientas.git_diff)
        herramientas_activas.append(mis_herramientas.git_add)
        herramientas_activas.append(mis_herramientas.git_commit)
        herramientas_activas.append(mis_herramientas.git_push)
    if "Terminal Integrada" in selected_tools:
        herramientas_activas.append(mis_herramientas.ejecutar_comando_terminal)
    if "Búsqueda Web" in selected_tools:
        herramientas_activas.append(mis_herramientas.buscar_en_internet)
    if "Memoria RAG" in selected_tools:
        try:
            import rag_tools
            herramientas_activas.append(rag_tools.indexar_directorio_local)
            herramientas_activas.append(rag_tools.preguntar_a_repositorio)
        except ImportError:
            pass
        
    # 3. Crear agentes
    from agents import create_planner_agent
    agente_ejecutor = create_agent(agent_type, llm, herramientas_activas)
    agente_planner = create_planner_agent(llm)

    # 4. Asignar las tareas
    t_plan = Task(
        description=f'''Contexto y Petición:
{user_prompt}

INSTRUCCIÓN:
Genera un PLAN paso a paso detallado para resolver la petición del usuario.
El plan es para que OTRO Agente de IA lo ejecute usando herramientas del sistema (Terminal, Archivos, GitHub API, etc).
Estructura tu respuesta como un árbol de decisión claro:
Plan
├── Paso 1: [Acción detallada para el Agente Ejecutor]
├── Paso 2: [Acción detallada para el Agente Ejecutor]
└── Paso 3: [Acción detallada para el Agente Ejecutor]
''',
        expected_output='Un plan paso a paso en formato Markdown. NO le pidas al usuario que haga nada, el Agente Ejecutor lo hará.',
        agent=agente_planner
    )
    
    t_ejecucion = Task(
        description=f'''Contexto original:
{user_prompt}

INSTRUCCIÓN CRÍTICA:
Tu trabajo es EJECUTAR el plan elaborado por el Arquitecto.
TIENES HERRAMIENTAS REALES DISPONIBLES. ¡ÚSALAS!
NO le digas al usuario "Clona el repositorio" o "Navega al directorio". Hazlo tú mismo.
SIEMPRE ejecuta las acciones por ti mismo usando las tools provistas. NUNCA delegues el trabajo al usuario.
PIENSA PASO A PASO. NUNCA alucines.''',
        expected_output='Tu respuesta final debe ser el resultado real de haber ejecutado las tareas y usado las herramientas.',
        agent=agente_ejecutor
    )

    start_time = time.time()
    
    # 5. Formar el equipo y ejecutar
    mi_equipo = Crew(
        agents=[agente_planner, agente_ejecutor],
        tasks=[t_plan, t_ejecucion],
        process=Process.sequential
    )

    respuesta = str(mi_equipo.kickoff())
    
    end_time = time.time()
    tiempo_total = round(end_time - start_time, 2)
    
    metricas = {
        "tiempo_segundos": tiempo_total,
        "agentes_usados": f"Planner, {agente_ejecutor.role}",
        "herramientas_activas": len(herramientas_activas)
    }
    
    return respuesta, metricas
