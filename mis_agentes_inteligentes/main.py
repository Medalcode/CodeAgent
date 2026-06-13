from crewai import Task, Crew, Process
from agents import get_llm, create_agent
import tools as mis_herramientas

def ejecutar_agentes(user_prompt: str, provider: str, model_name: str, api_key: str, agent_type: str, selected_tools: list) -> str:
    """Ejecuta el equipo de agentes basándose en la configuración dinámica seleccionada en la UI."""
    
    # 1. Inicializar el Modelo de Lenguaje
    llm = get_llm(provider, model_name, api_key)
    
    # 2. Cargar las herramientas (Skills / MCPs simulados) seleccionadas
    herramientas_activas = []
    if "Base de Datos (SQLite)" in selected_tools:
        herramientas_activas.append(mis_herramientas.consultar_db)
        herramientas_activas.append(mis_herramientas.guardar_reporte)
    if "GitHub API" in selected_tools:
        herramientas_activas.append(mis_herramientas.consultar_github)
        herramientas_activas.append(mis_herramientas.leer_repositorio_github)
        
    # 3. Crear el agente con el Rol seleccionado
    agente = create_agent(agent_type, llm, herramientas_activas)

    # 4. Asignar la tarea pasando todo el historial como contexto
    t1 = Task(
        description=f'Contexto de la conversación:\n{user_prompt}\n\nInstrucción: Analiza el contexto y responde al último mensaje del usuario de la mejor forma posible. Usa tus herramientas solo si la petición lo requiere.',
        expected_output='Una respuesta conversacional, markdown-friendly y útil, dirigida al usuario.',
        agent=agente
    )

    # 5. Formar el equipo y ejecutar
    mi_equipo = Crew(
        agents=[agente],
        tasks=[t1],
        process=Process.sequential
    )

    return str(mi_equipo.kickoff())
