import logging
import os
import threading
import uuid
from collections.abc import Callable
from typing import Any

from runtime.event_bus import EventBus, get_event_bus
from storage.database import DatabaseManager, get_db_manager


class CodeAgentRuntime:
    """Motor de ejecución autónomo desacoplado para CodeAgent v6.0.
    Permite iniciar, pausar, reanudar y consultar tareas agénticas sin depender de la UI.
    """

    def __init__(self, db_manager: DatabaseManager | None = None, event_bus: EventBus | None = None):
        self.db = db_manager or get_db_manager()
        self.event_bus = event_bus or get_event_bus()
        self._active_threads: dict[str, threading.Thread] = {}
        self._stop_flags: dict[str, threading.Event] = {}

    def start_task(self, goal: str, project_path: str = ".", agent_runner: Callable[[str], str] | None = None) -> str:
        """Inicia una nueva tarea agéntica de forma asíncrona y la registra en SQLite."""
        task_id = str(uuid.uuid4())
        abs_project = os.path.abspath(project_path)

        # Importar dinámicamente para evitar dependencias circulares
        from agent_pipeline import AgentStateMachineController

        controller = AgentStateMachineController(workspace_dir=abs_project)
        level = controller.infer_execution_level(goal)

        # Crear registro en SQLite
        self.db.create_task(task_id, abs_project, goal, level.value)
        self.event_bus.publish(task_id, "TASK_CREATED", {
            "task_id": task_id,
            "goal": goal,
            "project_path": abs_project,
            "execution_level": level.value
        })

        stop_event = threading.Event()
        self._stop_flags[task_id] = stop_event

        thread = threading.Thread(
            target=self._run_task_worker,
            args=(task_id, goal, abs_project, level, agent_runner, stop_event),
            daemon=True,
            name=f"CodeAgentWorker-{task_id[:8]}"
        )
        self._active_threads[task_id] = thread
        thread.start()

        return task_id

    def _run_task_worker(self, task_id: str, goal: str, project_path: str, level: Any, agent_runner: Callable[[str], str] | None, stop_event: threading.Event) -> None:
        self.db.update_task_status(task_id, "RUNNING", current_state="PLAN")
        self.event_bus.publish(task_id, "STATE_CHANGED", {"state": "PLAN", "status": "RUNNING"})

        try:
            from agent_pipeline import AgentStateMachineController

            controller = AgentStateMachineController(workspace_dir=project_path)

            def event_aware_runner(prompt: str) -> str:
                self.event_bus.publish(task_id, "TOOL_EXECUTED", {"prompt": prompt[:120]})
                if agent_runner:
                    return agent_runner(prompt)

                # Fallback al ejecutor smolagents / litellm por defecto
                try:
                    from tools import agente_desarrollador_codeagent
                    res = agente_desarrollador_codeagent.run(prompt)
                    return str(res)
                except Exception as ex:
                    return f"Respuesta de ejecución: {ex}"

            output_text, metrics = controller.run(
                user_goal=goal,
                agent_runner=event_aware_runner,
                level=level,
                session_id=task_id
            )

            if stop_event.is_set():
                self.db.update_task_status(task_id, "CANCELLED", current_state="DONE")
                self.event_bus.publish(task_id, "TASK_CANCELLED", {"task_id": task_id})
                return

            # Guardar checkpoint final y evento de completado
            self.db.save_checkpoint(task_id, "DONE", plan=output_text, failed_verification=None, replans_count=metrics.get("replans_count", 0))
            self.db.update_task_status(task_id, "COMPLETED", current_state="DONE")
            self.event_bus.publish(task_id, "TASK_COMPLETED", {
                "task_id": task_id,
                "output": output_text,
                "metrics": metrics
            })

        except Exception as e:
            logging.error(f"❌ Error durante ejecución de tarea {task_id}: {e}", exc_info=True)
            self.db.update_task_status(task_id, "FAILED", current_state="DONE")
            self.event_bus.publish(task_id, "TASK_FAILED", {"task_id": task_id, "error": str(e)})

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        """Obtiene la información de la tarea, su estado actual y el último checkpoint."""
        task = self.db.get_task(task_id)
        if not task:
            return None
        checkpoint = self.db.get_latest_checkpoint(task_id)
        task["checkpoint"] = checkpoint
        return task

    def list_tasks(self, limit: int = 20) -> list[dict[str, Any]]:
        """Lista las tareas recientes guardadas en SQLite."""
        return self.db.list_tasks(limit=limit)

    def pause_task(self, task_id: str) -> bool:
        """Pausa una tarea activa."""
        if task_id in self._stop_flags:
            self._stop_flags[task_id].set()
            self.db.update_task_status(task_id, "PAUSED")
            self.event_bus.publish(task_id, "TASK_PAUSED", {"task_id": task_id})
            return True
        return False

    def resume_task(self, task_id: str, agent_runner: Callable[[str], str] | None = None) -> bool:
        """Reanuda una tarea desde su último checkpoint en SQLite."""
        task = self.get_task(task_id)
        if not task:
            return False

        if task["status"] in ("COMPLETED", "FAILED"):
            return False

        stop_event = threading.Event()
        self._stop_flags[task_id] = stop_event

        thread = threading.Thread(
            target=self._run_resume_worker,
            args=(task_id, agent_runner, stop_event),
            daemon=True,
            name=f"CodeAgentResumeWorker-{task_id[:8]}"
        )
        self._active_threads[task_id] = thread
        thread.start()
        return True

    def _run_resume_worker(self, task_id: str, agent_runner: Callable[[str], str] | None, stop_event: threading.Event) -> None:
        self.db.update_task_status(task_id, "RUNNING")
        self.event_bus.publish(task_id, "TASK_RESUMED", {"task_id": task_id})

        try:
            from agent_pipeline import AgentStateMachineController

            task = self.get_task(task_id)
            if not task:
                return

            controller = AgentStateMachineController(workspace_dir=task["project_path"])

            def event_aware_runner(prompt: str) -> str:
                self.event_bus.publish(task_id, "TOOL_EXECUTED", {"prompt": prompt[:120]})
                if agent_runner:
                    return agent_runner(prompt)
                try:
                    from tools import agente_desarrollador_codeagent
                    return str(agente_desarrollador_codeagent.run(prompt))
                except Exception as ex:
                    return f"Respuesta de ejecución: {ex}"

            output_text, metrics = controller.resume_session(session_id=task_id, agent_runner=event_aware_runner)

            if stop_event.is_set():
                self.db.update_task_status(task_id, "CANCELLED", current_state="DONE")
                self.event_bus.publish(task_id, "TASK_CANCELLED", {"task_id": task_id})
                return

            self.db.update_task_status(task_id, "COMPLETED", current_state="DONE")
            self.event_bus.publish(task_id, "TASK_COMPLETED", {"task_id": task_id, "output": output_text, "metrics": metrics})

        except Exception as e:
            self.db.update_task_status(task_id, "FAILED")
            self.event_bus.publish(task_id, "TASK_FAILED", {"task_id": task_id, "error": str(e)})

    def cancel_task(self, task_id: str) -> bool:
        """Cancela definitivamente una tarea."""
        if task_id in self._stop_flags:
            self._stop_flags[task_id].set()
        self.db.update_task_status(task_id, "CANCELLED", current_state="DONE")
        self.event_bus.publish(task_id, "TASK_CANCELLED", {"task_id": task_id})
        return True

    def get_events(self, task_id: str, since_id: int = 0) -> list[dict[str, Any]]:
        """Obtiene la lista de eventos desde un determinado ID."""
        return self.event_bus.get_events(task_id, since_id=since_id)


_global_runtime: CodeAgentRuntime | None = None

def get_runtime() -> CodeAgentRuntime:
    global _global_runtime
    if _global_runtime is None:
        _global_runtime = CodeAgentRuntime()
    return _global_runtime
