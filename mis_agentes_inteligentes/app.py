import streamlit as st
import os
import datetime
from datetime import datetime as dt

# ─── Soporte .env ────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

import session_manager
from main import ejecutar_agentes

os.chdir(os.path.dirname(os.path.abspath(__file__)))
session_manager.init_sessions_dir()

st.set_page_config(page_title="OpenCode Hub", page_icon="💻", layout="wide")

# ─────────────────────────────────────────────────────────────────────────────
# INICIALIZACIÓN DE ESTADO
# ─────────────────────────────────────────────────────────────────────────────
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR: Configuración y Sesiones
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuración del Hub")

    provider = st.selectbox(
        "Proveedor de IA",
        ["Ollama (Local)", "OpenAI", "Anthropic", "Groq", "Gemini (Google)"]
    )

    if provider == "Ollama (Local)":
        model_name = st.selectbox(
            "Modelo",
            ["qwen2.5-coder:7b", "qwen2.5-coder:14b", "llama3.1:8b", "mistral", "gemma2", "qwen2", "deepseek-coder:6.7b"]
        )
        api_key = ""
    elif provider == "OpenAI":
        model_name = st.selectbox("Modelo", ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"])
        api_key = st.text_input(
            "API Key",
            type="password",
            value=os.environ.get("OPENAI_API_KEY", ""),
            help="Introduce tu API Key o guárdala en el archivo .env"
        )
    elif provider == "Anthropic":
        model_name = st.selectbox("Modelo", ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"])
        api_key = st.text_input(
            "API Key",
            type="password",
            value=os.environ.get("ANTHROPIC_API_KEY", ""),
            help="Introduce tu API Key o guárdala en el archivo .env"
        )
    elif provider == "Groq":
        model_name = st.selectbox("Modelo", ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "mixtral-8x7b-32768"])
        api_key = st.text_input(
            "API Key",
            type="password",
            value=os.environ.get("GROQ_API_KEY", ""),
            help="Introduce tu API Key o guárdala en el archivo .env"
        )
    elif provider == "Gemini (Google)":
        model_name = st.selectbox("Modelo", ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"])
        api_key = st.text_input(
            "API Key",
            type="password",
            value=os.environ.get("GOOGLE_API_KEY", ""),
            help="Introduce tu API Key o guárdala en el archivo .env"
        )
    else:
        model_name = ""
        api_key = ""

    st.divider()

    from agents import get_available_agents

    st.header("🤖 Agente (Persona)")
    lista_agentes = ["Auto (Enrutador Automático) 🌟"] + get_available_agents()
    agent_type = st.selectbox("Seleccionar Agente", lista_agentes)

    st.divider()

    st.header("🛠️ Herramientas y Skills")
    if agent_type == "Auto (Enrutador Automático) 🌟":
        st.info("🪄 En modo Auto, el Ruteador asignará las herramientas ideales automáticamente.")
        selected_tools = []
    else:
        use_local_fs = st.checkbox("Archivos Locales (Leer/Escribir)", value=True)
        use_git = st.checkbox("Control de Versiones (Git)", value=True)
        use_terminal = st.checkbox("Terminal Integrada", value=True)
        use_db = st.checkbox("Base de Datos (SQLite)", value=False)
        use_github = st.checkbox("GitHub API", value=False)
        use_websearch = st.checkbox("Búsqueda Web (Google)", value=False)
        use_rag = st.checkbox("Memoria RAG (Indexación Local)", value=False)

        selected_tools = []
        if use_local_fs: selected_tools.append("Archivos Locales")
        if use_git: selected_tools.append("Git")
        if use_terminal: selected_tools.append("Terminal Integrada")
        if use_db: selected_tools.append("Base de Datos (SQLite)")
        if use_github: selected_tools.append("Github")
        if use_websearch: selected_tools.append("Búsqueda Web")
        if use_rag: selected_tools.append("Memoria RAG")

    st.divider()

    # ── Gestión de Sesiones ───────────────────────────────────────────────────
    st.header("📁 Sesiones")

    col_new, col_export = st.columns(2)
    with col_new:
        if st.button("➕ Nueva", use_container_width=True):
            new_id = session_manager.create_new_session("Sesión " + dt.now().strftime("%H:%M:%S"))
            st.session_state.current_session_id = new_id
            st.session_state.messages = []
            st.rerun()

    # BUG 4 FIX: función de cache con TTL corto para que se invalide automáticamente
    def get_sessions_list():
        return session_manager.list_sessions()

    sesiones = get_sessions_list()
    sesiones_dict = {s["id"]: s["name"] for s in sesiones}

    if sesiones:
        index = 0
        if st.session_state.current_session_id in sesiones_dict:
            index = list(sesiones_dict.keys()).index(st.session_state.current_session_id)

        selected_session = st.selectbox(
            "Cambiar de Sesión",
            options=list(sesiones_dict.keys()),
            format_func=lambda x: sesiones_dict.get(x, x),
            index=index
        )

        if selected_session != st.session_state.current_session_id:
            st.session_state.current_session_id = selected_session
            s_data = session_manager.load_session(selected_session)
            st.session_state.messages = s_data["messages"] if s_data else []
            st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Borrar", use_container_width=True):
                # BUG 5 FIX: session_manager.delete_session ahora maneja None
                session_manager.delete_session(st.session_state.current_session_id)
                st.session_state.current_session_id = None
                st.session_state.messages = []
                st.rerun()
        with col2:
            if st.session_state.current_session_id:
                md = session_manager.export_session_to_markdown(st.session_state.current_session_id)
                nombre = sesiones_dict.get(st.session_state.current_session_id, "sesion")
                st.download_button(
                    "📤 Exportar",
                    data=md,
                    file_name=f"{nombre[:20]}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
    else:
        sesiones_dict = {}

# ─────────────────────────────────────────────────────────────────────────────
# CREAR SESIÓN POR DEFECTO SI NO HAY NINGUNA
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.current_session_id:
    new_id = session_manager.create_new_session("Sesión " + dt.now().strftime("%H:%M:%S"))
    st.session_state.current_session_id = new_id

# ─────────────────────────────────────────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────────────────────────────────────────
st.title("💻 OpenCode Hub")
st.caption(f"🤖 **{agent_type}** · {provider} / `{model_name}` | `/help`, `/clear`, `/export`")

# Mostrar historial de la sesión actual
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("time"):
            st.caption(f"🕒 {msg['time']}")
        st.markdown(msg["content"])

# ─────────────────────────────────────────────────────────────────────────────
# CAPTURA DE INPUT
# ─────────────────────────────────────────────────────────────────────────────
prompt = st.chat_input(f"Escribe tu petición a {agent_type} (/help para comandos)")

if prompt:
    # ── Slash Commands ────────────────────────────────────────────────────────
    if prompt.strip().startswith("/"):
        comando = prompt.strip().lower()

        if comando == "/help":
            ayuda = (
                "**Comandos Disponibles:**\n"
                "- `/help` — Muestra esta ayuda\n"
                "- `/clear` — Borra el historial de la sesión actual\n"
                "- `/export` — Exporta la sesión como Markdown\n"
                "- `/status` — Muestra la configuración activa\n\n"
                "*Tip:* Usa `@workspace` en tu mensaje para que el agente analice la estructura del proyecto automáticamente."
            )
            st.session_state.messages.append({"role": "assistant", "content": ayuda, "time": dt.now().strftime("%H:%M:%S")})
            session_manager.save_session(
                st.session_state.current_session_id,
                {"id": st.session_state.current_session_id, "name": sesiones_dict.get(st.session_state.current_session_id, "Sesión"), "messages": st.session_state.messages}
            )
            st.rerun()

        elif comando == "/clear":
            st.session_state.messages = []
            session_manager.save_session(
                st.session_state.current_session_id,
                {"id": st.session_state.current_session_id, "name": sesiones_dict.get(st.session_state.current_session_id, "Sesión"), "messages": []}
            )
            st.rerun()

        elif comando == "/status":
            status = (
                f"**Configuración Activa:**\n"
                f"- 🤖 Agente: `{agent_type}`\n"
                f"- ☁️ Proveedor: `{provider}`\n"
                f"- 🧠 Modelo: `{model_name}`\n"
                f"- 🛠️ Herramientas: `{', '.join(selected_tools) or 'Ninguna (modo chat)'}`\n"
                f"- 📁 Directorio: `{os.getcwd()}`\n"
                f"- 💬 Mensajes en sesión: `{len(st.session_state.messages)}`"
            )
            st.session_state.messages.append({"role": "assistant", "content": status, "time": dt.now().strftime("%H:%M:%S")})
            st.rerun()

        elif comando == "/export":
            md = session_manager.export_session_to_markdown(st.session_state.current_session_id)
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"📤 Sesión lista para exportar. Usa el botón **Exportar** en el sidebar.",
                "time": dt.now().strftime("%H:%M:%S")
            })
            st.rerun()

        else:
            st.warning(f"Comando desconocido: `{comando}`. Escribe `/help` para ver los comandos.")

    # ── Flujo normal de chat ──────────────────────────────────────────────────
    else:
        timestamp = dt.now().strftime("%H:%M:%S")
        st.session_state.messages.append({"role": "user", "content": prompt, "time": timestamp})

        with st.chat_message("user"):
            st.caption(f"🕒 {timestamp}")
            st.markdown(prompt)

        with st.chat_message("assistant"):
            respuesta = ""
            metricas = {"tiempo_segundos": 0, "agentes_usados": "-", "herramientas_activas": 0}

            # BUG 3 FIX: construir el prompt correcto
            # Solo el prompt actual + contexto comprimido del historial reciente
            historial_reciente = st.session_state.messages[-7:-1]  # últimos 7 mensajes, sin el actual
            if historial_reciente:
                contexto_historial = "## Historial reciente de la conversación\n"
                for m in historial_reciente:
                    role_label = "Usuario" if m["role"] == "user" else "Asistente"
                    # Comprimir respuestas largas del asistente
                    contenido = m["content"]
                    if m["role"] == "assistant" and len(contenido) > 400:
                        contenido = contenido[:400] + "... [resumido]"
                    contexto_historial += f"**{role_label}:** {contenido}\n\n"
                prompt_final = f"{contexto_historial}\n---\n\n## Petición actual del usuario\n{prompt}"
            else:
                prompt_final = prompt

            # Inyectar contexto @workspace si se menciona
            if "@workspace" in prompt.lower() or "analiza este proyecto" in prompt.lower():
                import tools as mis_herramientas
                contexto_ws = mis_herramientas.obtener_contexto_workspace()
                prompt_final = f"{contexto_ws}\n\n{prompt_final}"

            status_placeholder = st.empty()
            response_placeholder = st.empty()

            with st.spinner(f"🧠 {agent_type} ({provider}/{model_name}) procesando..."):
                try:
                    respuesta, metricas = ejecutar_agentes(
                        user_prompt=prompt_final,
                        provider=provider,
                        model_name=model_name,
                        api_key=api_key,
                        agent_type=agent_type,
                        selected_tools=selected_tools,
                    )
                    response_placeholder.markdown(respuesta)

                except Exception as e:
                    import traceback
                    respuesta = f"❌ **Error de ejecución:**\n```\n{e}\n```"
                    st.error(respuesta)

                finally:
                    ts_resp = dt.now().strftime("%H:%M:%S")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": respuesta,
                        "time": ts_resp
                    })

                    # Auto-nombrar la sesión con el primer mensaje
                    nombre_sesion = sesiones_dict.get(st.session_state.current_session_id, "Sesión")
                    if len(st.session_state.messages) <= 2:
                        nombre_sesion = prompt[:30].strip() + "..."

                    # Guardar sesión en disco
                    session_manager.save_session(
                        st.session_state.current_session_id,
                        {
                            "id": st.session_state.current_session_id,
                            "name": nombre_sesion,
                            "messages": st.session_state.messages
                        }
                    )

            # Panel de métricas
            if metricas.get("tiempo_segundos"):
                with st.expander("📊 Métricas de Ejecución", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("⏱️ Tiempo", f"{metricas['tiempo_segundos']}s")
                    col2.metric("🤖 Agente", metricas.get("agentes_usados", "-").split("(")[-1].rstrip(")"))
                    col3.metric("🛠️ Herramientas", metricas.get("herramientas_activas", 0))
