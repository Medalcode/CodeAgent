import streamlit as st
import os
import contextlib
from datetime import datetime
import session_manager
from main import ejecutar_agentes

os.chdir(os.path.dirname(os.path.abspath(__file__)))
session_manager.init_sessions_dir()

st.set_page_config(page_title="OpenCode Hub", page_icon="💻", layout="wide")

# Inicialización de estado de la app
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR: Configuración y Sesiones ---
with st.sidebar:
    st.header("⚙️ Configuración del Hub")
    
    provider = st.selectbox("Proveedor de IA", ["Ollama (Local)", "OpenAI", "Anthropic", "Groq", "Gemini (Google)"])
    
    # Modelos dinámicos
    if provider == "Ollama (Local)":
        model_name = st.selectbox("Modelo", ["qwen2.5-coder:7b", "qwen2.5-coder:14b", "llama3.1:8b", "mistral", "gemma2", "qwen2"])
        api_key = ""
    elif provider == "OpenAI":
        model_name = st.selectbox("Modelo", ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"])
        api_key = st.text_input("API Key", type="password", help="Tu API Key de OpenAI")
    elif provider == "Anthropic":
        model_name = st.selectbox("Modelo", ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229"])
        api_key = st.text_input("API Key", type="password", help="Tu API Key de Anthropic")
    elif provider == "Groq":
        model_name = st.selectbox("Modelo", ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"])
        api_key = st.text_input("API Key", type="password", help="Tu API Key de Groq")
    elif provider == "Gemini (Google)":
        model_name = st.selectbox("Modelo", ["gemini-1.5-pro", "gemini-1.5-flash"])
        api_key = st.text_input("API Key", type="password", help="Tu API Key de Google")
        
    st.divider()
    
    from agents import get_available_agents
    
    st.header("🤖 Agente (Persona)")
    
    # Cargamos dinámicamente los agentes (tanto fijos como subagentes markdown)
    lista_agentes = ["Auto (Enrutador Automático) 🌟"] + get_available_agents()
    agent_type = st.selectbox("Seleccionar Agente", lista_agentes)
    
    st.divider()
    
    st.header("🛠️ Herramientas y Skills")
    if agent_type == "Auto (Enrutador Automático) 🌟":
        st.info("🪄 En modo Auto, el Ruteador asignará las herramientas ideales automáticamente según tu petición.")
        selected_tools = []
    else:
        use_local_fs = st.checkbox("Archivos Locales (Leer/Escribir)", value=True, help="Permite al agente modificar código en tu PC")
        use_terminal = st.checkbox("Terminal Integrada", value=True, help="Permite al agente ejecutar comandos en tu PC")
        use_db = st.checkbox("Base de Datos (SQLite)", value=False)
        use_github = st.checkbox("GitHub API", value=False)
        use_websearch = st.checkbox("Búsqueda Web (Google)", value=False, help="Permite al agente buscar info en internet (Fase 4)")
        use_rag = st.checkbox("Memoria RAG (Indexación Local)", value=False, help="Indexa y busca semánticamente en repositorios grandes (Fase 4)")
        
        selected_tools = []
        if use_local_fs: selected_tools.append("Archivos Locales")
        if use_terminal: selected_tools.append("Terminal Integrada")
        if use_db: selected_tools.append("Base de Datos (SQLite)")
        if use_github: selected_tools.append("GitHub API")
        if use_websearch: selected_tools.append("Búsqueda Web")
        if use_rag: selected_tools.append("Memoria RAG")
    
    st.divider()
    
    st.header("📁 Sesiones")
    if st.button("➕ Nueva Sesión"):
        new_id = session_manager.create_new_session("Sesión " + str(datetime.now().strftime("%H:%M:%S")))
        st.session_state.current_session_id = new_id
        st.session_state.messages = []
        st.rerun()

    sesiones = session_manager.list_sessions()
    sesiones_dict = {s["id"]: s["name"] for s in sesiones}
    
    if sesiones:
        # Encontrar el índice de la sesión actual
        index = 0
        if st.session_state.current_session_id in sesiones_dict:
            index = list(sesiones_dict.keys()).index(st.session_state.current_session_id)
            
        selected_session = st.selectbox("Cambiar de Sesión", options=list(sesiones_dict.keys()), format_func=lambda x: sesiones_dict[x], index=index)
        
        if selected_session != st.session_state.current_session_id:
            st.session_state.current_session_id = selected_session
            s_data = session_manager.load_session(selected_session)
            st.session_state.messages = s_data["messages"] if s_data else []
            st.rerun()
            
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Borrar Sesión"):
                session_manager.delete_session(st.session_state.current_session_id)
                st.session_state.current_session_id = None
                st.session_state.messages = []
                st.rerun()

# Si no hay sesión activa, crear una por defecto
if not st.session_state.current_session_id:
    new_id = session_manager.create_new_session("Sesión " + str(datetime.now().strftime("%H:%M:%S")))
    st.session_state.current_session_id = new_id

# --- MAIN UI ---
st.title("💻 OpenCode Hub")
st.caption("Comandos disponibles: `/help`, `/clear` | Configura el modelo, el agente y los Skills en la barra lateral.")

# Mostrar historial de la sesión actual
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Captura de input principal
prompt = st.chat_input("Escribe tu petición aquí (ej. /help para comandos)")

if prompt:
    # 1. Interceptar Slash Commands
    if prompt.strip().startswith("/"):
        comando = prompt.strip().lower()
        if comando == "/help":
            ayuda = "**Comandos Disponibles:**\n- `/help`: Muestra esta ayuda.\n- `/clear`: Borra el historial de la sesión actual.\n\n*Tip:* Utiliza la **Barra Lateral (Sidebar)** para cambiar de agentes, modelos de IA, proveedores o inyectar tus API Keys."
            st.session_state.messages.append({"role": "assistant", "content": ayuda})
            session_manager.save_session(st.session_state.current_session_id, {"id": st.session_state.current_session_id, "name": sesiones_dict.get(st.session_state.current_session_id, "Sesión"), "messages": st.session_state.messages})
            st.rerun()
        elif comando == "/clear":
            st.session_state.messages = []
            session_manager.save_session(st.session_state.current_session_id, {"id": st.session_state.current_session_id, "name": sesiones_dict.get(st.session_state.current_session_id, "Sesión"), "messages": []})
            st.rerun()
        else:
            st.warning(f"Comando desconocido: {comando}. Escribe `/help` para ver los comandos.")
    
    # 2. Flujo normal de chat (Enviar al Agente)
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner(f"🧠 {agent_type} pensando con {provider} ({model_name})..."):
                try:
                    historial_texto = "Historial de la conversación:\n"
                    for m in st.session_state.messages:
                        historial_texto += f"{m['role'].upper()}: {m['content']}\n"
                    
                    with open(os.devnull, 'w') as devnull:
                        with contextlib.redirect_stdout(devnull):
                            respuesta = ejecutar_agentes(
                                user_prompt=historial_texto,
                                provider=provider,
                                model_name=model_name,
                                api_key=api_key,
                                agent_type=agent_type,
                                selected_tools=selected_tools
                            )
                    
                    st.markdown(respuesta)
                    st.session_state.messages.append({"role": "assistant", "content": respuesta})
                    
                    # Generar nombre automático para la sesión si es el primer mensaje
                    nombre_sesion = sesiones_dict.get(st.session_state.current_session_id, "Sesión")
                    if len(st.session_state.messages) <= 2:  # Solo 1 par de mensajes
                        nombre_sesion = prompt[:20] + "..."
                        
                    # Guardar sesión en disco
                    session_manager.save_session(
                        st.session_state.current_session_id, 
                        {"id": st.session_state.current_session_id, "name": nombre_sesion, "messages": st.session_state.messages}
                    )
                    
                except Exception as e:
                    # Capturar errores si faltan API keys o no hay conexión
                    error_msg = f"**Error de ejecución:** {e}\n\n*Asegúrate de haber introducido tu API Key si no estás usando Ollama local.*"
                    st.error(error_msg)
