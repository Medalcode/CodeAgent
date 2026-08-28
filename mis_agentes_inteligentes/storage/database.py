import json
import os
import sqlite3
import threading
import time
from typing import Any

DB_FILE_PATH = os.getenv("CODEAGENT_DB_PATH", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codeagent_desktop.db"))
_DB_LOCK = threading.Lock()


class DatabaseManager:
    """Gestor de almacenamiento persistente SQLite multihilo seguro para CodeAgent v6.0."""

    def __init__(self, db_path: str = DB_FILE_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        # WAL mode para lecturas y escrituras multihilo no bloqueantes
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self) -> None:
        with _DB_LOCK, self._get_connection() as conn:
            cursor = conn.cursor()

            # Tabla de Tareas
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                project_path TEXT NOT NULL,
                goal TEXT NOT NULL,
                execution_level TEXT NOT NULL,
                status TEXT NOT NULL,
                current_state TEXT NOT NULL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            );
            """)

            # Tabla de Checkpoints de Estado
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                state TEXT NOT NULL,
                plan TEXT,
                failed_verification_json TEXT,
                replans_count INTEGER DEFAULT 0,
                created_at REAL NOT NULL,
                FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
            );
            """)

            # Tabla de Eventos (Event Sourcing Stream)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                timestamp REAL NOT NULL,
                FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
            );
            """)

            # Tabla de Métricas Cuantitativas
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                metric_key TEXT NOT NULL,
                metric_value REAL NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
            );
            """)

            conn.commit()

    # --- OPERACIONES DE TAREAS ---
    def create_task(self, task_id: str, project_path: str, goal: str, execution_level: str) -> dict[str, Any]:
        now = time.time()
        with _DB_LOCK, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO tasks (id, project_path, goal, execution_level, status, current_state, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'CREATED', 'INIT', ?, ?)
                """,
                (task_id, project_path, goal, execution_level, now, now)
            )
            conn.commit()
        return self.get_task(task_id)

    def update_task_status(self, task_id: str, status: str, current_state: str | None = None) -> None:
        now = time.time()
        with _DB_LOCK, self._get_connection() as conn:
            cursor = conn.cursor()
            if current_state:
                cursor.execute(
                    "UPDATE tasks SET status = ?, current_state = ?, updated_at = ? WHERE id = ?",
                    (status, current_state, now, task_id)
                )
            else:
                cursor.execute(
                    "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
                    (status, now, task_id)
                )
            conn.commit()

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return dict(row)

    def list_tasks(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    # --- OPERACIONES DE CHECKPOINTS ---
    def save_checkpoint(self, task_id: str, state: str, plan: str | None, failed_verification: dict | None, replans_count: int) -> int:
        now = time.time()
        failed_json = json.dumps(failed_verification, ensure_ascii=False) if failed_verification else None
        with _DB_LOCK, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO checkpoints (task_id, state, plan, failed_verification_json, replans_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (task_id, state, plan, failed_json, replans_count, now)
            )
            conn.commit()
            return cursor.lastrowid

    def get_latest_checkpoint(self, task_id: str) -> dict[str, Any] | None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM checkpoints WHERE task_id = ? ORDER BY id DESC LIMIT 1", (task_id,))
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            if data.get("failed_verification_json"):
                try:
                    data["failed_verification"] = json.loads(data["failed_verification_json"])
                except Exception:
                    data["failed_verification"] = None
            return data

    # --- OPERACIONES DE EVENTOS (EVENT SOURCING) ---
    def record_event(self, task_id: str, event_type: str, payload: dict[str, Any]) -> int:
        now = time.time()
        payload_json = json.dumps(payload, ensure_ascii=False)
        with _DB_LOCK, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO events (task_id, event_type, payload_json, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (task_id, event_type, payload_json, now)
            )
            conn.commit()
            return cursor.lastrowid

    def get_task_events(self, task_id: str, since_id: int = 0) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM events WHERE task_id = ? AND id > ? ORDER BY id ASC",
                (task_id, since_id)
            )
            rows = cursor.fetchall()
            events = []
            for r in rows:
                item = dict(r)
                try:
                    item["payload"] = json.loads(item["payload_json"])
                except Exception:
                    item["payload"] = {}
                events.append(item)
            return events


_global_db_manager: DatabaseManager | None = None

def get_db_manager() -> DatabaseManager:
    global _global_db_manager
    if _global_db_manager is None:
        _global_db_manager = DatabaseManager()
    return _global_db_manager
