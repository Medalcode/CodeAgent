import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from ..storage.database import DatabaseManager, get_db_manager


@dataclass
class Event:
    task_id: str
    event_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    event_id: int | None = None


class EventBus:
    """Bus de eventos persistente con patrón Observador (Event Sourcing)."""

    def __init__(self, db_manager: DatabaseManager | None = None):
        self.db = db_manager or get_db_manager()
        self._listeners: list[Callable[[Event], None]] = []
        self._lock = threading.Lock()

    def subscribe(self, listener: Callable[[Event], None]) -> None:
        """Registra un callback de escucha de eventos en tiempo real."""
        with self._lock:
            if listener not in self._listeners:
                self._listeners.append(listener)

    def unsubscribe(self, listener: Callable[[Event], None]) -> None:
        """Elimina un callback de escucha."""
        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)

    def publish(self, task_id: str, event_type: str, payload: dict[str, Any] | None = None) -> Event:
        """Persiste el evento en SQLite y notifica a todos los suscriptores activos."""
        payload = payload or {}
        event_id = self.db.record_event(task_id, event_type, payload)
        event = Event(
            task_id=task_id,
            event_type=event_type,
            payload=payload,
            timestamp=time.time(),
            event_id=event_id
        )

        with self._lock:
            listeners_copy = list(self._listeners)

        for listener in listeners_copy:
            try:
                listener(event)
            except Exception as e:
                logging.error(f"❌ Error en suscriptor de EventBus ({event_type}): {e}")

        return event

    def get_events(self, task_id: str, since_id: int = 0) -> list[dict[str, Any]]:
        """Obtiene la corriente de eventos guardados para reconstruir el estado visual en la UI."""
        return self.db.get_task_events(task_id, since_id=since_id)


_global_event_bus: EventBus | None = None

def get_event_bus() -> EventBus:
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus
