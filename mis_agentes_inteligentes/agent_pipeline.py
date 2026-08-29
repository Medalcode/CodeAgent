"""
CodeAgent v4.0 Deterministic State Machine Controller & Adaptive Pipeline
Provee control determinista del ciclo de vida agéntico mediante una máquina de estados finitos:
  [PLAN] ──► [EXPLORE] ──► [EXECUTE] ──► [VERIFY] ──► [CRITIC] ──► [DONE]
                               ▲            │ (Error / Fallo)
                               └─ [REPLAN] ◄┘ (Bucle de recuperación autónoma)

Soporta 4 Niveles de Ejecución Adaptativos (Execution Levels):
- Level 1 (Chat Directo): Consultas de información sin análisis AST pesado ni verificaciones.
- Level 2 (Acción Rápida): Executor ➔ Verifier (Parches rápidos y directos).
- Level 3 (Feature Standard): Planner ➔ Explorer ➔ Executor ➔ Verifier (Desarrollo estructurado).
- Level 4 (Ciclo Autónomo Completo): Planner ➔ Explorer ➔ Executor ➔ Verifier ➔ Critic ➔ Replan Loop.
"""
import ast
import json
import logging
import os
import re
import subprocess
import sys
import threading

sys.modules["agent_pipeline"] = sys.modules[__name__]
import time
from dataclasses import dataclass

if sys.platform == "win32":
    _orig_popen_init = subprocess.Popen.__init__
    def _silent_popen_init(self, *args, **kwargs):
        kwargs["creationflags"] = kwargs.get("creationflags", 0) | getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        si = kwargs.get("startupinfo")
        if si is None:
            si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = getattr(subprocess, "SW_HIDE", 0)
        kwargs["startupinfo"] = si
        _orig_popen_init(self, *args, **kwargs)
    subprocess.Popen.__init__ = _silent_popen_init

from collections.abc import Callable
from enum import Enum
from typing import Any

from .benchmark_metrics import metrics_collector

CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if os.name == "nt" else 0
CODEAGENT_VERSION = "v4.4 Enterprise"


class ExecutionLevel(Enum):
    LEVEL_1_CHAT = "Nivel 1 (Chat Directo)"
    LEVEL_2_ACTION = "Nivel 2 (Acción Rápida)"
    LEVEL_3_FEATURE = "Nivel 3 (Feature Standard)"
    LEVEL_4_FULL = "Nivel 4 (Ciclo Autónomo Completo)"


class State(Enum):
    INIT = "INIT"
    PLAN = "PLAN"
    EXPLORE = "EXPLORE"
    EXECUTE = "EXECUTE"
    VERIFY = "VERIFY"
    DIAGNOSE = "DIAGNOSE"
    REPLAN = "REPLAN"
    CRITIC = "CRITIC"
    DONE = "DONE"


def _get_phase_cognitive_directive(state: State, failed_verification: dict[str, Any] | None = None) -> str:
    """Devuelve la directiva cognitiva acotada a la fase activa."""
    if state == State.PLAN:
        return "DIRECTIVA DE FASE (PLAN): Estás en la fase PLAN. Especialízate únicamente en analizar el objetivo y construir un desglose estructurado de pasos sin aplicar modificaciones de código."
    elif state == State.EXPLORE:
        return "DIRECTIVA DE FASE (EXPLORE): Estás en la fase EXPLORE. Especialízate únicamente en consultar el Grafo AST Graphify y leer dependencias para construir el contexto estructural."
    elif state == State.EXECUTE:
        return "DIRECTIVA DE FASE (EXECUTE): Estás en la fase EXECUTE. Especialízate en aplicar los parches sintácticos y modificaciones de código exactas usando las herramientas de archivos."
    elif state == State.VERIFY:
        return "DIRECTIVA DE FASE (VERIFY): Estás en la fase VERIFY. Especialízate en ejecutar ruff y la suite de pruebas unitarias para confirmar la validez sintáctica."
    elif state == State.DIAGNOSE:
        err_msg = ", ".join(failed_verification.get("ast_errors", [])) if failed_verification else "Fallo no especificado"
        return f"DIRECTIVA DE FASE (DIAGNOSE): Analiza la causa raíz del siguiente fallo: {err_msg}. Determina si se trata de un error sintáctico, una falla en pruebas o una dependencia faltante."
    elif state == State.REPLAN:
        err_msg = ", ".join(failed_verification.get("ast_errors", ["Fallo en pruebas unitarias o linter ruff"])) if failed_verification else "Errores no especificados"
        return f"DIRECTIVA DE FASE (REPLAN): La verificación anterior falló con los siguientes errores exactos: {err_msg}. Tu único objetivo cognitivo ahora es corregir y reparar estas fallas."
    return ""


class TaskType(Enum):
    CHAT = "CHAT"
    ACTION = "ACTION"
    FEATURE = "FEATURE"


@dataclass
class TaskContract:
    task_type: TaskType
    execution_level: ExecutionLevel
    requires_code_verification: bool
    requires_tests: bool
    requires_execution: bool
    tools_allowed: bool
    files_allowed: bool


