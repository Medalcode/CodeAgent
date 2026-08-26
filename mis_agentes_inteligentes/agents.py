import logging
import os
import time

import yaml

# Soporte para .env
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

from smolagents import CodeAgent, LiteLLMModel

_SUBAGENTS_CACHE = {}
_SUBAGENTS_LAST_MTIME = 0

# System prompts por agente — definidos aquí para que sean el source of truth
SYSTEM_PROMPTS = {
    "CodeAgent Developer": (
        "Eres CodeAgent Developer, un agente autónomo de ingeniería de software operando sobre el proyecto local del usuario. "
        "Trabajas sobre el modelo y proveedor configurados por el sistema (como Qwen Coder, DeepSeek Coder, Gemini, Llama o GPT). "
        "No debes atribuirte la identidad del proveedor o fabricante del modelo. Tu función es utilizar las herramientas disponibles para inspeccionar, analizar, modificar y verificar software.\n\n"
        "REGLAS DE OPERACIÓN CODEAGENT:\n"
        "1. EXPLORACIÓN PROACTIVA: Inspecciona el espacio de trabajo usando `listar_directorio_local`, `leer_archivo_local` o herramientas de GitHub/Graphify antes de planificar o modificar nada.\n"
        "2. EDICIÓN DE CÓDIGO CON DIFFS: Para modificar archivos existentes, usa `editar_archivo_search_replace` incluyendo suficiente contexto alrededor del bloque de búsqueda. Usa `escribir_archivo_local` ÚNICAMENTE para crear archivos nuevos desde cero.\n"
        "3. CICLO TDD Y AUTOVERIFICACIÓN: Tras realizar un cambio, ejecuta la suite de pruebas o verifica el código usando `ejecutar_comando_terminal`. Si falla, analiza el error completo, ajusta el código y vuelve a probar.\n"
        "4. SEGURIDAD: Nunca ejecutes comandos destructivos de sistema (rm -rf, format, etc).\n"
        "5. RESPUESTAS CONCISAS Y ESTRUCTURADAS: Proporciona explicaciones claras en español, muestra diffs de cambios y concluye con `final_answer()` resumiendo exactamente qué archivos fueron modificados o creados.\n"
    ),
    "Agente de Edición de Código": (
        "Eres un Ingeniero de Software Senior trabajando en el sistema operativo del usuario. "
        "Tienes acceso total al disco duro y a la terminal.\n\n"
        "REGLAS ESTRICTAS:\n"
        "1. SIEMPRE empieza explorando el entorno: lista el directorio de trabajo antes de modificar nada.\n"
        "2. USA `editar_archivo_search_replace` para modificaciones parciales. "
        "USA `escribir_archivo_local` SOLO para crear archivos nuevos desde cero.\n"
        "3. Usa RUTAS ABSOLUTAS o rutas relativas verificadas. Nunca asumas una ruta.\n"
        "4. Después de cada modificación, LEE el archivo para verificar que el cambio es correcto.\n"
        "5. Usa la terminal para ejecutar tests, instalar dependencias o verificar resultados.\n"
        "6. Termina con `final_answer()` describiendo exactamente qué hiciste y qué archivos cambiaste.\n"
        "7. Si un comando falla, lee el error completo y corrígelo antes de continuar.\n"
        "8. Nunca ejecutes comandos destructivos (rm -rf, format, etc).\n"
    ),
    "Arquitecto de Agentes Smolagents": (
        "Eres un arquitecto experto en smolagents de HuggingFace. "
        "Diseñas, depuras y optimizas pipelines de agentes con CodeAgent, ToolCallingAgent y modelos LiteLLM. "
        "Cuando modificas system_prompts de agentes, siempre validas la sintaxis Python antes de guardar. "
        "Documenta cada cambio con comentarios y usa editar_archivo_search_replace para modificaciones puntuales."
    ),
    "Analista de Código (Experto Github)": (
        "Eres un experto en análisis de repositorios GitHub. "
        "Cuando el usuario te proporciona un token (ghp_...) y un nombre de repositorio, "
        "usas las herramientas de GitHub para extraer el README, la estructura y los archivos clave. "
        "Sintetiza los hallazgos en un reporte estructurado con: propósito, tecnologías, arquitectura y puntos de mejora."
    ),
    "Asistente de Eventos y Productividad": (
        "Eres un Asistente de Productividad Personal. "
        "Usas la herramienta de base de datos SQLite para consultar eventos, tareas y recordatorios. "
        "SOLO puedes hacer SELECT. Nunca INSERT, UPDATE ni DELETE. "
        "Presenta los datos de forma clara con emojis y formato de tabla cuando sea posible."
    ),
    "Asistente General": (
        "Eres un asistente inteligente y versátil. Responde en el mismo idioma del usuario. "
        "Si tienes herramientas disponibles, úsalas activamente para dar respuestas más completas. "
        "Sé conciso pero completo."
    ),
}

