import os
import warnings
from datetime import datetime as dt

import session_manager
import streamlit as st
from main import ejecutar_agentes
from tools import obtener_contexto_workspace

warnings.warn("app.py (Streamlit) estÃ¡ deprecado a partir de v2.5.0. Por favor utiliza localcode_server.py y frontend/dist/index.html.", DeprecationWarning, stacklevel=2)

# â”€â”€â”€ Soporte .env â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
session_manager.init_sessions_dir()

def _guardar_sesion_actual(session_id: str, name: str, messages: list):
    """Guarda los datos de la sesiÃ³n activa en disco."""
    if session_id:
        session_manager.save_session(session_id, {"id": session_id, "name": name, "messages": messages})

def _truncar_markdown(texto: str, max_chars: int = 400) -> str:
    """Comprime texto y asegura la validez de los bloques de cÃ³digo markdown."""
    if len(texto) <= max_chars:
        return texto
    truncado = texto[:max_chars]
    if truncado.count("```") % 2 != 0:
        truncado += "\n```"
    return truncado + "... [resumido]"

st.set_page_config(page_title="OpenCode Hub", page_icon="ðŸ’»", layout="wide")

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# INICIALIZACIÃ“N DE ESTADO
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "active_file" not in st.session_state:
    st.session_state.active_file = "README.md"


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# SIDEBAR: ConfiguraciÃ³n y Sesiones
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
with st.sidebar:
    st.header("âš™ï¸ ConfiguraciÃ³n del Hub")

    provider = "Ollama (Local)"
    st.info("ðŸ”’ Modo MODO LOCAL-ONLY Activo (0$ Costo - Sin Cloud)")
    model_name = st.selectbox(
        "Modelo Local",
        ["qwen2.5-coder:14b", "qwen2.5-coder:7b", "llama3.1:8b", "deepseek-coder:6.7b", "mistral", "gemma2"]
    )
    api_key = ""

    st.divider()

    from agents import get_available_agents

    st.header("ðŸ¤– Agente (Persona)")
    lista_agentes = ["Auto (Enrutador AutomÃ¡tico) ðŸŒŸ"] + get_available_agents()
    agent_type = st.selectbox("Seleccionar Agente", lista_agentes)

    st.divider()

    st.header("ðŸ› ï¸ Herramientas y Skills")
    if agent_type == "Auto (Enrutador AutomÃ¡tico) ðŸŒŸ":
        st.info("ðŸª„ En modo Auto, el Ruteador asignarÃ¡ las herramientas ideales automÃ¡ticamente.")
        selected_tools = []
    else:
        use_local_fs = st.checkbox("Archivos Locales (Leer/Escribir)", value=True)
        use_git = st.checkbox("Control de Versiones (Git)", value=True)
        use_terminal = st.checkbox("Terminal Integrada", value=True)
        use_db = st.checkbox("Base de Datos (SQLite)", value=False)
        use_github = st.checkbox("GitHub API", value=False)
        use_websearch = st.checkbox("BÃºsqueda Web (Google)", value=False)
        use_rag = st.checkbox("Memoria RAG (IndexaciÃ³n Local)", value=False)

        selected_tools = []
        if use_local_fs:
            selected_tools.append("Archivos Locales")
        if use_git:
            selected_tools.append("Git")
        if use_terminal:
            selected_tools.append("Terminal Integrada")
        if use_db:
            selected_tools.append("Base de Datos (SQLite)")
        if use_github:
            selected_tools.append("Github")
        if use_websearch:
            selected_tools.append("BÃºsqueda Web")
        if use_rag:
            selected_tools.append("Memoria RAG")

    st.divider()

    # â”€â”€ GestiÃ³n de Sesiones â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    st.header("ðŸ“ Sesiones")

    col_new, col_export = st.columns(2)
    with col_new:
        if st.button("âž• Nueva", use_container_width=True):
            new_id = session_manager.create_new_session("SesiÃ³n " + dt.now().strftime("%H:%M:%S"))
            st.session_state.current_session_id = new_id
            st.session_state.messages = []
            st.rerun()

    # BUG 4 FIX: funciÃ³n de cache con TTL corto para que se invalide automÃ¡ticamente
    def get_sessions_list():
        return session_manager.list_sessions()

    sesiones = get_sessions_list()
    sesiones_dict = {s["id"]: s.get("name", s.get("id", "SesiÃ³n Sin Nombre")) for s in sesiones if isinstance(s, dict) and "id" in s}

    if sesiones:
        index = 0
        if st.session_state.current_session_id in sesiones_dict:
            index = list(sesiones_dict.keys()).index(st.session_state.current_session_id)

        selected_session = st.selectbox(
            "Cambiar de SesiÃ³n",
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
            if st.button("ðŸ—‘ï¸ Borrar", use_container_width=True):
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
                    "ðŸ“¤ Exportar",
                    data=md,
                    file_name=f"{nombre[:20]}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
    else:
        sesiones_dict = {}

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# CREAR SESIÃ“N POR DEFECTO SI NO HAY NINGUNA
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if not st.session_state.current_session_id:
    new_id = session_manager.create_new_session("SesiÃ³n " + dt.now().strftime("%H:%M:%S"))
    st.session_state.current_session_id = new_id

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# MAIN UI & CLAUDE CODE 3-PANEL IDE LAYOUT
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.title("ðŸ’» CodeAgent Hub")
st.caption(f"ðŸ¤– **{agent_type}** Â· {provider} / `{model_name}` | `/help`, `/clear`, `/export`, `/status`")

# Botones de AcciÃ³n RÃ¡pida estilo CodeAgent
col_q1, col_q2, col_q3, col_q4 = st.columns(4)
action_prompt = None

with col_q1:
    if st.button("ðŸ” Explora Workspace", use_container_width=True):
        action_prompt = "@workspace Explora la estructura de archivos y tecnologÃ­as del proyecto actual."
with col_q2:
    if st.button("âœï¸ Sugiere Refactor", use_container_width=True):
        action_prompt = "Analiza el cÃ³digo del proyecto y propone refactorizaciones o mejoras de Clean Code."
with col_q3:
    if st.button("ðŸ§ª Correr Tests", use_container_width=True):
        action_prompt = "Ejecuta los tests unitarios del proyecto usando ejecutar_comando_terminal y reporta los resultados."
with col_q4:
    if st.button("ðŸ“Š Estado Git Diff", use_container_width=True):
        action_prompt = "Muestra el estado de git status y git diff de los archivos modificados."

# Paneles visuales si la persona elegida es CodeAgent Developer (o en vista IDE)
if agent_type in ("CodeAgent Developer", "Agente de EdiciÃ³n de CÃ³digo"):
    col_workspace, col_chat = st.columns([1, 1])

    with col_workspace:
        st.subheader("ðŸ“ Explorador y Visor de CÃ³digo")
        archivos_disponibles = []
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', 'venv', '.venv', 'chroma_db', 'graphify-out']]
            for file in files:
                if file.endswith(('.py', '.md', '.json', '.txt', '.yml', '.yaml', '.sh', '.bat', '.toml')):
                    rel_path = os.path.relpath(os.path.join(root, file), ".")
                    archivos_disponibles.append(rel_path)

        archivos_disponibles.sort()
        if archivos_disponibles:
            selected_file = st.selectbox("Archivo Activo", archivos_disponibles, index=0 if st.session_state.active_file not in archivos_disponibles else archivos_disponibles.index(st.session_state.active_file))
            st.session_state.active_file = selected_file

            if os.path.exists(selected_file):
                with open(selected_file, encoding='utf-8', errors='replace') as f:
                    content = f.read(10000)
                st.caption(f"ðŸ“„ Vendo `{selected_file}` ({len(content)} caracteres)")
                st.code(content, language="python" if selected_file.endswith(".py") else "markdown")

    with col_chat:
        st.subheader("ðŸ’¬ Chat con Asistente")
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                if msg.get("time"):
                    st.caption(f"ðŸ•’ {msg['time']}")
                st.markdown(msg["content"])
else:
    # Mostrar historial de la sesiÃ³n actual en vista completa
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("time"):
                st.caption(f"ðŸ•’ {msg['time']}")
            st.markdown(msg["content"])

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# CAPTURA DE INPUT
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
chat_input_prompt = st.chat_input(f"Escribe tu peticiÃ³n a {agent_type} (/help para comandos)")
prompt = action_prompt or chat_input_prompt


if prompt:
    # â”€â”€ Slash Commands â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if prompt.strip().startswith("/"):
        comando = prompt.strip().lower()

        if comando == "/help":
            ayuda = (
                "**Comandos Disponibles:**\n"
                "- `/help` â€” Muestra esta ayuda\n"
                "- `/clear` â€” Borra el historial de la sesiÃ³n actual\n"
                "- `/export` â€” Exporta la sesiÃ³n como Markdown\n"
                "- `/status` â€” Muestra la configuraciÃ³n activa\n\n"
                "*Tip:* Usa `@workspace` en tu mensaje para que el agente analice la estructura del proyecto automÃ¡ticamente."
            )
            st.session_state.messages.append({"role": "assistant", "content": ayuda, "time": dt.now().strftime("%H:%M:%S")})
            session_manager.save_session(
                st.session_state.current_session_id,
                {"id": st.session_state.current_session_id, "name": sesiones_dict.get(st.session_state.current_session_id, "SesiÃ³n"), "messages": st.session_state.messages}
            )
            st.rerun()

        elif comando == "/clear":
            st.session_state.messages = []
            session_manager.save_session(
                st.session_state.current_session_id,
                {"id": st.session_state.current_session_id, "name": sesiones_dict.get(st.session_state.current_session_id, "SesiÃ³n"), "messages": []}
            )
            st.rerun()

        elif comando == "/status":
            status = (
                f"**ConfiguraciÃ³n Activa:**\n"
                f"- ðŸ¤– Agente: `{agent_type}`\n"
                f"- â˜ï¸ Proveedor: `{provider}`\n"
                f"- ðŸ§  Modelo: `{model_name}`\n"
                f"- ðŸ› ï¸ Herramientas: `{', '.join(selected_tools) or 'Ninguna (modo chat)'}`\n"
                f"- ðŸ“ Directorio: `{os.getcwd()}`\n"
                f"- ðŸ’¬ Mensajes en sesiÃ³n: `{len(st.session_state.messages)}`"
            )
            st.session_state.messages.append({"role": "assistant", "content": status, "time": dt.now().strftime("%H:%M:%S")})
            st.rerun()

        elif comando == "/export":
            md = session_manager.export_session_to_markdown(st.session_state.current_session_id)
            st.session_state.messages.append({
                "role": "assistant",
                "content": "ðŸ“¤ SesiÃ³n lista para exportar. Usa el botÃ³n **Exportar** en el sidebar.",
                "time": dt.now().strftime("%H:%M:%S")
            })
            st.rerun()

        else:
            st.warning(f"Comando desconocido: `{comando}`. Escribe `/help` para ver los comandos.")

    # â”€â”€ Flujo normal de chat â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    else:
        timestamp = dt.now().strftime("%H:%M:%S")
        st.session_state.messages.append({"role": "user", "content": prompt, "time": timestamp})

        with st.chat_message("user"):
            st.caption(f"ðŸ•’ {timestamp}")
            st.markdown(prompt)

        with st.chat_message("assistant"):
            respuesta = ""
            metricas = {"tiempo_segundos": 0, "agentes_usados": "-", "herramientas_activas": 0}

            # BUG 3 FIX: construir el prompt correcto
            # Solo el prompt actual + contexto comprimido del historial reciente
            historial_reciente = st.session_state.messages[-7:-1]  # Ãºltimos 7 mensajes, sin el actual
            if historial_reciente:
                contexto_historial = "## Historial reciente de la conversaciÃ³n\n"
                for m in historial_reciente:
                    role_label = "Usuario" if m["role"] == "user" else "Asistente"
                    # Comprimir respuestas largas del asistente
                    contenido = m["content"]
                    if m["role"] == "assistant":
                        contenido = _truncar_markdown(m["content"], 400)
                    contexto_historial += f"**{role_label}:** {contenido}\n\n"
                prompt_final = f"{contexto_historial}\n---\n\n## PeticiÃ³n actual del usuario\n{prompt}"
            else:
                prompt_final = prompt

            # Inyectar contexto @workspace si se menciona
            if "@workspace" in prompt.lower() or "analiza este proyecto" in prompt.lower():
                contexto_ws = obtener_contexto_workspace()
                prompt_final = f"{contexto_ws}\n\n{prompt_final}"

            status_placeholder = st.empty()
            response_placeholder = st.empty()

            with st.spinner(f"ðŸ§  {agent_type} ({provider}/{model_name}) procesando..."):
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
                    respuesta = f"âŒ **Error de ejecuciÃ³n:**\n```\n{e}\n```"
                    st.error(respuesta)

                finally:
                    ts_resp = dt.now().strftime("%H:%M:%S")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": respuesta,
                        "time": ts_resp
                    })

                    # Auto-nombrar la sesiÃ³n con el primer mensaje
                    nombre_sesion = sesiones_dict.get(st.session_state.current_session_id, "SesiÃ³n")
                    if len(st.session_state.messages) <= 2:
                        nombre_sesion = prompt[:30].strip() + "..."

                    # Guardar sesiÃ³n en disco
                    session_manager.save_session(
                        st.session_state.current_session_id,
                        {
                            "id": st.session_state.current_session_id,
                            "name": nombre_sesion,
                            "messages": st.session_state.messages
                        }
                    )

            # Panel de mÃ©tricas
            if metricas.get("tiempo_segundos"):
                with st.expander("ðŸ“Š MÃ©tricas de EjecuciÃ³n", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("â±ï¸ Tiempo", f"{metricas['tiempo_segundos']}s")
                    col2.metric("ðŸ¤– Agente", metricas.get("agentes_usados", "-").split("(")[-1].rstrip(")"))
                    col3.metric("ðŸ› ï¸ Herramientas", metricas.get("herramientas_activas", 0))

