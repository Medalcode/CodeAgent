import json
import logging
import os
import tempfile
import uuid
import warnings
from abc import ABC, abstractmethod
from datetime import datetime

warnings.warn(
    "session_manager.py JSON persistence is deprecated. Use DatabaseManager (storage/database.py) for canonical session/checkpoint storage.",
    DeprecationWarning,
    stacklevel=2,
)

# ─────────────────────────────────────────────────────────────────────────────
# C3.1 PERSISTENCE CANONICALIZATION — LEGACY SESSION COMPATIBILITY NOTICE
# ─────────────────────────────────────────────────────────────────────────────
# Este módulo (session_manager.py) está clasificado como LEGACY SESSION COMPATIBILITY.
# NO es el Source of Truth primario para sesiones/checkpoints.
#
# Autoridad canónica (DRIFT-01 fix):
#   DatabaseManager / SQLite = SOURCE OF TRUTH
#   session_manager / JSON   = LEGACY FALLBACK / MIGRATION / COMPATIBILITY ONLY
#
# APIs deprecadas para uso como autoridad primaria:
#   - create_new_session()     → Use DatabaseManager.create_task()
#   - load_session()           → Use DatabaseManager.get_task() + get_latest_checkpoint()
#   - save_session()           → Use DatabaseManager.save_checkpoint() + update_task_status()
#   - list_sessions()          → Use DatabaseManager.list_tasks()
#   - delete_session()         → Use DatabaseManager (soft delete via status)
#   - rename_session()         → Use DatabaseManager.update_task() (no implementado)
#   - export_session_to_markdown() → Legacy export only
#
# Estas funciones se mantienen SOLO para:
#   1. Compatibilidad con localcode_server.py endpoints (fase C3.2+)
#   2. Migración explícita JSON → SQLite (resume_session)
#   3. LEGACY EXPORT desde _save_checkpoint (marcado con _legacy_export=True)
# ─────────────────────────────────────────────────────────────────────────────

import platform

def _resolve_default_sessions_dir(base_dir: str) -> str:
    env_path = os.getenv("CODEAGENT_SESSIONS_DIR")
    if env_path:
        return env_path
        
    repo_root = os.path.dirname(base_dir)
    if os.path.exists(os.path.join(repo_root, ".git")) or os.path.exists(os.path.join(repo_root, "AGENTS.md")):
        return os.path.join(base_dir, "sesiones")

    if platform.system() == "Windows":
        appdata = os.environ.get("APPDATA") or os.path.expanduser("~\\AppData\\Roaming")
        target_dir = os.path.join(appdata, "CodeAgent", "sesiones")
    elif platform.system() == "Darwin":
        target_dir = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "CodeAgent", "sesiones")
    else:
        target_dir = os.path.join(os.path.expanduser("~"), ".config", "CodeAgent", "sesiones")

    os.makedirs(target_dir, exist_ok=True)
    return target_dir

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSIONS_DIR = _resolve_default_sessions_dir(BASE_DIR)


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
            try:
                with open(filepath, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return None
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
    """LEGACY: Inicializa directorio de sesiones JSON. Use DatabaseManager para almacenamiento canónico."""
    _default_repo._init_dir()


def create_new_session(name="Nueva Sesión"):
    """LEGACY SESSION COMPATIBILITY: Crea sesión JSON.
    
    DEPRECATED como autoridad primaria. Use DatabaseManager.create_task() para 
    creación canónica de tareas en SQLite (Source of Truth).
    """
    return _default_repo.create_session(name)


def list_sessions():
    """LEGACY SESSION COMPATIBILITY: Lista sesiones JSON.
    
    DEPRECATED como autoridad primaria. Use DatabaseManager.list_tasks() para 
    listado canónico desde SQLite (Source of Truth).
    """
    return _default_repo.list_sessions()


def load_session(session_id):
    """LEGACY SESSION COMPATIBILITY: Carga sesión JSON.
    
    DEPRECATED como autoridad primaria. Use DatabaseManager.get_task() + 
    get_latest_checkpoint() para carga canónica desde SQLite (Source of Truth).
    
    Esta función se mantiene SOLO para:
      1. Migración explícita JSON → SQLite en resume_session()
      2. Compatibilidad temporal con localcode_server.py endpoints
    """
    return _default_repo.load_session(session_id)


def save_session(session_id, data):
    """LEGACY SESSION COMPATIBILITY: Guarda sesión JSON.
    
    DEPRECATED como autoridad primaria. Use DatabaseManager.save_checkpoint() + 
    update_task_status() para persistencia canónica en SQLite (Source of Truth).
    
    Esta función se mantiene SOLO para:
      1. LEGACY EXPORT desde _save_checkpoint() (marcado _legacy_export=True)
      2. Compatibilidad temporal con localcode_server.py endpoints
    """
    _default_repo.save_session(session_id, data)


def delete_session(session_id):
    """LEGACY SESSION COMPATIBILITY: Elimina sesión JSON.
    
    DEPRECATED como autoridad primaria. Use DatabaseManager con soft-delete 
    via status (CANCELLED/PAUSED) para gestión canónica en SQLite.
    """
    _default_repo.delete_session(session_id)


def rename_session(session_id, new_name: str):
    """LEGACY SESSION COMPATIBILITY: Renombra sesión JSON.
    
    DEPRECATED como autoridad primaria. No hay equivalente directo en 
    DatabaseManager; use update_task_status() con metadata si necesario.
    """
    data = load_session(session_id)
    if data:
        data["name"] = new_name
        save_session(session_id, data)


def export_session_to_markdown(session_id) -> str:
    """LEGACY SESSION COMPATIBILITY: Exporta sesión JSON a Markdown.
    
    Función de utilidad legacy. No tiene equivalente en DatabaseManager.
    """
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
