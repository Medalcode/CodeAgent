import os
import yaml
from smolagents import CodeAgent, LiteLLMModel

def get_model(provider: str, model_name: str, api_key: str = ""):
    """Instancia dinámicamente el modelo LiteLLMModel según el proveedor elegido."""
    if provider == "Ollama (Local)":
        return LiteLLMModel(
            model_id=f"ollama_chat/{model_name}",
            api_base="http://localhost:11434"
        )
    
    elif provider == "OpenAI":
        if not api_key: raise ValueError("Se requiere API Key para OpenAI.")
        return LiteLLMModel(model_id=model_name, api_key=api_key)
        
    elif provider == "Anthropic":
        if not api_key: raise ValueError("Se requiere API Key para Anthropic.")
        # LiteLLM maneja anthropic models
        return LiteLLMModel(model_id=f"anthropic/{model_name}", api_key=api_key)
        
    elif provider == "Groq":
        if not api_key: raise ValueError("Se requiere API Key para Groq.")
        return LiteLLMModel(model_id=f"groq/{model_name}", api_key=api_key)
    
    elif provider == "Gemini (Google)":
        if not api_key: raise ValueError("Se requiere API Key para Google Gemini.")
        return LiteLLMModel(model_id=f"gemini/{model_name}", api_key=api_key)

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

def route_prompt(prompt: str) -> str:
    """Enrutador automático por palabras clave."""
    prompt_lower = prompt.lower()
    if any(k in prompt for k in ["ghp_", "github.com"]) or any(k in prompt_lower for k in ["repositorio", "repo", "github", "token"]):
        return "Analista de Código (Experto Github)"
    if any(k in prompt_lower for k in ["agenda", "evento", "recordatorio", "tarea", "productividad"]):
        return "Asistente de Eventos y Productividad"
    if any(k in prompt_lower for k in ["código", "archivo", "función", "bug", "error", "refactor", "test", "implementa", "crea un", "modifica"]):
        return "Ingeniero de Software Local"
    return "Asistente General"

def crear_agente(agent_type: str, model, tools_list: list):
    """Crea el CodeAgent de smolagents. El system_prompt puede personalizarse según el agent_type."""
    system_prompt = "Eres un asistente inteligente. Utiliza Python y las herramientas para resolver las peticiones del usuario."
    
    # 1. Chequear si es un agente fijo clásico
    if agent_type == "Ingeniero de Software Local":
        system_prompt = "Eres un Ingeniero de Software Senior. Tienes acceso al disco duro del usuario y la terminal. REGLAS: 1. Siempre explora el entorno antes de modificar algo. 2. Usa Python para ejecutar las herramientas necesarias. 3. Puedes usar herramientas de bash para probar."
    elif agent_type == "Analista de Código (Experto Github)":
        system_prompt = "Eres un experto en Github. Usa el token proporcionado por el usuario con las herramientas correspondientes para extraer y analizar repositorios. Escribe scripts en Python usando las herramientas provistas."
    elif agent_type == "Asistente de Eventos y Productividad":
        system_prompt = "Eres un Asistente de Productividad. Utiliza tus herramientas de BD para SQLite para consultar eventos y agendar."
    elif agent_type == "Asistente General":
        system_prompt = "Eres un asistente general versátil. Si tienes herramientas, úsalas escribiendo código Python."
    else:
        # 2. Chequear si es un Subagente Dinámico
        subagents = load_subagents_from_disk()
        if agent_type in subagents:
            agent_data = subagents[agent_type]
            system_prompt = agent_data["body"]
    
    return CodeAgent(
        tools=tools_list,
        model=model,
        max_steps=5,
        additional_authorized_imports=['os', 'subprocess', 'requests', 'json', 're', 'datetime']
    )
