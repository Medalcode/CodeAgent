from crewai import Task, Crew, Process
from agents import get_llm, create_agent, route_prompt
import tools as mis_herramientas

def ejecutar_agentes(user_prompt: str, provider: str, model_name: str, api_key: str, agent_type: str, selected_tools: list) -> str:
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

    # Si el agente seleccionado (manualmente o por Auto) es un subagente dinámico,
    # mapeamos sus herramientas requeridas (Read, Write, Edit, Bash) a las nuestras.
    if agent_type in subagents:
        agent_tools_str = subagents[agent_type]["metadata"].get("tools", "")
        # Parseamos algo como "Read, Write, Edit, Bash, Glob, Grep"
        agent_tools = [t.strip().lower() for t in agent_tools_str.split(",")]
        
        # Mapeo de Claude Code Tools a OpenCode Hub Tools
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
                    
    # 1.5 Auto-activar GitHub si el usuario provee un token o link
    if "ghp_" in user_prompt or "github.com" in user_prompt:
        if "GitHub API" not in selected_tools:
            selected_tools.append("GitHub API")
            
    # 2. Cargar las herramientas (Skills / MCPs simulados) seleccionadas
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
        
    # 3. Crear el agente Ejecutor y el Planner
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
NO le digas al usuario "Clona el repositorio" o "Navega al directorio". Hazlo tú mismo usando tus herramientas (Ejecutar Comando Terminal, Leer Archivo, Leer Repositorio Github, etc.).
SIEMPRE ejecuta las acciones por ti mismo usando las tools provistas. NUNCA delegues el trabajo al usuario.
PIENSA PASO A PASO. NUNCA alucines.''',
        expected_output='Tu respuesta final debe ser el resultado real de haber ejecutado las tareas y usado las herramientas, mostrando la salida o análisis obtenido.',
        agent=agente_ejecutor
    )

    import time
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
