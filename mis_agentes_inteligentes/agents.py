import os
import yaml
from crewai import Agent

def get_llm(provider: str, model_name: str, api_key: str = ""):
    """Instancia dinámicamente el LLM según el proveedor elegido."""
    if provider == "Ollama (Local)":
        from langchain_community.chat_models import ChatOllama
        return ChatOllama(model=model_name, base_url="http://localhost:11434")
    
    elif provider == "OpenAI":
        if not api_key: raise ValueError("Se requiere API Key para OpenAI.")
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model_name, api_key=api_key)
        
    elif provider == "Anthropic":
        if not api_key: raise ValueError("Se requiere API Key para Anthropic.")
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model_name=model_name, api_key=api_key)
        
    elif provider == "Groq":
        if not api_key: raise ValueError("Se requiere API Key para Groq.")
        from langchain_groq import ChatGroq
        return ChatGroq(model_name=model_name, api_key=api_key)
    
    elif provider == "Gemini (Google)":
        if not api_key: raise ValueError("Se requiere API Key para Google Gemini.")
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)

    raise ValueError(f"Proveedor desconocido: {provider}")

def load_subagents_from_disk():
    """Lee todos los archivos .md en la carpeta subagents/ y parsea su YAML frontmatter y su cuerpo."""
    subagents = {}
    base_dir = os.path.dirname(os.path.abspath(__file__))
    subagents_dir = os.path.join(base_dir, "subagents")
    
    if not os.path.exists(subagents_dir):
        return subagents
        
    for filename in os.listdir(subagents_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(subagents_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Parsear el YAML Frontmatter
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    try:
                        metadata = yaml.safe_load(parts[1])
                        body = parts[2].strip()
                        if metadata and "name" in metadata:
                            subagents[metadata["name"]] = {
                                "metadata": metadata,
                                "body": body
                            }
                    except Exception as e:
                        print(f"Error parseando {filename}: {e}")
    return subagents

def get_available_agents():
    """Devuelve la lista completa de agentes disponibles (Fijos + Dinámicos)."""
    agentes_fijos = ["Ingeniero de Software Local", "Analista de Código (Experto Github)", "Asistente de Eventos y Productividad", "Asistente General"]
    subagents = load_subagents_from_disk()
    agentes_dinamicos = list(subagents.keys())
    return agentes_fijos + agentes_dinamicos

def create_agent(agent_type: str, llm, tools_list: list):
    """Fábrica de agentes dinámicos basada en el rol seleccionado."""
    # 1. Chequear si es un agente fijo clásico
    if agent_type == "Ingeniero de Software Local":
        return Agent(
            role='Ingeniero de Software Local',
            goal='Desarrollar, refactorizar y probar código directamente en el disco duro del usuario.',
            backstory='Eres un Ingeniero de Software Senior. Tienes acceso al disco duro del usuario y la terminal. REGLAS: 1. Siempre usa "Listar Directorio Local" y "Leer Archivo Local" antes de intentar modificar algo. 2. Usa "Editar Archivo (Search/Replace)" para modificar código sin romperlo. 3. Usa "Ejecutar Comando Terminal" para probar.',
            tools=tools_list,
            llm=llm,
            verbose=True,
            max_iter=5
        )
    elif agent_type == "Analista de Código (Experto Github)":
        return Agent(
            role='Analista de Código Senior',
            goal='Hacer análisis profundos de repositorios en GitHub.',
            backstory='Eres un experto en Github. REGLAS ESTRICTAS: 1. Si el usuario te da un token, USA INMEDIATAMENTE la herramienta "Consultar Github" para listar sus repositorios. 2. Si te piden analizar un repositorio (o varios), USA SIEMPRE "Leer Repositorio Github" pasándole el nombre completo (ej: usuario/repo1, usuario/repo2) y el token. NUNCA alucines o inventes el contenido de un repo, debes descargarlo con tu herramienta primero.',
            tools=tools_list,
            llm=llm,
            verbose=True,
            max_iter=5
        )
    elif agent_type == "Asistente de Eventos y Productividad":
        return Agent(
            role='Asistente de Productividad',
            goal='Gestionar la agenda del usuario y ayudarle con tareas del día a día.',
            backstory='Eres un asistente personal amigable. Usa tus herramientas de Base de Datos para consultar SQLite.',
            tools=tools_list,
            llm=llm,
            verbose=True,
            max_iter=5
        )
    elif agent_type == "Asistente General":
        return Agent(
            role='Asistente General Multiusos',
            goal='Conversar amigablemente y utilizar cualquier herramienta a disposición.',
            backstory='Eres una IA versátil. Respondes con claridad.',
            tools=tools_list,
            llm=llm,
            verbose=True,
            max_iter=5
        )
    
    # 2. Chequear si es un Subagente Dinámico (Markdown de Claude Code)
    subagents = load_subagents_from_disk()
    if agent_type in subagents:
        agent_data = subagents[agent_type]
        metadata = agent_data["metadata"]
        body = agent_data["body"]
        
        # Inyectamos la regla de Aider a TODOS los subagentes para que no alucinen
        backstory_mejorado = body + "\n\nCRITICAL RULES:\n- YOU MUST use the Edit File (Search/Replace) tool to modify existing code. DO NOT overwrite files entirely unless creating new ones."
        
        return Agent(
            role=metadata.get("name", "Agente Especializado"),
            goal=metadata.get("description", "Resolver la tarea encomendada por el usuario."),
            backstory=backstory_mejorado,
            tools=tools_list,  # El main.py le inyectará las tools correctas
            llm=llm,
            verbose=True,
            max_iter=5
        )
        
    raise ValueError(f"Agente no encontrado: {agent_type}")

def route_prompt(prompt: str, llm) -> str:
    """Clasifica el prompt y decide qué agente instanciar (Swarm Router)."""
    agentes_disponibles = get_available_agents()
    
    # Preparamos un string con los agentes y sus descripciones cortas para el router
    lista_opciones = []
    subagents = load_subagents_from_disk()
    
    descripciones_fijas = {
        "Ingeniero de Software Local": "Desarrollador general para programar, refactorizar y probar código localmente.",
        "Analista de Código (Experto Github)": "Especialista en descargar, inspeccionar y analizar repositorios de GitHub usando tokens.",
        "Asistente de Eventos y Productividad": "Asistente para gestionar agenda y base de datos local SQLite.",
        "Asistente General": "Agente conversacional sin especialidad técnica."
    }

    for agent in agentes_disponibles:
        if agent in subagents:
            desc = subagents[agent]["metadata"].get("description", "Especialista")
            lista_opciones.append(f'- "{agent}": {desc}')
        else:
            desc = descripciones_fijas.get(agent, "Agente del sistema fijo.")
            lista_opciones.append(f'- "{agent}": {desc}')

    opciones_str = "\n".join(lista_opciones)
    
    system_prompt = f'''Eres un Enrutador Maestro de Tareas. Lee la petición del usuario y decide qué agente especializado debe atenderla de esta lista:
{opciones_str}

Responde ÚNICAMENTE con el nombre exacto del agente de la lista anterior. Nada más.

Petición del usuario: {prompt}
Agente seleccionado:'''
    
    # --- Fallback por palabras clave (más rápido y fiable que el LLM) ---
    prompt_lower = prompt.lower()
    if any(k in prompt for k in ["ghp_", "github.com"]) or any(k in prompt_lower for k in ["repositorio", "repo", "github", "token"]):
        return "Analista de Código (Experto Github)"
    if any(k in prompt_lower for k in ["agenda", "evento", "recordatorio", "tarea", "productividad"]):
        return "Asistente de Eventos y Productividad"
    if any(k in prompt_lower for k in ["código", "archivo", "función", "bug", "error", "refactor", "test", "implementa", "crea un", "modifica"]):
        return "Ingeniero de Software Local"

    # --- Si no hay match por keywords, preguntar al LLM ---
    try:
        response = llm.invoke(system_prompt)
        texto = response.content if hasattr(response, 'content') else str(response)
        
        for agent in agentes_disponibles:
            if agent in texto:
                return agent
        return "Asistente General"
    except Exception:
        return "Asistente General"

def create_planner_agent(llm):
    from crewai import Agent
    return Agent(
        role='Arquitecto de Software (Planner)',
        goal='Analizar la petición del usuario y crear un plan paso a paso.',
        backstory='Eres un arquitecto de software experto. Tu trabajo es leer el requerimiento y el contexto, y dividir la solución en pasos claros, lógicos y secuenciales (Paso 1, Paso 2, etc.) que otro agente ejecutará. No escribes el código final ni usas herramientas de ejecución, solo entregas el PLAN.',
        tools=[],  # El planner no usa herramientas, solo piensa.
        llm=llm,
        verbose=True,
        max_iter=3
    )
