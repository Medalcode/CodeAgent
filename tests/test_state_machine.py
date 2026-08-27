import unittest
from unittest.mock import MagicMock

from agent_pipeline import AgentStateMachineController, ExecutionLevel
from benchmark_metrics import BenchmarkMetricsCollector


class TestAgentStateMachineController(unittest.TestCase):

    def setUp(self):
        import os
        os.environ["SKIP_SUBPROCESS_TESTS"] = "1"
        self.controller = AgentStateMachineController()

    def test_infer_execution_level_level_1_chat(self):
        goal = "¿Qué hace esta función y cómo se configura?"
        level = self.controller.infer_execution_level(goal)
        self.assertEqual(level, ExecutionLevel.LEVEL_1_CHAT)

    def test_infer_execution_level_level_2_action(self):
        goal = "Añade un comentario en la cabecera del archivo utils.py"
        level = self.controller.infer_execution_level(goal)
        self.assertEqual(level, ExecutionLevel.LEVEL_2_ACTION)

    def test_infer_execution_level_level_3_feature(self):
        goal = "Crea un nuevo endpoint /api/stats en localcode_server.py"
        level = self.controller.infer_execution_level(goal)
        self.assertEqual(level, ExecutionLevel.LEVEL_3_FEATURE)

    def test_infer_execution_level_level_4_full(self):
        goal = "Refactoriza el módulo de autenticación y resuelve los linter warnings"
        level = self.controller.infer_execution_level(goal)
        self.assertEqual(level, ExecutionLevel.LEVEL_4_FULL)

    def test_run_level_1_chat_fast_path(self):
        mock_runner = MagicMock(return_value="Respuesta de prueba")
        response, metrics = self.controller.run(
            user_goal="¿Qué hace la función main?",
            agent_runner=mock_runner,
            level=ExecutionLevel.LEVEL_1_CHAT
        )
        self.assertIn("Respuesta de prueba", response)
        self.assertEqual(metrics["execution_level"], ExecutionLevel.LEVEL_1_CHAT.value)
        self.assertTrue(metrics["verifier_passed"])

    def test_run_level_4_replan_loop(self):
        # Simular runner que arregla el código en el segundo intento
        calls = []

        def mock_runner(prompt):
            calls.append(prompt)
            return f"Ejecución paso {len(calls)}"

        response, metrics = self.controller.run(
            user_goal="Refactoriza el parser de expresiones",
            agent_runner=mock_runner,
            level=ExecutionLevel.LEVEL_4_FULL
        )

        self.assertIn("Control de Estados Determinista", response)
        self.assertEqual(metrics["execution_level"], ExecutionLevel.LEVEL_4_FULL.value)

    def test_benchmark_metrics_collector(self):
        collector = BenchmarkMetricsCollector()
        summary = collector.compute_summary()
        self.assertIn("task_success_rate_pct", summary)
        self.assertIn("autonomous_recovery_rate_pct", summary)


if __name__ == "__main__":
    unittest.main()
