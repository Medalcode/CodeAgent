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
        with tempfile.NamedTemporaryFile("w", dir=dir_path, delete=False, encoding="utf-8") as tf:
            json.dump(data, tf, indent=2, ensure_ascii=False)
            temp_name = tf.name
        os.replace(temp_name, self.filepath)

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

    def compute_summary(self) -> dict[str, Any]:
        """Calcula los KPIs cuantitativos agregados."""
        data = self._load_data()
        total = data.get("total_runs", 0)
        if total == 0:
            return {
                "total_runs": 0,
                "task_success_rate_pct": 0.0,
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
            "autonomous_recovery_rate_pct": round((recoveries / max(1, replans)) * 100, 1) if replans > 0 else 100.0,
            "avg_replans_per_task": round(replans / total, 2),
            "avg_elapsed_seconds": round(avg_time, 2)
        }


# Singleton predeterminado de métricas
metrics_collector = BenchmarkMetricsCollector()
