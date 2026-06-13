from crewai import Agent

def get_llm(provider: str, model_name: str, api_key: str = ""):
    """Instancia dinámicamente el LLM según el proveedor elegido."""
    if provider == "Ollama (Local)":
        from langchain_community.llms import Ollama
        return Ollama(model=model_name, base_url="http://localhost:11434")
    
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

def create_agent(agent_type: str, llm, tools_list: list):
    """Fábrica de agentes dinámicos basada en el rol seleccionado."""
    if agent_type == "Analista de Código (Experto Github)":
        return Agent(
            role='Analista de Código Senior',
            goal='Hacer análisis profundos de código en repositorios y resolver dudas de desarrollo.',
            backstory='Eres un arquitecto de software experto. Analizas el código, la estructura de archivos y los READMEs para dar feedback constructivo. NUNCA inventes información; usa SIEMPRE tus herramientas para leer repositorios.',
            tools=tools_list,
            llm=llm,
            verbose=True
        )
    elif agent_type == "Asistente de Eventos y Productividad":
        return Agent(
            role='Asistente de Productividad',
            goal='Gestionar la agenda del usuario y ayudarle con tareas del día a día.',
            backstory='Eres un asistente personal amigable. Puedes conversar de cualquier tema, pero tu fuerte es consultar la base de datos de eventos y ayudar al usuario a priorizar su día.',
            tools=tools_list,
            llm=llm,
            verbose=True
        )
    else: # "Asistente General"
        return Agent(
            role='Asistente General Multiusos',
            goal='Conversar amigablemente y utilizar cualquier herramienta que tengas a disposición si el usuario te lo pide explícitamente.',
            backstory='Eres una IA versátil. Respondes con claridad y concisión. Estás equipado con varias herramientas y sabes usarlas proactivamente según el contexto de la conversación.',
            tools=tools_list,
            llm=llm,
            verbose=True
        )
