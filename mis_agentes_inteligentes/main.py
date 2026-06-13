"""
Pipeline de agentes sin CrewAI.
El LLM solo genera texto. Python llama las herramientas directamente.
Compatible con cualquier modelo, incluyendo modelos locales de 7B.
"""
import re
import time
from agents import get_llm, route_prompt
import tools as mis_herramientas


# ─────────────────────────────────────────────────────────────────────────────
# UTILIDAD: invocar LLM de forma segura con fallback
# ─────────────────────────────────────────────────────────────────────────────
def _llamar_llm(llm, system: str, user: str) -> str:
    """Llama al LLM con mensajes estructurados o texto plano como fallback."""
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        resp = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
        return resp.content if hasattr(resp, "content") else str(resp)
    except Exception:
        resp = llm.invoke(f"{system}\n\n{user}")
        return resp.content if hasattr(resp, "content") else str(resp)


# ─────────────────────────────────────────────────────────────────────────────
# MODO GITHUB: herramientas llamadas desde Python, LLM solo analiza resultados
# ─────────────────────────────────────────────────────────────────────────────
def _modo_github(user_prompt: str, llm) -> tuple[str, dict]:
    start = time.time()

    # 1. Extraer token del mensaje
    match = re.search(r'ghp_[A-Za-z0-9]+', user_prompt)
    if not match:
        return "❌ No encontré un token de GitHub válido en el mensaje (debe empezar con `ghp_`).", {}
    token = match.group(0)

    # 2. Listar repos del usuario (llamada Python directa, sin LLM)
    repos_raw = mis_herramientas.consultar_github(token)

    # 3. Identificar qué repo pidió el usuario comparando nombres
    prompt_lower = user_prompt.lower().replace("-", "").replace(" ", "")
    repo_solicitado = None
    for linea in repos_raw.splitlines():
        m = re.search(r'Nombre completo: ([^\|]+)', linea)
        if m:
            full_name = m.group(1).strip()
            nombre_repo = full_name.split("/")[-1].lower().replace("-", "").replace("_", "")
            if nombre_repo in prompt_lower:
                repo_solicitado = full_name
                break

    # 4. Leer el repo identificado (llamada Python directa, sin LLM)
    if repo_solicitado:
        repo_info = mis_herramientas.leer_repositorio_github(
            token=token,
            nombres_repos=repo_solicitado
        )
    else:
        repo_info = f"Tus repositorios disponibles:\n{repos_raw}\n\n⚠️ No identifiqué el repositorio específico. Por favor menciona el nombre exacto."

    # 5. LLM analiza los datos reales (sin herramientas, solo texto)
    system = (
        "Eres un experto en análisis de código y arquitectura de software. "
        "Se te dan datos reales de un repositorio GitHub (estructura de archivos y README). "
        "Tu trabajo es: 1) Resumir qué hace el proyecto. 2) Evaluar su calidad (estructura, documentación, tecnologías). "
        "3) Listar fortalezas. 4) Listar debilidades y riesgos. 5) Proponer mejoras concretas. "
        "Responde siempre en español con formato Markdown claro."
    )
    user = f"Petición del usuario: {user_prompt}\n\nDatos reales del repositorio:\n{repo_info}"

    resultado = _llamar_llm(llm, system, user)

    return resultado, {
        "tiempo_segundos": round(time.time() - start, 2),
        "agentes_usados": "Pipeline Directo → GitHub",
        "herramientas_activas": 2
    }


