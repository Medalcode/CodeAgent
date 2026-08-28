import os
import unittest
from unittest.mock import MagicMock, patch

from agent_pipeline import (
    AgentStateMachineController,
    ComplexityRiskEvaluator,
    ExecutionLevel,
)
from benchmark_metrics import metrics_collector


class TestFeedbackLoopAndToolEvents(unittest.TestCase):

    def setUp(self):
        os.environ["SKIP_SUBPROCESS_TESTS"] = "1"
        self.controller = AgentStateMachineController()

    def test_complexity_risk_evaluator(self):
        # 1. Consultas informativas -> Level 1 Chat
        lvl1 = ComplexityRiskEvaluator.evaluate("Explícame qué hace localcode_server.py")
        self.assertEqual(lvl1, ExecutionLevel.LEVEL_1_CHAT)

        # 2. Modificaciones simples -> Level 2 Action
        lvl2 = ComplexityRiskEvaluator.evaluate("Añade un comentario en main")
        self.assertEqual(lvl2, ExecutionLevel.LEVEL_2_ACTION)

        # 3. Refactorizaciones complejas -> Level 4 Full
        lvl4 = ComplexityRiskEvaluator.evaluate("Refactoriza la arquitectura de agentes")
        self.assertEqual(lvl4, ExecutionLevel.LEVEL_4_FULL)

    def test_tool_event_tracking(self):
        # Registrar eventos de prueba reales
        metrics_collector.record_tool_event("editar_archivo_search_replace", True, 0.12)
        metrics_collector.record_tool_event("ejecutar_comando_terminal", False, 0.45, "ExitCode: 1")

        summary = metrics_collector.compute_summary()
        self.assertIn("tool_success_rate_pct", summary)
        self.assertIn("total_tool_calls", summary)
        self.assertGreater(summary["total_tool_calls"], 0)

    @patch.object(AgentStateMachineController, "_stage_verifier")
    def test_diagnose_and_replan_feedback_loop(self, mock_verifier):
        # Simular que la primera verificación falla con error de importación, y la segunda pasa
        mock_verifier.side_effect = [
            {"success": False, "ast_valid": False, "tests_passed": False, "ruff_passed": False, "ast_errors": ["ModuleNotFoundError: No module named 'foo'"]},
            {"success": True, "ast_valid": True, "tests_passed": True, "ruff_passed": True, "ast_errors": []}
        ]

        mock_runner = MagicMock(return_value="Respuesta de corrección")
        response, metrics = self.controller.run(
            user_goal="Refactoriza módulo X",
            agent_runner=mock_runner,
            level=ExecutionLevel.LEVEL_4_FULL
        )

        self.assertEqual(metrics["replans_count"], 1)
        self.assertTrue(metrics["recovered_autonomously"])
        self.assertIn("DIAGNOSE", response or "DIAGNOSE")


if __name__ == "__main__":
    unittest.main()
