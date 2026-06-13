import os
import json
import uuid
from datetime import datetime

SESSIONS_DIR = "sesiones"

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
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    sessions.append(data)
            except:
                pass
    # Ordenar por fecha de creación descendente
    sessions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return sessions

def load_session(session_id):
    init_sessions_dir()
    filepath = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_session(session_id, data):
    init_sessions_dir()
    filepath = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def delete_session(session_id):
    filepath = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
