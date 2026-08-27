import json
import logging
import os
import tempfile
import uuid
from abc import ABC, abstractmethod
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSIONS_DIR = os.path.join(BASE_DIR, "sesiones")


class BaseSessionRepository(ABC):
    """Interfaz abstracta para la gestión de sesiones de chat (Patrón Repositorio)."""

    @abstractmethod
    def create_session(self, name: str = "Nueva Sesión") -> str:
        pass

    @abstractmethod
    def load_session(self, session_id: str) -> dict | None:
        pass

    @abstractmethod
    def save_session(self, session_id: str, data: dict) -> None:
        pass

    @abstractmethod
    def list_sessions(self) -> list:
        pass

    @abstractmethod
    def delete_session(self, session_id: str) -> None:
        pass


class JSONSessionRepository(BaseSessionRepository):
    """Adaptador de persistencia basado en archivos JSON locales en disco."""

    def __init__(self, sessions_dir: str | None = None):
        self._sessions_dir = sessions_dir
        self._init_dir()

    @property
    def sessions_dir(self) -> str:
        return self._sessions_dir or SESSIONS_DIR

    def _init_dir(self):
        if not os.path.exists(self.sessions_dir):
            os.makedirs(self.sessions_dir)

    def create_session(self, name: str = "Nueva Sesión") -> str:
        self._init_dir()
        session_id = str(uuid.uuid4())
        session_data = {
            "id": session_id,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "messages": [],
            "memory": {
                "factual": "Proyecto CodeAgent v3.0 Enterprise (Python, smolagents, LiteLLM, localcode_server).",
                "decisions": ["Arquitectura ReAct basada en smolagents", "Verificación obligatoria AST/Tests/Ruff"],
                "working": {"active_task": "", "modified_files": [], "pending_checklist": []}
            }
        }
        self.save_session(session_id, session_data)
        return session_id

    def load_session(self, session_id: str) -> dict | None:
        if not session_id:
            return None
        self._init_dir()
        filepath = os.path.join(self.sessions_dir, f"{session_id}.json")
        if os.path.exists(filepath):
            with open(filepath, encoding="utf-8") as f:
                return json.load(f)
        return None

    def save_session(self, session_id: str, data: dict) -> None:
        if not session_id:
            return
        self._init_dir()
        filepath = os.path.join(self.sessions_dir, f"{session_id}.json")
        with tempfile.NamedTemporaryFile("w", dir=self.sessions_dir, delete=False, encoding="utf-8") as tf:
            json.dump(data, tf, indent=4, ensure_ascii=False)
            temp_name = tf.name
        os.replace(temp_name, filepath)

    def list_sessions(self) -> list:
        self._init_dir()
        sessions = []
        for file in os.listdir(self.sessions_dir):
            if file.endswith(".json"):
                filepath = os.path.join(self.sessions_dir, file)
                try:
                    with open(filepath, encoding="utf-8") as f:
                        data = json.load(f)
                        sessions.append(data)
                except Exception as e:
                    logging.warning(f"Error cargando sesión desde {file}: {e}")
        sessions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return sessions

    def delete_session(self, session_id: str) -> None:
        if not session_id:
            return
        filepath = os.path.join(self.sessions_dir, f"{session_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)


# Singleton del repositorio por defecto
_default_repo = JSONSessionRepository()


def init_sessions_dir():
    _default_repo._init_dir()


def create_new_session(name="Nueva Sesión"):
    return _default_repo.create_session(name)


def list_sessions():
    return _default_repo.list_sessions()


def load_session(session_id):
    return _default_repo.load_session(session_id)


def save_session(session_id, data):
    _default_repo.save_session(session_id, data)


def delete_session(session_id):
    _default_repo.delete_session(session_id)


def rename_session(session_id, new_name: str):
    data = load_session(session_id)
    if data:
        data["name"] = new_name
        save_session(session_id, data)


def export_session_to_markdown(session_id) -> str:
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
