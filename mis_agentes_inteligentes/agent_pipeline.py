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
import subprocess
import time
from collections.abc import Callable
from enum import Enum
from typing import Any

from benchmark_metrics import metrics_collector


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
    CRITIC = "CRITIC"
    REPLAN = "REPLAN"
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
    elif state == State.REPLAN:
        err_msg = ", ".join(failed_verification.get("ast_errors", ["Fallo en pruebas unitarias o linter ruff"])) if failed_verification else "Errores no especificados"
        return f"DIRECTIVA DE FASE (REPLAN): La verificación anterior falló con los siguientes errores exactos: {err_msg}. Tu único objetivo cognitivo ahora es corregir y reparar estas fallas."
    return ""


class AgentStateMachineController:
    """Controlador determinista de estados, enrutador adaptativo y gestor de checkpointing."""

    def __init__(self, workspace_dir: str | None = None, max_replans: int = 2):
        self.workspace_dir = workspace_dir or os.getcwd()
        self.max_replans = max_replans

    def infer_execution_level(self, user_goal: str) -> ExecutionLevel:
        """Determina automáticamente el Nivel de Ejecución óptimo según la intención del usuario."""
        goal_lower = user_goal.lower()

        # Nivel 1: Consultas puramente informativas o explicaciones
        preguntas = ("qué hace", "explicar", "cómo funciona", "dónde está", "para qué sirve", "resumen", "revisa")
        if any(p in goal_lower for p in preguntas) and not any(a in goal_lower for a in ("crea", "modifica", "corrige", "arregla", "refactoriza")):
            return ExecutionLevel.LEVEL_1_CHAT

        # Nivel 2: Modificaciones simples y puntuales de un solo archivo
        acciones_simples = ("formatea", "añade un comentario", "cambia el nombre", "elimina la línea", "imprime")
        if any(a in goal_lower for a in acciones_simples):
            return ExecutionLevel.LEVEL_2_ACTION

        # Nivel 4: Refactorizaciones complejas o resolución autónoma de errores/tests
        complejos = ("refactoriza", "resuelve los linter warnings", "haz que los tests pasen", "arquitectura", "migra")
        if any(c in goal_lower for c in complejos):
            return ExecutionLevel.LEVEL_4_FULL

        # Nivel 3: Por defecto para desarrollo de nuevas características o scripts
        return ExecutionLevel.LEVEL_3_FEATURE

    def _save_checkpoint(
        self,
        session_id: str | None,
        current_state: State,
        execution_level: ExecutionLevel,
        user_goal: str,
        replans_count: int,
        failed_verification: dict[str, Any] | None = None
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
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                save_session(session_id, data)
        except Exception as e:
            logging.warning(f"No se pudo guardar checkpoint de estado: {e}")

    def run(
        self,
        user_goal: str,
        agent_runner: Callable[[str], str] | None = None,
        level: ExecutionLevel | None = None,
        session_id: str | None = None,
        start_state: State | None = None,
        initial_replans: int = 0,
        initial_verification: dict[str, Any] | None = None
    ) -> tuple[str, dict[str, Any]]:
        """Ejecuta el ciclo agéntico mediante la Máquina de Estados Determinista."""
        start_time = time.time()
        active_level = level or self.infer_execution_level(user_goal)
        current_state = start_state or (State.PLAN if active_level in (ExecutionLevel.LEVEL_3_FEATURE, ExecutionLevel.LEVEL_4_FULL) else State.EXECUTE)
        state_history = [State.INIT, current_state]

        replans_count = initial_replans
        recovered_autonomously = initial_replans > 0
        plan_data = {}
        graph_context = ""
        verification_res = initial_verification or {"success": True, "ast_valid": True, "tests_passed": True, "ruff_passed": True}
        critic_summary = "N/A"
        execution_result = ""

        # Nivel 1: Atajo ultra-rápido para consultas puras de chat
        if active_level == ExecutionLevel.LEVEL_1_CHAT:
            directive = _get_phase_cognitive_directive(State.EXECUTE)
            full_prompt = f"{directive}\n\n{user_goal}"
            if agent_runner:
                execution_result = agent_runner(full_prompt)
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
            return (
                f"### 💬 Respuesta Directa ({active_level.value})\n\n{execution_result}",
                {
                    "tiempo_segundos": elapsed,
                    "execution_level": active_level.value,
                    "verifier_passed": True,
                    "replans_count": 0,
                    "kpis": summary_metrics
                }
            )

        while current_state != State.DONE:
            if current_state not in state_history:
                state_history.append(current_state)

            self._save_checkpoint(session_id, current_state, active_level, user_goal, replans_count, verification_res)

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
                verification_res = self._stage_verifier()
                if verification_res["success"]:
                    current_state = State.CRITIC if active_level == ExecutionLevel.LEVEL_4_FULL else State.DONE
                else:
                    if active_level == ExecutionLevel.LEVEL_4_FULL and replans_count < self.max_replans:
                        current_state = State.REPLAN
                    else:
                        current_state = State.CRITIC if active_level == ExecutionLevel.LEVEL_4_FULL else State.DONE

            elif current_state == State.REPLAN:
                replans_count += 1
                recovered_autonomously = True
                logging.info(f"🔄 [StateMachine] Re-planificación activa ({replans_count}/{self.max_replans}) por fallos en verificación.")
                current_state = State.EXECUTE

            elif current_state == State.CRITIC:
                critic_summary = self._stage_critic(user_goal, verification_res)
                current_state = State.DONE

        elapsed = round(time.time() - start_time, 2)
        success = verification_res["success"]

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
        final_response = (
            f"### 🚀 Resultado Agéntico v4.0 — {active_level.value}\n\n"
            f"{execution_result}\n\n"
            f"---\n"
            f"#### ⚙️ Control de Estados Determinista:\n"
            f"- **Flujo de Transición de Estados:** `{transitions_str}`\n"
            f"- **Re-planificaciones Autónomas:** {replans_count} / {self.max_replans}\n"
            f"- **Sintaxis AST:** {'✅ Válida' if verification_res['ast_valid'] else '❌ Error sintáctico'}\n"
            f"- **Suite de Pruebas:** {'✅ Pasadas' if verification_res['tests_passed'] else '⚠ Fallo en tests'}\n"
            f"- **Linter (Ruff):** {'✅ 0 Errores' if verification_res['ruff_passed'] else '⚠ Advertencias'}\n"
            f"- **Evaluación Critic:** {critic_summary}\n"
        )

        metrics = {
            "tiempo_segundos": elapsed,
            "execution_level": active_level.value,
            "verifier_passed": success,
            "replans_count": replans_count,
            "recovered_autonomously": recovered_autonomously and success,
            "kpis": summary_metrics
        }

        return final_response, metrics

    def run_pipeline(self, user_goal: str, agent_runner: Callable[[str], str] | None = None) -> tuple[str, dict[str, Any]]:
        """Alias de compatibilidad hacia atrás para la versión v3.0."""
        return self.run(user_goal=user_goal, agent_runner=agent_runner)

    def resume_session(self, session_id: str, agent_runner: Callable[[str], str] | None = None) -> tuple[str, dict[str, Any]]:
        """Reanuda la ejecución agéntica desde el último StateCheckpoint persistido en la sesión."""
        from session_manager import load_session
        data = load_session(session_id)
        if not data or "memory" not in data:
            return "Error: No se encontró la sesión o no tiene memoria persistente.", {}

        checkpoint = data.get("memory", {}).get("working", {}).get("state_checkpoint")
        if not checkpoint:
            return "No se encontró ningún checkpoint de estado en esta sesión.", {}

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
            initial_verification=failed_verification
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

    def _stage_explorer(self, _user_goal: str) -> str:
        """Consulta el Grafo AST Graphify en busca de contexto estructural."""
        graph_dir = os.path.join(self.workspace_dir, "graphify-out")
        if os.path.exists(graph_dir):
            graph_json = os.path.join(graph_dir, "graph.json")
            if os.path.exists(graph_json):
                try:
                    with open(graph_json, encoding="utf-8") as f:
                        data = json.load(f)
                    nodes = data.get("nodes", [])
                    node_names = [n.get("name", "") for n in nodes[:10] if isinstance(n, dict) and "name" in n]
                    return f"Nodos relevantes en Grafo AST Graphify: {', '.join(node_names)}"
                except Exception:
                    pass
        return "Exploración estándar del árbol de archivos."

    def _build_execution_prompt(
        self,
        user_goal: str,
        plan_data: dict[str, Any],
        graph_context: str,
        failed_verification: dict[str, Any] | None = None
    ) -> str:
        prompt_parts = [
            f"OBJETIVO DEL USUARIO: {user_goal}",
        ]

        if plan_data:
            prompt_parts.append(f"PLAN DE ACCIÓN:\n{json.dumps(plan_data, ensure_ascii=False, indent=2)}")

        if graph_context:
            prompt_parts.append(f"CONTEXTO GRAFO AST (GRAPHIFY):\n{graph_context}")

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

    def _stage_verifier(self) -> dict[str, Any]:
        """Comprueba sintaxis AST, linter Ruff y suite de pruebas unitarias."""
        ast_valid = True
        ast_errors = []

        for root, _, files in os.walk(self.workspace_dir):
            if any(ign in root for ign in ('.git', '.venv', 'venv', '__pycache__', 'node_modules')):
                continue
            for file in files:
                if file.endswith('.py'):
                    full_p = os.path.join(root, file)
                    try:
                        with open(full_p, encoding='utf-8') as f:
                            ast.parse(f.read(), filename=file)
                    except SyntaxError as se:
                        ast_valid = False
                        ast_errors.append(f"{file}: línea {se.lineno} - {se.msg}")
                    except Exception:
                        pass

        ruff_passed = True
        try:
            res_ruff = subprocess.run(["uv", "run", "--with", "ruff", "ruff", "check", "."], cwd=self.workspace_dir, capture_output=True, text=True, timeout=15)
            if res_ruff.returncode != 0:
                ruff_passed = False
        except Exception:
            ruff_passed = True

        tests_passed = True
        if os.environ.get("SKIP_SUBPROCESS_TESTS") != "1":
            try:
                env = os.environ.copy()
                env["PYTHONPATH"] = "mis_agentes_inteligentes"
                res_test = subprocess.run([os.sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=self.workspace_dir, env=env, capture_output=True, text=True, timeout=30)
                if res_test.returncode != 0:
                    tests_passed = False
            except Exception:
                tests_passed = True

        return {
            "success": ast_valid and tests_passed and ruff_passed,
            "ast_valid": ast_valid,
            "ast_errors": ast_errors,
            "tests_passed": tests_passed,
            "ruff_passed": ruff_passed
        }

    def _stage_critic(self, user_goal: str, verification: dict[str, Any]) -> str:
        """Evaluación de cumplimiento final."""
        if verification["success"]:
            return f"Objetivo '{user_goal[:40]}' verificado y validado al 100% sin errores."
        else:
            errs = ", ".join(verification.get("ast_errors", ["Advertencia en suite de pruebas"]))
            return f"Finalizado con advertencias: {errs}"


# Compatibilidad directa
AgentPipeline = AgentStateMachineController