# ─────────────────────────────────────────────────────────────────────────────
# MODO LOCAL: herramientas del sistema de archivos/terminal, LLM decide los pasos
# ─────────────────────────────────────────────────────────────────────────────
def _modo_local(user_prompt: str, llm, selected_tools: list) -> tuple[str, dict]:
    start = time.time()
    pasos_ejecutados = []

    # 1. LLM genera un plan de acción simple
    tools_disponibles = ", ".join(selected_tools) if selected_tools else "ninguna"
    plan_raw = _llamar_llm(
        llm,
        system=(
            "Eres un planificador de tareas de software. "
            f"Tienes disponibles estas herramientas: {tools_disponibles}. "
            "Genera un plan de máximo 3 pasos concisos para resolver la petición. "
            "Formato: 'Paso 1: ...' en líneas separadas. Sin explicaciones extra."
        ),
        user=f"Petición: {user_prompt}"
    )
    pasos_ejecutados.append(f"**📋 Plan generado:**\n{plan_raw}")

    # 2. Si hay archivos locales mencionados en el prompt, leerlos automáticamente
    contexto_archivos = ""
    if "Archivos Locales" in selected_tools:
        # Detectar rutas de archivo en el prompt
        rutas = re.findall(r'[\w./\\-]+\.(?:py|js|ts|json|md|txt|yaml|yml|css|html)', user_prompt)
        for ruta in rutas[:3]:  # máximo 3 archivos
            contenido = mis_herramientas.leer_archivo_local(ruta)
            if "Error" not in contenido:
                contexto_archivos += f"\n\n{contenido[:2000]}"
                pasos_ejecutados.append(f"**📄 Archivo leído:** `{ruta}`")

    # 3. LLM genera la respuesta final con el contexto real
    resultado = _llamar_llm(
        llm,
        system=(
            "Eres un ingeniero de software senior. "
            "Basándote en el plan y el contexto disponible, da una respuesta técnica completa y accionable. "
            "Si necesitas modificar archivos, muestra el código exacto con bloques ```código```. "
            "Responde en español."
        ),
        user=f"Petición original: {user_prompt}\n\nPlan elaborado:\n{plan_raw}\n\nContexto de archivos:{contexto_archivos if contexto_archivos else ' (ninguno detectado)'}"
    )

    pasos_ejecutados.append(f"**✅ Respuesta:**\n{resultado}")
    respuesta_final = "\n\n---\n\n".join(pasos_ejecutados)

    return respuesta_final, {
        "tiempo_segundos": round(time.time() - start, 2),
        "agentes_usados": "Pipeline Directo → Local",
        "herramientas_activas": len(selected_tools)
    }


# ─────────────────────────────────────────────────────────────────────────────
# MODO CONVERSACIÓN: respuesta directa del LLM, sin herramientas
# ─────────────────────────────────────────────────────────────────────────────
def _modo_conversacion(user_prompt: str, llm) -> tuple[str, dict]:
    start = time.time()
    resultado = _llamar_llm(
        llm,
        system="Eres un asistente de programación experto. Responde de forma clara, concisa y en español. Usa Markdown cuando sea útil.",
        user=user_prompt
    )
    return resultado, {
        "tiempo_segundos": round(time.time() - start, 2),
        "agentes_usados": "Pipeline Directo → Chat",
        "herramientas_activas": 0
    }


# ─────────────────────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────
def ejecutar_agentes(user_prompt: str, provider: str, model_name: str, api_key: str,
                     agent_type: str, selected_tools: list) -> tuple[str, dict]:
    """
    Pipeline principal sin CrewAI.
    Detecta el tipo de tarea y ejecuta el modo correcto automáticamente.
    """
    llm = get_llm(provider, model_name, api_key)

    # ── Modo GitHub: token detectado en el mensaje ──────────────────────────
    if "ghp_" in user_prompt or "github.com/" in user_prompt:
        return _modo_github(user_prompt, llm)

    # ── Enrutador automático ─────────────────────────────────────────────────
    if agent_type == "Auto (Enrutador Automático) 🌟":
        agent_type = route_prompt(user_prompt, llm)

    # ── Modo Local: ingeniero de software con herramientas ───────────────────
    if agent_type in ("Ingeniero de Software Local", "python-pro", "frontend-developer", "code-reviewer", "security-auditor"):
        # Auto-asignar herramientas si viene del modo Auto
        if not selected_tools:
            selected_tools = ["Archivos Locales", "Terminal Integrada", "Git"]
        return _modo_local(user_prompt, llm, selected_tools)

    # ── Modo Conversación: todo lo demás ────────────────────────────────────
    return _modo_conversacion(user_prompt, llm)
