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
            selected_tools.extend(["Archivos Locales", "Terminal Integrada"])
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
            
    # 2. Cargar las herramientas (Skills / MCPs simulados) seleccionadas
    herramientas_activas = []
    if "Base de Datos (SQLite)" in selected_tools:
        herramientas_activas.append(mis_herramientas.consultar_db)
        herramientas_activas.append(mis_herramientas.guardar_reporte)
    if "GitHub API" in selected_tools:
        herramientas_activas.append(mis_herramientas.consultar_github)
        herramientas_activas.append(mis_herramientas.leer_repositorio_github)
    if "Archivos Locales" in selected_tools:
        herramientas_activas.append(mis_herramientas.listar_directorio_local)
        herramientas_activas.append(mis_herramientas.leer_archivo_local)
        herramientas_activas.append(mis_herramientas.escribir_archivo_local)
        herramientas_activas.append(mis_herramientas.editar_archivo_search_replace)
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
        
    # 3. Crear el agente con el Rol seleccionado
    agente = create_agent(agent_type, llm, herramientas_activas)

    # 4. Asignar la tarea pasando todo el historial como contexto
    t1 = Task(
        description=f'''Contexto de la conversación:
{user_prompt}

INSTRUCCIÓN CRÍTICA PARA EL MODELO: 
Tu único trabajo es analizar el último mensaje del usuario. 
¡TIENES HERRAMIENTAS DISPONIBLES! NUNCA digas "no tengo información" o "no puedo encontrar". 
Si te dan un token de GitHub, DEBES invocar la herramienta "Consultar Github".
Si te mencionan un repositorio, DEBES invocar la herramienta "Leer Repositorio Github".
Si te piden revisar archivos locales, DEBES invocar "Listar Directorio Local" o "Leer Archivo Local".

PIENSA PASO A PASO. Usa tus herramientas para buscar la información ANTES de responder al usuario. NUNCA alucines.''',
        expected_output='Tu respuesta final debe ser un análisis detallado y completo dirigido al usuario, escrito en lenguaje natural y formateado con Markdown. NUNCA respondas con placeholders como "[La respuesta aquí]".',
        agent=agente
    )

    # 5. Formar el equipo y ejecutar
    mi_equipo = Crew(
        agents=[agente],
        tasks=[t1],
        process=Process.sequential
    )

    return str(mi_equipo.kickoff())