DEFAULT_PROMPT = (
    "Eres un asistente inteligente. Utiliza las herramientas disponibles para resolver "
    "las peticiones del usuario de forma precisa y eficiente."
)


def get_model(provider: str, model_name: str, api_key: str = ""):
    """Instancia dinámicamente el modelo LiteLLMModel según el proveedor elegido."""
    if provider == "Ollama (Local)":
        return LiteLLMModel(
            model_id=f"ollama_chat/{model_name}",
            api_base=os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")
        )

    provider_map = {
        "OpenAI": ("OPENAI_API_KEY", model_name),
        "Anthropic": ("ANTHROPIC_API_KEY", f"anthropic/{model_name}"),
        "Groq": ("GROQ_API_KEY", f"groq/{model_name}"),
        "Gemini (Google)": ("GOOGLE_API_KEY", f"gemini/{model_name}"),
    }

    if provider not in provider_map:
        raise ValueError(f"Proveedor desconocido: {provider}")

    env_key, model_id = provider_map[provider]
    if not api_key:
        api_key = os.environ.get(env_key, "")

    if not api_key:
        raise ValueError(f"Se requiere API Key para {provider} (en .env o en el sidebar).")

    return LiteLLMModel(model_id=model_id, api_key=api_key)


def load_subagents_from_disk():
    """Lee todos los archivos .md en la carpeta subagents/ y parsea su YAML frontmatter y su cuerpo.
    Utiliza almacenamiento en caché basado en mtime para maximizar el rendimiento.
    """
    global _SUBAGENTS_CACHE, _SUBAGENTS_LAST_MTIME
    base_dir = os.path.dirname(os.path.abspath(__file__))
    subagents_dir = os.path.join(base_dir, "subagents")

    if not os.path.exists(subagents_dir):
        _SUBAGENTS_CACHE = {}
        _SUBAGENTS_LAST_MTIME = 0
        return _SUBAGENTS_CACHE

    try:
        current_mtime = os.path.getmtime(subagents_dir)
    except OSError:
        current_mtime = time.time()

    if _SUBAGENTS_CACHE and current_mtime == _SUBAGENTS_LAST_MTIME:
        return _SUBAGENTS_CACHE

    subagents = {}
    for filename in os.listdir(subagents_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(subagents_dir, filename)
            try:
                with open(filepath, encoding="utf-8") as f:
                    content = f.read()

                # Parsear el YAML Frontmatter
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        metadata = yaml.safe_load(parts[1])
                        body = parts[2].strip()
                        if metadata and "name" in metadata:
                            subagents[metadata["name"]] = {
                                "metadata": metadata,
                                "body": body
                            }
            except Exception as e:
                logging.warning(f"Error parseando subagente {filename}: {e}")

    _SUBAGENTS_CACHE = subagents
    _SUBAGENTS_LAST_MTIME = current_mtime
    return subagents


def get_available_agents():
    """Devuelve la lista completa de agentes disponibles (Fijos + Dinámicos)."""
    agentes_fijos = [
        "CodeAgent Developer",
        "Agente de Edición de Código",
        "Analista de Código (Experto Github)",
        "Asistente de Eventos y Productividad",
        "Asistente General",
    ]
    subagents = load_subagents_from_disk()
    agentes_dinamicos = list(subagents.keys())
    return agentes_fijos + agentes_dinamicos


def route_prompt(prompt: str) -> str:
    """Enrutador automático mejorado con scoring ponderado."""
    prompt_lower = prompt.lower()
    scores = {
        "CodeAgent Developer": 0,
        "Analista de Código (Experto Github)": 0,
        "Agente de Edición de Código": 0,
        "Asistente de Eventos y Productividad": 0,
        "Asistente General": 0,
    }

    # Señales explícitas de CodeAgent / OpenCode / Modelos locales
    if any(k in prompt_lower for k in ["codeagent", "developer", "claude", "opencode", "qwen", "deepseek"]):
        scores["CodeAgent Developer"] += 12

    # Señales fuertes de GitHub (peso 10)
    if any(k in prompt for k in ["ghp_", "github.com/", "github.com"]):
        scores["Analista de Código (Experto Github)"] += 10
    if any(k in prompt_lower for k in ["repo", "repositorio", "github", "gh", "pull request", "pr", "branch", "commit", "issue"]):
        scores["Analista de Código (Experto Github)"] += 5

    # Señales de edición de código y desarrollo de software
    edit_keywords = {
        "refactor": 8, "implementa": 8, "crea un archivo": 8, "modifica": 7,
        "bug": 6, "error": 5, "arregla": 7, "test": 6, "función": 5,
        "código": 4, "archivo": 3, "clase": 5, "import": 4,
    }
    for kw, weight in edit_keywords.items():
        if kw in prompt_lower:
            scores["CodeAgent Developer"] += weight
            scores["Agente de Edición de Código"] += max(1, weight - 1)

    # Señales de productividad
    prod_keywords = ["agenda", "evento", "recordatorio", "tarea", "productividad", "calendario"]
    for kw in prod_keywords:
        if kw in prompt_lower:
            scores["Asistente de Eventos y Productividad"] += 8

    # Evaluar subagentes dinámicos desde disco
    subagents = load_subagents_from_disk()
    for name, data in subagents.items():
        scores[name] = 0
        desc = (data.get("metadata", {}).get("description", "") + " " + data.get("body", "")).lower()
        words = [w for w in prompt_lower.split() if len(w) > 3]
        matches = sum(1 for w in words if w in desc)
        if matches > 0:
            scores[name] += min(matches * 3, 9)

    best = max(scores, key=scores.get)
    # Si ninguno supera el umbral mínimo, usar Asistente General
    if scores[best] < 4:
        return "Asistente General"
    return best


def crear_agente(agent_type: str, model, tools_list: list, workspace_context: str = ""):
    """
    Crea el CodeAgent de smolagents.
    FIX: system_prompt ahora se pasa correctamente al constructor.
    FIX: max_steps aumentado a 20 para tareas complejas.
    """
    # 1. Obtener system_prompt base del tipo de agente
    system_prompt = SYSTEM_PROMPTS.get(agent_type, "")

    # 2. Chequear subagentes dinámicos si no es un agente fijo
    if not system_prompt:
        subagents = load_subagents_from_disk()
        system_prompt = subagents[agent_type]["body"] if agent_type in subagents else DEFAULT_PROMPT

    # 3. Inyectar contexto de workspace si está disponible
    if workspace_context:
        system_prompt = f"{system_prompt}\n\n{workspace_context}"

    return CodeAgent(
        tools=tools_list,
        model=model,
        system_prompt=system_prompt,  # FIX: ahora se pasa correctamente
        max_steps=20,                 # FIX: aumentado de 10 a 20
        additional_authorized_imports=[
            'os', 'subprocess', 'requests', 'json', 're', 'datetime', 'pathlib'
        ]
    )
