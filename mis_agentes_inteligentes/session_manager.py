import json
import logging
import os
import tempfile
import uuid
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSIONS_DIR = os.path.join(BASE_DIR, "sesiones")


def init_sessions_dir():
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR)


def create_new_session(name="Nueva Sesión"):
    init_sessions_dir()
    session_id = str(uuid.uuid4())
    session_data = {
        "id": session_id,
        "name": name,
        "created_at": datetime.now().isoformat(),
        "messages": []
    }
    save_session(session_id, session_data)
    return session_id


def list_sessions():
    init_sessions_dir()
    sessions = []
    for file in os.listdir(SESSIONS_DIR):
        if file.endswith(".json"):
            filepath = os.path.join(SESSIONS_DIR, file)
            try:
                with open(filepath, encoding="utf-8") as f:
                    data = json.load(f)
                    sessions.append(data)
            except Exception as e:
                logging.warning(f"Error cargando sesión desde {file}: {e}")
    # Ordenar por fecha de creación descendente
    sessions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return sessions


def load_session(session_id):
    if not session_id:
        return None
    init_sessions_dir()
    filepath = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    if os.path.exists(filepath):
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    return None


def save_session(session_id, data):
    if not session_id:
        return
    init_sessions_dir()
    filepath = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    with tempfile.NamedTemporaryFile("w", dir=SESSIONS_DIR, delete=False, encoding="utf-8") as tf:
        json.dump(data, tf, indent=4, ensure_ascii=False)
        temp_name = tf.name
    os.replace(temp_name, filepath)


def delete_session(session_id):
    """BUG 5 FIX: protegido contra session_id None o inválido."""
    if not session_id:
        return
    filepath = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)


def rename_session(session_id, new_name: str):
    """Renombra una sesión existente."""
    data = load_session(session_id)
    if data:
        data["name"] = new_name
        save_session(session_id, data)


def export_session_to_markdown(session_id) -> str:
    """Exporta una sesión como texto Markdown."""
    data = load_session(session_id)
    if not data:
        return ""
    lines = [f"# Sesión: {data.get('name', 'Sin nombre')}\n"]
    lines.append(f"*Creada: {data.get('created_at', '')}*\n\n---\n")
    for msg in data.get("messages", []):
        role = "👤 Usuario" if msg["role"] == "user" else "🤖 Asistente"
        time_str = f" _{msg.get('time', '')}_" if msg.get("time") else ""
        lines.append(f"### {role}{time_str}\n\n{msg['content']}\n\n---\n")
    return "\n".join(lines)
