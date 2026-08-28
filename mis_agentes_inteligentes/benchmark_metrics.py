"""
CodeAgent Benchmark & Quality Metrics Engine
Registra, calcula y persiste métricas cuantitativas reproducibles de rendimiento agéntico:
- Task Success Rate (% de tareas completadas con éxito)
- Tool Success Rate (% de ejecuciones de herramientas exitosas)
- Verification Success Rate (% de verificaciones sintácticas y de tests aprobadas)
- Autonomous Recovery Rate (% de errores corregidos automáticamente vía Re-planificación)
- Average Tool Calls / Replans
"""
import json
import logging
import os
import tempfile
import time
from typing import Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
METRICS_FILE = os.path.join(BASE_DIR, "metrics_benchmarks.json")


class BenchmarkMetricsCollector:
    """Colector y repositorio persistente de métricas cuantitativas agénticas."""

    def __init__(self, filepath: str = METRICS_FILE):
        self.filepath = filepath
        self._init_file()

    def _init_file(self):
        if not os.path.exists(self.filepath):
            initial_data = {
                "total_runs": 0,
                "successful_runs": 0,
                "total_replans": 0,
                "successful_recoveries": 0,
                "total_tool_calls": 0,
                "successful_tool_calls": 0,
                "history": []
            }
            self._save_data(initial_data)

    def _load_data(self) -> dict[str, Any]:
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {
            "total_runs": 0,
            "successful_runs": 0,
            "total_replans": 0,
            "successful_recoveries": 0,
            "total_tool_calls": 0,
            "successful_tool_calls": 0,
            "history": []
        }

    def _save_data(self, data: dict[str, Any]) -> None:
        dir_path = os.path.dirname(self.filepath)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        try:
            with tempfile.NamedTemporaryFile("w", dir=dir_path, delete=False, encoding="utf-8") as tf:
                json.dump(data, tf, indent=2, ensure_ascii=False)
                temp_name = tf.name
            os.replace(temp_name, self.filepath)
        except Exception as e:
            logging.warning(f"Aviso guardando métricas en {self.filepath}: {e}")

    def record_run(
        self,
        execution_level: str,
        user_goal: str,
        success: bool,
        elapsed_seconds: float,
        replans_count: int = 0,
        recovered_autonomously: bool = False,
        verification_results: dict[str, Any] = None,
        tool_calls_count: int = 0
    ) -> dict[str, Any]:
        """Registra el resultado de un ciclo de ejecución de la Máquina de Estados."""
        data = self._load_data()
        data["total_runs"] += 1
        if success:
            data["successful_runs"] += 1
        data["total_replans"] += replans_count
        if recovered_autonomously:
            data["successful_recoveries"] += 1
        data["total_tool_calls"] += tool_calls_count

        run_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "execution_level": execution_level,
            "user_goal": user_goal[:80],
            "success": success,
            "elapsed_seconds": elapsed_seconds,
            "replans_count": replans_count,
            "recovered_autonomously": recovered_autonomously,
            "verification": verification_results or {},
            "tool_calls_count": tool_calls_count
        }

        # Mantener historial reciente (últimas 100 ejecuciones)
        data["history"].insert(0, run_entry)
        data["history"] = data["history"][:100]

        self._save_data(data)
        return self.compute_summary()

    def record_tool_event(
        self,
        tool_name: str,
        success: bool,
        duration_seconds: float = 0.0,
        error_type: str | None = None
    ) -> None:
        """Registra la ejecución real de una herramienta por el agente."""
        data = self._load_data()
        data["total_tool_calls"] = data.get("total_tool_calls", 0) + 1
        if success:
            data["successful_tool_calls"] = data.get("successful_tool_calls", 0) + 1

        if "tool_events" not in data:
            data["tool_events"] = []

        event = {
            "tool_name": tool_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "success": success,
            "duration_seconds": round(duration_seconds, 3),
            "error_type": error_type or "None"
        }

        data["tool_events"].insert(0, event)
        data["tool_events"] = data["tool_events"][:200]
        self._save_data(data)

    def compute_summary(self) -> dict[str, Any]:
        """Calcula los KPIs cuantitativos agregados con datos reales."""
        data = self._load_data()
        total = data.get("total_runs", 0)
        total_tools = data.get("total_tool_calls", 0)
        success_tools = data.get("successful_tool_calls", 0)
        tool_success_rate = round((success_tools / total_tools) * 100, 1) if total_tools > 0 else 100.0

        if total == 0:
            return {
                "total_runs": 0,
                "task_success_rate_pct": 0.0,
                "tool_success_rate_pct": tool_success_rate,
                "total_tool_calls": total_tools,
                "autonomous_recovery_rate_pct": 0.0,
                "avg_replans_per_task": 0.0,
                "avg_elapsed_seconds": 0.0
            }

        success_count = data.get("successful_runs", 0)
        recoveries = data.get("successful_recoveries", 0)
        replans = data.get("total_replans", 0)

        history = data.get("history", [])
        avg_time = (
            sum(h.get("elapsed_seconds", 0) for h in history) / len(history)
            if history else 0.0
        )

        return {
            "total_runs": total,
            "task_success_rate_pct": round((success_count / total) * 100, 1),
            "tool_success_rate_pct": tool_success_rate,
            "total_tool_calls": total_tools,
            "autonomous_recovery_rate_pct": round((recoveries / max(1, replans)) * 100, 1) if replans > 0 else 100.0,
            "avg_replans_per_task": round(replans / total, 2),
            "avg_elapsed_seconds": round(avg_time, 2)
        }

    def get_benchmark_report_markdown(self) -> str:
        """Genera un reporte formateado en Markdown con los KPIs cuantitativos."""
        summary = self.compute_summary()
        data = self._load_data()
        history = data.get("history", [])[:5]

        lines = [
            "### 📊 Reporte Cuantitativo de Rendimiento & Benchmarks (CodeAgent v4.1)\n",
            f"- **Total de Tareas Ejecutadas:** `{summary['total_runs']}`",
            f"- **Tasa de Éxito de Tareas (Task Success Rate):** `{summary['task_success_rate_pct']}%`",
            f"- **Recuperación Autónoma (Autonomous Recovery Rate):** `{summary['autonomous_recovery_rate_pct']}%`",
            f"- **Promedio de Re-planificaciones / Tarea:** `{summary['avg_replans_per_task']}`",
            f"- **Tiempo Promedio de Ejecución:** `{summary['avg_elapsed_seconds']}s`\n",
            "#### 🕒 Últimas 5 Tareas Registradas:"
        ]

        if history:
            lines.append("| Fecha | Nivel | Objetivo | Éxito | Tiempo | Re-plans |")
            lines.append("| :--- | :--- | :--- | :---: | :---: | :---: |")
            for h in history:
                status = "✅ Pasado" if h.get("success") else "❌ Fallo"
                lines.append(
                    f"| {h.get('timestamp', '')} | {h.get('execution_level', '')} | {h.get('user_goal', '')[:30]}... | {status} | {h.get('elapsed_seconds', 0)}s | {h.get('replans_count', 0)} |"
                )
        else:
            lines.append("*No hay ejecuciones registradas en el historial.*")

        return "\n".join(lines)


# Singleton predeterminado de métricas
metrics_collector = BenchmarkMetricsCollector()