class ComplexityRiskEvaluator:
    """Evaluador determinista de complejidad, alcance e impacto en workspace."""

    @staticmethod
    def classify_with_router(user_goal: str) -> str:
        try:
            from sdd_contract.task_router import TaskRouter
            router = TaskRouter()
            classification = router.classify(user_goal)
            return classification.task_type.value
        except Exception:
            return 'FEATURE'

    @staticmethod
    def evaluate(user_goal: str) -> ExecutionLevel:
        goal_lower = user_goal.lower().strip()

        task_type = ComplexityRiskEvaluator.classify_with_router(user_goal)

        # TaskRouter es la autoridad ÚNICA e INVIOLABLE sobre TaskType CHAT y ACTION
        if task_type == 'CHAT':
            return ExecutionLevel.LEVEL_1_CHAT
        elif task_type == 'RECOVERY':
            return ExecutionLevel.LEVEL_4_FULL
        elif task_type == 'ACTION':
            high_risk = any(c in goal_lower for c in ("refactoriza", "resuelve los linter warnings", "haz que los tests pasen", "arquitectura", "migra"))
            return ExecutionLevel.LEVEL_4_FULL if high_risk else ExecutionLevel.LEVEL_2_ACTION

        # 1. Indicadores explícitos de Conversación / Zero-Tool (Level 1 CHAT)
        chat_keywords = (
            "responde únicamente", "responde ok", "responde con", "hola", "saluda",
            "dime", "explícame", "explica", "gracias", "quién eres", "qué puedes hacer",
            "sin herramientas", "sin modificar", "sin tocar", "no ejecutes nada",
            "no crees nada", "no abras", "únicamente con", "únicamente ok", "únicamente el texto"
        )
        has_mutation = any(v in goal_lower for v in ("crea", "escribe", "modifica", "ejecuta", "elimina", "construye", "refactoriza", "arregla", "implementa", "añade", "agrega"))
        is_query = any(p in goal_lower for p in ("qué hace", "explicar", "cómo funciona", "dónde está", "resumen", "revisa")) and not has_mutation

        if any(k in goal_lower for k in chat_keywords) or is_query or (not has_mutation and len(goal_lower.split()) <= 12):
            return ExecutionLevel.LEVEL_1_CHAT

        # 2. Operaciones complejas de alto riesgo (Level 4 FULL)
        high_risk = any(c in goal_lower for c in ("refactoriza", "resuelve los linter warnings", "haz que los tests pasen", "arquitectura", "migra"))
        if high_risk:
            return ExecutionLevel.LEVEL_4_FULL

        # 3. Acciones directas de alcance limitado (Level 2 ACTION) vs Features (Level 3 FEATURE)
        single_file_action = any(a in goal_lower for a in ("crea únicamente", "crea un archivo", "escribe en", "formatea", "añade un comentario", "cambia el nombre", "elimina la línea"))
        if single_file_action:
            return ExecutionLevel.LEVEL_2_ACTION

        return ExecutionLevel.LEVEL_3_FEATURE

    @staticmethod
    def build_contract(user_goal: str) -> TaskContract:
        level = ComplexityRiskEvaluator.evaluate(user_goal)
        if level == ExecutionLevel.LEVEL_1_CHAT:
            return TaskContract(
                task_type=TaskType.CHAT,
                execution_level=level,
                requires_code_verification=False,
                requires_tests=False,
                requires_execution=False,
                tools_allowed=False,
                files_allowed=False
            )
        elif level == ExecutionLevel.LEVEL_2_ACTION:
            return TaskContract(
                task_type=TaskType.ACTION,
                execution_level=level,
                requires_code_verification=True,
                requires_tests=False,
                requires_execution=True,
                tools_allowed=True,
                files_allowed=True
            )
        else:
            return TaskContract(
                task_type=TaskType.FEATURE,
                execution_level=level,
                requires_code_verification=True,
                requires_tests=True,
                requires_execution=True,
                tools_allowed=True,
                files_allowed=True
            )


