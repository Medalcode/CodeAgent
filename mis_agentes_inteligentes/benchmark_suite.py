"""
CodeAgent v4.2 Reproducible Benchmark Suite
Suite estandarizada de 5 tareas reales de ingeniería de software para evaluación comparativa:
- Task 01: Bug Simple (Identificación y corrección local)
- Task 02: Refactor Seguro (Descomposición de funciones sin romper tests)
- Task 03: Feature Multicapa (Creación de módulo/endpoint con pruebas)
- Task 04: Debug Difícil (Aislamiento y auto-recuperación de pruebas fallidas)
- Task 05: Proyecto Desconocido (Graphify) (Exploración estructural AST y parches guiados)
"""
import logging
import os
import time
from collections.abc import Callable
from typing import Any

from .agent_pipeline import AgentStateMachineController, ExecutionLevel
from benchmark_metrics import metrics_collector


class CodeAgentBenchmarkSuite:
    """Ejecutor automatizado de la Suite de 5 Benchmarks Reales de Ingeniería."""

    def __init__(self, workspace_dir: str | None = None):
        self.workspace_dir = workspace_dir or os.getcwd()
        self.controller = AgentStateMachineController(workspace_dir=self.workspace_dir)

    def get_benchmark_tasks(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "TASK_01",
                "name": "Task 01 — Bug Simple",
                "level": ExecutionLevel.LEVEL_2_ACTION,
                "goal": "Corrige el error sintáctico de comillas en la función _safe_print en localcode_server.py.",
                "category": "Bugfix"
            },
            {
                "id": "TASK_02",
                "name": "Task 02 — Refactor Seguro",
                "level": ExecutionLevel.LEVEL_3_FEATURE,
                "goal": "Descompón la función monolítica main en localcode_server.py en sub-funciones modularizadas.",
                "category": "Refactoring"
            },
            {
                "id": "TASK_03",
                "name": "Task 03 — Feature Multicapa",
                "level": ExecutionLevel.LEVEL_3_FEATURE,
                "goal": "Crea el endpoint /api/benchmark/summary en localcode_server.py devolviendo los KPIs de rendimiento.",
                "category": "New Feature"
            },
            {
                "id": "TASK_04",
                "name": "Task 04 — Debug Difícil & Auto-Recuperación",
                "level": ExecutionLevel.LEVEL_4_FULL,
                "goal": "Resuelve la prueba unitaria fallida en test_state_machine.py asegurando que el bucle Replan repare el fallo.",
                "category": "Autonomous Debugging"
            },
            {
                "id": "TASK_05",
                "name": "Task 05 — Proyecto Desconocido (Graphify-First)",
                "level": ExecutionLevel.LEVEL_4_FULL,
                "goal": "Consulta el Grafo AST Graphify para identificar los símbolos conectados a JSONSessionRepository y añade validación de esquema.",
                "category": "Graphify Exploration"
            }
        ]

    def run_suite(self, agent_runner: Callable[[str], str] | None = None) -> dict[str, Any]:
        """Ejecuta la suite completa de 5 tareas y compila el informe comparativo."""
        tasks = self.get_benchmark_tasks()
        suite_start = time.time()
        results = []

        for task in tasks:
            logging.info(f"🧪 [BenchmarkSuite] Ejecutando {task['name']}...")
            start_t = time.time()

            try:
                response, metrics = self.controller.run(
                    user_goal=task["goal"],
                    agent_runner=agent_runner,
                    level=task["level"]
                )
                passed = metrics.get("verifier_passed", False)
                elapsed = metrics.get("tiempo_segundos", round(time.time() - start_t, 2))
                replans = metrics.get("replans_count", 0)
                recovered = metrics.get("recovered_autonomously", False)
            except Exception as e:
                response = f"Error durante la ejecución del benchmark: {e}"
                passed = False
                elapsed = round(time.time() - start_t, 2)
                replans = 0
                recovered = False
                metrics = {}

            results.append({
                "id": task["id"],
                "name": task["name"],
                "category": task["category"],
                "passed": passed,
                "elapsed_seconds": elapsed,
                "replans": replans,
                "recovered_autonomously": recovered,
                "response_summary": response[:120]
            })

        total_elapsed = round(time.time() - suite_start, 2)
        total_tasks = len(tasks)
        passed_tasks = sum(1 for r in results if r["passed"])
        success_rate = round((passed_tasks / total_tasks) * 100, 1)

        summary = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tasks": total_tasks,
            "passed_tasks": passed_tasks,
            "success_rate_pct": success_rate,
            "total_elapsed_seconds": total_elapsed,
            "tasks_results": results,
            "overall_kpis": metrics_collector.compute_summary()
        }

        self._export_report_markdown(summary)
        return summary

    def _export_report_markdown(self, summary: dict[str, Any]):
        """Exporta el reporte de benchmark en formato Markdown en mis_agentes_inteligentes/benchmark_report_v42.md."""
        report_path = os.path.join(self.workspace_dir, "mis_agentes_inteligentes", "benchmark_report_v42.md")
        lines = [
            "# 🧪 Reporte Oficial de Benchmark Reales CodeAgent (v4.2 Enterprise)\n",
            f"**Fecha de Ejecución:** `{summary['timestamp']}`  ",
            f"**Tasa de Éxito de Tareas (Task Success Rate):** `{summary['success_rate_pct']}%` ({summary['passed_tasks']}/{summary['total_tasks']} Pasadas)  ",
            f"**Tiempo Total de la Suite:** `{summary['total_elapsed_seconds']}s`  \n",
            "## 📊 Resultados por Tarea de Ingeniería\n",
            "| ID | Nombre de Tarea | Categoría | Estado | Tiempo | Re-plans | Autoreparado |",
            "| :--- | :--- | :--- | :---: | :---: | :---: | :---: |"
        ]

        for r in summary["tasks_results"]:
            st = "✅ PASADO" if r["passed"] else "❌ FALLO"
            rec = "✅ Sí" if r["recovered_autonomously"] else "N/A"
            lines.append(f"| {r['id']} | {r['name']} | {r['category']} | {st} | {r['elapsed_seconds']}s | {r['replans']} | {rec} |")

        kpis = summary.get("overall_kpis", {})
        lines.extend([
            "\n## 📈 KPIs Globales Acumulados\n",
            f"- **Task Success Rate:** `{kpis.get('task_success_rate_pct', 0)}%`",
            f"- **Autonomous Recovery Rate:** `{kpis.get('autonomous_recovery_rate_pct', 0)}%`",
            f"- **Promedio Re-planificaciones / Tarea:** `{kpis.get('avg_replans_per_task', 0)}`",
            f"- **Tiempo Promedio de Tarea:** `{kpis.get('avg_elapsed_seconds', 0)}s`"
        ])

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


if __name__ == "__main__":
    suite = CodeAgentBenchmarkSuite()
    res = suite.run_suite()
    print(f"✅ Benchmark completado con {res['passed_tasks']}/{res['total_tasks']} tareas exitosas ({res['success_rate_pct']}%)")