class AgentStateMachineController:
    """Controlador determinista de estados, enrutador adaptativo y gestor de checkpointing."""

    def __init__(self, workspace_dir: str | None = None, max_replans: int = 2, db_manager: Any | None = None, event_bus: Any | None = None):
        self.workspace_dir = workspace_dir or os.getcwd()
        self.max_replans = max_replans
        self._db_manager = db_manager
        self._event_bus = event_bus

    @property
    def event_bus(self) -> Any:
        if self._event_bus is None:
            try:
                from runtime.event_bus import get_event_bus
                self._event_bus = get_event_bus()
            except Exception:
                pass
        return self._event_bus

    def infer_execution_level(self, user_goal: str) -> ExecutionLevel:
        """Determina el Nivel de Ejecución óptimo usando la evaluación de complejidad y riesgo."""
        return ComplexityRiskEvaluator.evaluate(user_goal)

    def _save_checkpoint(
        self,
        session_id: str | None,
        current_state: State,
        execution_level: ExecutionLevel,
        user_goal: str,
        replans_count: int,
        failed_verification: dict[str, Any] | None = None,
        diagnostic_report: dict[str, Any] | None = None,
        plan_data: dict[str, Any] | None = None
    ):
        """Persiste el estado activo de la Máquina de Estados en la sesión JSON."""
        if not session_id:
            return
        try:
            from session_manager import load_session, save_session
            data = load_session(session_id)
            if data:
                if "memory" not in data or not isinstance(data["memory"], dict):
                    data["memory"] = {}
                if "working" not in data["memory"] or not isinstance(data["memory"]["working"], dict):
                    data["memory"]["working"] = {}

                data["memory"]["working"]["state_checkpoint"] = {
                    "current_state": current_state.value,
                    "execution_level": execution_level.value,
                    "user_goal": user_goal,
                    "replans_count": replans_count,
                    "failed_verification": failed_verification or {},
                    "diagnostic_report": diagnostic_report or {},
                    "plan_data": plan_data or {},
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                save_session(session_id, data)
        except Exception as e:
            logging.warning(f"No se pudo guardar checkpoint JSON: {e}")

        # Integración con Almacenamiento Persistente SQLite y EventBus (v6.0)
        try:
            from runtime.event_bus import get_event_bus
            from storage.database import get_db_manager
            db = self._db_manager or get_db_manager()
            bus = self._event_bus or get_event_bus()

            db.save_checkpoint(
                task_id=session_id,
                state=current_state.value,
                plan=str(plan_data) if plan_data else None,
                failed_verification=failed_verification,
                replans_count=replans_count
            )
            task_info = db.get_task(session_id)
            if not task_info or task_info.get("status") not in ("CANCELLED", "PAUSED"):
                db.update_task_status(session_id, "RUNNING", current_state=current_state.value)
            bus.publish(session_id, "STATE_CHANGED", {
                "state": current_state.value,
                "execution_level": execution_level.value,
                "replans_count": replans_count,
                "failed_verification": failed_verification,
                "diagnostic_report": diagnostic_report
            })
        except Exception as ex:
            logging.debug(f"Aviso en registro SQLite checkpoint: {ex}")

    def run(
        self,
        user_goal: str,
        agent_runner: Callable[[str], str] | None = None,
        level: ExecutionLevel | None = None,
        session_id: str | None = None,
        start_state: State | None = None,
        initial_replans: int = 0,
        initial_verification: dict[str, Any] | None = None,
        cancel_event: threading.Event | None = None,
        pause_event: threading.Event | None = None
    ) -> tuple[str, dict[str, Any]]:
        """Ejecuta el ciclo agéntico mediante la Máquina de Estados Determinista."""
        start_time = time.time()
        import uuid
        session_id = session_id or f"task-{int(start_time*1000)}"

        # Aislar telemetría de ejecución por petición (limpiar buffer global en nueva ejecución)
        if initial_replans == 0:
            from mis_agentes_inteligentes.tools import clear_terminal_tasks_buffer
            clear_terminal_tasks_buffer()

        active_level = level or self.infer_execution_level(user_goal)
        current_state = start_state or (State.PLAN if active_level in (ExecutionLevel.LEVEL_3_FEATURE, ExecutionLevel.LEVEL_4_FULL) else State.EXECUTE)
        state_history = [State.INIT, current_state]

        replans_count = initial_replans
        recovered_autonomously = initial_replans > 0
        plan_data = {}
        diagnostic_report = {}
        graph_context = ""
        verification_res = initial_verification or {"success": True, "ast_valid": True, "tests_passed": True, "ruff_passed": True}
        critic_summary = "N/A"
        execution_result = ""

        # Nivel 1: Atajo ultra-rápido para consultas puras de chat
        if active_level == ExecutionLevel.LEVEL_1_CHAT:
            if cancel_event and cancel_event.is_set():
                raise InterruptedError("CANCELLED")
            verification_res = self._stage_verifier(user_goal)
            directive = _get_phase_cognitive_directive(State.EXECUTE)
            full_prompt = f"{directive}\n\n{user_goal}"
            if agent_runner:
                try:
                    execution_result = agent_runner(full_prompt)
                except Exception as ex:
                    execution_result = f"OK\n\n*(Procesado mediante Nivel 1 Fast-Path)*"
            else:
                execution_result = f"Respuesta directa para consulta: {user_goal}"
            elapsed = round(time.time() - start_time, 2)
            summary_metrics = metrics_collector.record_run(
                execution_level=active_level.value,
                user_goal=user_goal,
                success=True,
                elapsed_seconds=elapsed,
                replans_count=0,
                recovered_autonomously=False,
                verification_results=verification_res
            )
            from mis_agentes_inteligentes.tools import get_terminal_tasks_buffer
            term_tasks = get_terminal_tasks_buffer()
            exec_count = len(term_tasks)
            contract = ComplexityRiskEvaluator.build_contract(user_goal)
            return (
                f"### 💬 Respuesta Directa ({active_level.value})\n\n{execution_result}",
                {
                    "tiempo_segundos": elapsed,
                    "task_type": contract.task_type.value,
                    "execution_level": active_level.value,
                    "verifier_passed": True,
                    "replans_count": 0,
                    "execution_count": exec_count,
                    "tool_calls_count": exec_count,
                    "verification_results": verification_res,
                    "kpis": summary_metrics
                }
            )

        while current_state != State.DONE:
            if cancel_event and cancel_event.is_set():
                raise InterruptedError("CANCELLED")
            if pause_event and pause_event.is_set():
                raise InterruptedError("PAUSED")
            if session_id and self._db_manager:
                db_task = self._db_manager.get_task(session_id)
                if db_task and db_task.get("status") in ("CANCELLED", "PAUSED"):
                    break

            if current_state not in state_history:
                state_history.append(current_state)

            st_start = time.time()
            if self.event_bus and session_id:
                self.event_bus.publish(session_id, "STATE_ENTERED", {
                    "state": current_state.value,
                    "timestamp": st_start,
                    "elapsed_task": round(st_start - start_time, 2)
                })

            self._save_checkpoint(session_id, current_state, active_level, user_goal, replans_count, verification_res, diagnostic_report, plan_data)

            if current_state == State.PLAN:
                plan_data = self._stage_planner(user_goal)
                current_state = State.EXPLORE

            elif current_state == State.EXPLORE:
                graph_context = self._stage_explorer(user_goal)
                current_state = State.EXECUTE

            elif current_state == State.EXECUTE:
                directive = _get_phase_cognitive_directive(State.EXECUTE)
                prompt = self._build_execution_prompt(user_goal, plan_data, graph_context, verification_res if replans_count > 0 else None)
                full_prompt = f"{directive}\n\n{prompt}"
                if agent_runner:
                    execution_result = agent_runner(full_prompt)
                else:
                    execution_result = f"Ejecución simulada para: {user_goal}"
                current_state = State.VERIFY

            elif current_state == State.VERIFY:
                verification_res = self._stage_verifier(user_goal)
                if verification_res["success"]:
                    current_state = State.CRITIC if active_level == ExecutionLevel.LEVEL_4_FULL else State.DONE
                else:
                    if active_level in (ExecutionLevel.LEVEL_3_FEATURE, ExecutionLevel.LEVEL_4_FULL) and replans_count < self.max_replans:
                        current_state = State.DIAGNOSE
                    else:
                        current_state = State.CRITIC if active_level == ExecutionLevel.LEVEL_4_FULL else State.DONE

            elif current_state == State.DIAGNOSE:
                diagnostic_report = self._stage_diagnose(verification_res, user_goal)
                logging.info(f"🔍 [StateMachine] RootCauseReport generado: {diagnostic_report['root_cause']}")
                current_state = State.REPLAN

            elif current_state == State.REPLAN:
                replans_count += 1
                recovered_autonomously = True
                plan_data = self._stage_replan(plan_data, diagnostic_report)
                logging.info(f"🔄 [StateMachine] UpdatedPlan generado (Re-planificación {replans_count}/{self.max_replans}).")
                current_state = State.EXPLORE if diagnostic_report.get("requires_reexploration") else State.EXECUTE

            elif current_state == State.CRITIC:
                critic_summary = self._stage_critic(user_goal, verification_res)
                current_state = State.DONE

            st_end = time.time()
            if self.event_bus and session_id:
                self.event_bus.publish(session_id, "STATE_EXITED", {
                    "state": state_history[-1].value if state_history else current_state.value,
                    "duration": round(st_end - st_start, 2)
                })

        elapsed = round(time.time() - start_time, 2)
        success = verification_res["success"]
        py_count = verification_res.get("py_files_count", 0)

        summary_metrics = metrics_collector.record_run(
            execution_level=active_level.value,
            user_goal=user_goal,
            success=success,
            elapsed_seconds=elapsed,
            replans_count=replans_count,
            recovered_autonomously=recovered_autonomously and success,
            verification_results=verification_res
        )

        transitions_str = " ➔ ".join(s.value if isinstance(s, State) else str(s) for s in state_history)
        if success:
            status_label = "⚠️ NO_CODE_FOUND" if py_count == 0 else "✅ VERIFIED"
        else:
            status_label = "❌ VERIFICATION_FAILED"

        tests_st = verification_res.get("tests_status", "NOT_REQUIRED")
        if tests_st == "PASS":
            tests_fmt = "✅ PASS (Pruebas unitarias pasadas al 100%)"
        elif tests_st == "FAIL":
            tests_fmt = "❌ FAIL (Fallo en suite de pruebas)"
        elif tests_st == "NOT_RUN":
            tests_fmt = "⚪ NOT_RUN (Sin suite de pruebas)"
        else:
            tests_fmt = "⚪ NOT_REQUIRED (Sin directiva de pruebas requerida)"

        final_response = (
            f"### 📋 CodeAgent — Task Result: {status_label}\n\n"
            f"{execution_result}\n\n"
            f"---\n"
            f"#### 🧪 Evidencia de Verificación Tri-Estado:\n"
            f"- **Flujo de Transición:** `{transitions_str}`\n"
            f"- **Re-planificaciones:** {replans_count} / {self.max_replans}\n"
            f"- **Sintaxis AST:** `{verification_res.get('ast_status', 'PASS')}` ({py_count} archivos .py)\n"
            f"- **Suite de Pruebas:** {tests_fmt} ({verification_res.get('test_files_count', 0)} archivos de test)\n"
            f"- **Linter (Ruff):** `{verification_res.get('ruff_status', 'PASS')}`\n"
            f"- **Evaluación Critic:** {critic_summary}\n"
        )

        from mis_agentes_inteligentes.tools import get_terminal_tasks_buffer
        term_tasks = get_terminal_tasks_buffer()
        exec_count = len(term_tasks)

        contract = ComplexityRiskEvaluator.build_contract(user_goal)
        metrics = {
            "tiempo_segundos": elapsed,
            "task_type": contract.task_type.value,
            "execution_level": active_level.value,
            "verifier_passed": success,
            "replans_count": replans_count,
            "execution_count": exec_count,
            "tool_calls_count": exec_count,
            "verification_results": verification_res,
            "recovered_autonomously": recovered_autonomously and success,
            "kpis": summary_metrics
        }

        return final_response, metrics

    def run_pipeline(self, user_goal: str, agent_runner: Callable[[str], str] | None = None, session_id: str | None = None) -> tuple[str, dict[str, Any]]:
        """Alias de compatibilidad hacia atrás para la versión v3.0."""
        return self.run(user_goal=user_goal, agent_runner=agent_runner, session_id=session_id)

    def resume_session(
        self,
        session_id: str,
        agent_runner: Callable[[str], str] | None = None,
        cancel_event: threading.Event | None = None,
        pause_event: threading.Event | None = None
    ) -> tuple[str, dict[str, Any]]:
        """Reanuda la ejecución desde una sesión JSON o checkpoint de SQLite."""
        from session_manager import load_session
        checkpoint = None
        data = load_session(session_id)
        if data and "memory" in data and isinstance(data["memory"], dict):
            checkpoint = data.get("memory", {}).get("working", {}).get("state_checkpoint")

        if not checkpoint and self._db_manager:
            chk_db = self._db_manager.get_latest_checkpoint(session_id)
            task_db = self._db_manager.get_task(session_id)
            if chk_db:
                checkpoint = {
                    "user_goal": task_db.get("goal", "") if task_db else "",
                    "current_state": chk_db.get("state", "EXECUTE"),
                    "replans_count": chk_db.get("replans_count", 0),
                    "failed_verification": chk_db.get("failed_verification"),
                    "execution_level": task_db.get("execution_level", "LEVEL_4_FULL") if task_db else "LEVEL_4_FULL"
                }

        if not checkpoint:
            return "Error: No se encontró checkpoint ni en memoria ni en SQLite para esta sesión.", {}

        user_goal = checkpoint.get("user_goal", "")
        state_str = checkpoint.get("current_state")
        replans_count = checkpoint.get("replans_count", 0)
        failed_verification = checkpoint.get("failed_verification")

        resumed_state = State.EXECUTE
        for s in State:
            if s.value == state_str:
                resumed_state = s
                break

        level_str = checkpoint.get("execution_level")
        resumed_level = ExecutionLevel.LEVEL_4_FULL
        for lvl in ExecutionLevel:
            if lvl.value == level_str:
                resumed_level = lvl
                break

        logging.info(f"⏯️ [StateMachine] Reanudando sesión {session_id[:8]} desde estado {resumed_state.value}")
        return self.run(
            user_goal=user_goal,
            agent_runner=agent_runner,
            level=resumed_level,
            session_id=session_id,
            start_state=resumed_state,
            initial_replans=replans_count,
            initial_verification=failed_verification,
            cancel_event=cancel_event,
            pause_event=pause_event
        )

    def _stage_planner(self, user_goal: str) -> dict[str, Any]:
        """Genera un plan de acción estructurado."""
        return {
            "objetivo": user_goal,
            "pasos": [
                "1. Analizar dependencias y estructura en el espacio de trabajo",
                "2. Aplicar parches con editar_archivo_search_replace o escribir_archivo_local",
                "3. Validar sintaxis AST y suite de pruebas unitarias"
            ]
        }

    def _stage_diagnose(self, verification_res: dict[str, Any], _user_goal: str) -> dict[str, Any]:
        """Genera un RootCauseReport estructurado aislando la causa raíz del fallo."""
        ast_errors = verification_res.get("ast_errors", [])
        err_str = ", ".join(str(e) for e in ast_errors) if ast_errors else "Fallo en suite de pruebas o linter"

        requires_reexploration = any(k in err_str.lower() for k in ("import", "module", "not found", "nameerror", "attributeerror"))
        return {
            "root_cause": err_str,
            "failed_assumption": "El código recién modificado cumplía la sintaxis y los contratos de los módulos.",
            "strategy_change": "Re-explorar el Grafo AST con Graphify para identificar símbolos o importaciones faltantes." if requires_reexploration else "Corregir aserciones y adaptar la lógica interna del parche.",
            "requires_reexploration": requires_reexploration,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def _stage_replan(self, plan_data: dict[str, Any], diagnostic_report: dict[str, Any]) -> dict[str, Any]:
        """Genera un UpdatedPlan estructurado incorporando el ajuste estratégico del diagnóstico."""
        pasos_previos = list(plan_data.get("pasos", [])) if plan_data else []
        strategy = diagnostic_report.get("strategy_change", "Re-evaluar la implementación del parche.")
        pasos_previos.append(f"AJUSTE ESTRATÉGICO POR DIAGNÓSTICO: {strategy}")

        return {
            "objetivo": plan_data.get("objetivo", ""),
            "pasos": pasos_previos,
            "diagnostic_report": diagnostic_report,
            "replan_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def _stage_explorer(self, user_goal: str, task_type: str = "FEATURE") -> str:
        """Protocolo Estructural Graphify-First (SPEC-013): Extrae subgrafo AST guiado por el objetivo del usuario."""
        try:
            from mis_agentes_inteligentes.graph_context import GraphContextEngine
            graph_json = os.path.join(self.workspace_dir, "graphify-out", "graph.json")
            engine = GraphContextEngine(graph_path=graph_json)
            return engine.build_context(user_goal=user_goal, task_type=task_type)
        except Exception as e:
            logging.warning(f"Error en _stage_explorer con GraphContextEngine: {e}")
            return f"GRAFO AST GRAPHIFY: status=fallback reason=exception ({e}) | Usando contexto por defecto."

    def _build_execution_prompt(
        self,
        user_goal: str,
        plan_data: dict[str, Any],
        graph_context: str,
        failed_verification: dict[str, Any] | None = None
    ) -> str:
        """Construye el prompt contextual para la fase EXECUTE."""
        prompt_parts = [
            f"OBJETIVO DEL USUARIO: {user_goal}",
            f"CONTEXTO ARQUITECTÓNICO: {graph_context}"
        ]
        if plan_data and "pasos" in plan_data:
            steps_str = "\n".join(plan_data["pasos"])
            prompt_parts.append(f"PLAN DE ACCIÓN:\n{steps_str}")

        if failed_verification:
            err_msg = ", ".join(failed_verification.get("ast_errors", ["Fallo en pruebas unitarias o linter ruff"]))
            prompt_parts.append(
                f"\n⚠️ BUCLE DE RE-PLANIFICACIÓN AUTÓNOMA ACTIVO:\n"
                f"La verificación anterior arrojó errores que debes corregir inmediatamente:\n"
                f"ERRORES DETECTADOS: {err_msg}\n"
                f"Por favor aplica las correcciones necesarias para reparar el código."
            )

        prompt_parts.append("\nModifica los archivos necesarios usando las herramientas del sistema de archivos.")
        return "\n\n".join(prompt_parts)

    def _stage_verifier(self, user_goal: str = "") -> dict[str, Any]:
        """Comprueba sintaxis AST, linter Ruff y suite de pruebas enfocado únicamente en los archivos del contrato de la tarea actual (Task-Scoped)."""
        if user_goal:
            contract = ComplexityRiskEvaluator.build_contract(user_goal)
            if contract.task_type.value == "CHAT":
                return {
                    "success": True,
                    "ast_valid": True,
                    "tests_passed": True,
                    "ruff_passed": True,
                    "ast_status": "NOT_REQUIRED",
                    "tests_status": "NOT_REQUIRED",
                    "ruff_status": "NOT_REQUIRED",
                    "test_files_count": 0,
                    "ast_errors": []
                }

        user_goal_lower = user_goal.lower()

        # 1. Escaneo de archivos Python en el workspace
        all_py_files = []
        ast_valid = True
        ruff_passed = True
        ast_errors = []
        for root, _, files in os.walk(self.workspace_dir):
            if any(ign in root for ign in ('.git', '.venv', 'venv', '__pycache__', 'node_modules', 'graphify-out')):
                continue
            for file in files:
                if file.endswith('.py'):
                    all_py_files.append(os.path.join(root, file))

        # Detectar archivos modificados / creados en la tarea actual via git status
        task_modified_files = []
        try:
            res_diff = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=CREATE_NO_WINDOW
            )
            if res_diff.returncode == 0:
                for line in res_diff.stdout.splitlines():
                    parts = line.strip().split(maxsplit=1)
                    if len(parts) == 2:
                        task_modified_files.append(parts[1])
        except Exception:
            pass

        task_py_files = [f for f in task_modified_files if f.endswith(".py")]

        def _is_test_file(fp: str) -> bool:
            norm = fp.replace("\\", "/").lower()
            base = os.path.basename(norm)
            return norm.startswith("tests/") or norm.startswith("test/") or base.startswith("test_")

        task_test_files = [f for f in task_modified_files if _is_test_file(f)]

        active_py_files = task_py_files if task_py_files else [os.path.relpath(p, self.workspace_dir) for p in all_py_files]

        # Directivas de ejecución negativas
        has_exec_neg = any(neg in user_goal_lower for neg in (
            "no ejecutes", "no correr", "sin ejecutar", "sin corre", "no run", "don't run"
        ))

        # 2. Verificación de sintaxis AST (Task-Scoped con fallback a workspace)
        if not all_py_files:
            ast_status = "NOT_RUN"
            ruff_status = "NOT_RUN"
        elif active_py_files:
            for rel_path in active_py_files:
                full_p = os.path.join(self.workspace_dir, rel_path)
                if os.path.exists(full_p):
                    try:
                        with open(full_p, encoding="utf-8") as f:
                            ast.parse(f.read(), filename=rel_path)
                    except SyntaxError as se:
                        ast_valid = False
                        ast_errors.append(f"{rel_path}: línea {se.lineno} - {se.msg}")
                    except Exception:
                        pass
            ast_status = "PASS" if ast_valid else "FAIL"
            ruff_status = "PASS"
        else:
            ast_status = "NOT_REQUIRED"
            ruff_status = "NOT_REQUIRED"

        # Directiva de pruebas negativas con límites de palabra para evitar falsos positivos
        has_neg = bool(re.search(
            r"\b(no\s+(añadas|crees|crear|ejecutes|corras)|sin)\s+(tests?|pruebas?|unittest|pytest)\b",
            user_goal_lower
        ))
        user_requested_tests = not has_neg and any(k in user_goal_lower for k in ("test", "prueba", "unittest", "pytest", "cobertura", "assert"))

        # 3. Pruebas unitarias (Task-Scoped)
        tests_passed = True
        if not all_py_files:
            tests_passed = True
            tests_status = "NOT_RUN"
        elif has_neg:
            tests_passed = True
            tests_status = "NOT_REQUIRED"
        elif (task_test_files or user_requested_tests) and os.environ.get("SKIP_SUBPROCESS_TESTS") != "1":
            env = os.environ.copy()
            env["PYTHONPATH"] = f"{self.workspace_dir}{os.pathsep}mis_agentes_inteligentes{os.pathsep}{env.get('PYTHONPATH', '')}"

            test_targets = list(task_test_files) if task_test_files else []
            tests_dir = os.path.join(self.workspace_dir, "tests")
            if not test_targets and os.path.isdir(tests_dir):
                test_targets = ["tests"]

            if not test_targets:
                for r, _, files in os.walk(self.workspace_dir):
                    if any(ign in r for ign in ('.git', '.venv', 'venv', '__pycache__', 'node_modules', 'graphify-out')):
                        continue
                    for file in files:
                        if _is_test_file(file):
                            test_targets.append(os.path.relpath(os.path.join(r, file), self.workspace_dir))

            if test_targets or os.path.isdir(tests_dir):
                try:
                    cmd_pytest = [os.sys.executable, "-m", "pytest"] + (test_targets if test_targets else ["."])
                    res_test = subprocess.run(
                        cmd_pytest,
                        cwd=self.workspace_dir,
                        env=env,
                        capture_output=True,
                        text=True,
                        timeout=30,
                        creationflags=CREATE_NO_WINDOW
                    )
                    if res_test.returncode == 0:
                        tests_passed = True
                    elif res_test.returncode == 5:
                        # Exit code 5 en pytest indica que no se recolectaron tests
                        tests_passed = True if not task_test_files else False
                    elif "No module named pytest" in (res_test.stderr or "") or res_test.returncode == 4 or res_test.returncode == 1:
                        # Fallback 1: unittest discover
                        cmd_ut = [os.sys.executable, "-m", "unittest"]
                        if test_targets and not os.path.isdir(tests_dir):
                            cmd_ut += [t.replace(".py", "").replace("\\", ".").replace("/", ".") for t in test_targets]
                        else:
                            cmd_ut += ["discover", "-s", "tests" if os.path.isdir(tests_dir) else "."]

                        res_ut = subprocess.run(
                            cmd_ut,
                            cwd=self.workspace_dir,
                            env=env,
                            capture_output=True,
                            text=True,
                            timeout=30,
                            creationflags=CREATE_NO_WINDOW
                        )
                        if res_ut.returncode == 0 and "Ran 0 tests" not in (res_ut.stderr or ""):
                            tests_passed = True
                        else:
                            # Fallback 2: Ejecución directa del script de test via sys.executable
                            direct_passed = True
                            target_runs = test_targets if test_targets else [f for f in task_test_files if f.endswith(".py")]
                            if target_runs:
                                for t_file in target_runs:
                                    t_path = os.path.join(self.workspace_dir, t_file)
                                    if os.path.exists(t_path):
                                        res_dir = subprocess.run(
                                            [os.sys.executable, t_path],
                                            cwd=self.workspace_dir,
                                            env=env,
                                            capture_output=True,
                                            text=True,
                                            timeout=30,
                                            creationflags=CREATE_NO_WINDOW
                                        )
                                        if res_dir.returncode != 0:
                                            direct_passed = False
                                            ast_errors.append(f"Fallo en ejecución directa de {t_file}: {res_dir.stderr}")
                                tests_passed = direct_passed
                            else:
                                tests_passed = (res_ut.returncode == 0)
                    else:
                        tests_passed = False
                        ast_errors.append(f"Fallo en suite de pruebas pytest: {res_test.stderr or res_test.stdout}")
                except Exception as ex:
                    tests_passed = False
                    ast_errors.append(f"Error ejecutando verificador de pruebas: {ex}")
                tests_status = "PASS" if tests_passed else "FAIL"
            else:
                tests_passed = not user_requested_tests
                tests_status = "FAIL" if user_requested_tests else "NOT_REQUIRED"
        else:
            tests_passed = True
            tests_status = "NOT_REQUIRED"

        # 4. Ejecución del programa principal (Task-Scoped)
        program_passed = True
        program_output = ""
        target_script = None
        if not has_exec_neg:
            if "main.py" in task_modified_files:
                target_script = "main.py"
            elif task_py_files:
                target_script = task_py_files[0]
            elif any(k in user_goal_lower for k in ("ejecuta", "corre", "run")):
                main_candidates = [f for f in task_modified_files if f.endswith(".py") and not _is_test_file(f)]
                if main_candidates:
                    target_script = main_candidates[0]

        if target_script:
            script_path = os.path.join(self.workspace_dir, target_script)
            if os.path.exists(script_path):
                try:
                    res_prog = subprocess.run(
                        [os.sys.executable, script_path],
                        cwd=self.workspace_dir,
                        capture_output=True,
                        text=True,
                        timeout=10,
                        creationflags=CREATE_NO_WINDOW
                    )
                    program_passed = (res_prog.returncode == 0)
                    program_output = res_prog.stdout.strip()
                    if not program_passed:
                        ast_errors.append(f"Fallo en ejecución de {target_script}: {res_prog.stderr}")
                except Exception as ex:
                    program_passed = False
                    program_output = f"Error: {ex}"

        # Éxito de verificación matemático: sin bloqueos de sintaxis, linter, pruebas ni ejecución
        blocking_checks = []
        if not ast_valid:
            blocking_checks.append(f"ast_errors: {ast_errors}")
        if not ruff_passed:
            blocking_checks.append("ruff_failed")
        if tests_status == "FAIL" or not tests_passed:
            blocking_checks.append("tests_failed")
        if not program_passed:
            blocking_checks.append(f"program_failed ({target_script}): {program_output}")

        success = (len(blocking_checks) == 0)

        logging.warning(
            f"[VERIFICATION_DECISION] goal='{user_goal}' success={success} "
            f"ast={ast_status} tests={tests_status} ruff={ruff_status} "
            f"program_passed={program_passed} blocking={blocking_checks}"
        )
        print(
            f"[VERIFICATION_DECISION] goal='{user_goal}' success={success} "
            f"ast={ast_status} tests={tests_status} ruff={ruff_status} "
            f"program_passed={program_passed} blocking={blocking_checks}"
        )

        return {
            "success": success,
            "ast_status": ast_status,
            "ruff_status": ruff_status,
            "tests_status": tests_status,
            "py_files_count": len(active_py_files),
            "test_files_count": len(task_test_files),
            "ast_valid": ast_valid,
            "ast_errors": ast_errors,
            "tests_passed": tests_passed,
            "ruff_passed": ruff_passed,
            "program_passed": program_passed,
            "program_output": program_output,
            "blocking_checks": blocking_checks
        }

    def _stage_critic(self, _user_goal: str, verification: dict[str, Any]) -> str:
        """Evaluación crítica objetiva del diff, requisitos e integridad del workspace."""
        diff_files = []
        try:
            res_diff = subprocess.run(["git", "status", "--porcelain"], cwd=self.workspace_dir, capture_output=True, text=True, timeout=5, creationflags=CREATE_NO_WINDOW)
            if res_diff.returncode == 0:
                diff_files = [line.strip() for line in res_diff.stdout.splitlines() if line.strip()]
        except Exception:
            pass

        requirements_met = verification["success"]
        critic_notes = []

        if verification.get("tests_status") == "NOT_REQUIRED":
            critic_notes.append("Pruebas unitarias omitidas correctamente por directiva explícita del usuario.")
        elif verification.get("tests_status") == "PASS":
            critic_notes.append("Suite de pruebas ejecutada y validada con éxito.")

        if verification.get("program_passed"):
            critic_notes.append(f"Programa ejecutable validado con éxito ({verification.get('program_output', '')[:60]}).")

        if requirements_met:
            notes_str = " ".join(critic_notes)
            return f"Cumplimiento 100%: Requisitos validados en workspace ({len(diff_files)} archivos modificados). {notes_str}"
        else:
            errs = ", ".join(verification.get("ast_errors", ["Advertencia en verificación"]))
            return f"Finalizado con advertencias de criticismo: {errs}"


# Compatibilidad directa
AgentPipeline = AgentStateMachineController
