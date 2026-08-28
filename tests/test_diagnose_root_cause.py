import os
import unittest
from unittest.mock import MagicMock

from agent_pipeline import CODEAGENT_VERSION, AgentStateMachineController, ExecutionLevel
from session_manager import JSONSessionRepository


class TestDiagnoseRootCauseAndVersion(unittest.TestCase):

    def setUp(self):
        os.environ["SKIP_SUBPROCESS_TESTS"] = "1"
        self.controller = AgentStateMachineController()
        self.repo = JSONSessionRepository()
        self.session_id = self.repo.create_session("Sesión RootCause & Replan")

    def test_version_unification_constant(self):
        self.assertEqual(CODEAGENT_VERSION, "v4.4 Enterprise")

    def test_stage_diagnose_generates_root_cause_report(self):
        verification_res = {
            "success": False,
            "ast_valid": False,
            "ast_errors": ["ModuleNotFoundError: No module named 'invalid_dep'"]
        }

        report = self.controller._stage_diagnose(verification_res, "Refactorizar modulo")
        self.assertIn("invalid_dep", report["root_cause"])
        self.assertTrue(report["requires_reexploration"])
        self.assertIn("strategy_change", report)

    def test_stage_replan_generates_updated_plan(self):
        initial_plan = {"objetivo": "Crear feature", "pasos": ["1. Paso inicial"]}
        diagnostic_report = {
            "root_cause": "SyntaxError",
            "strategy_change": "Ajustar parentesis en linea 4",
            "requires_reexploration": False
        }

        updated = self.controller._stage_replan(initial_plan, diagnostic_report)
        self.assertIn("pasos", updated)
        self.assertEqual(len(updated["pasos"]), 2)
        self.assertIn("AJUSTE ESTRATÉGICO", updated["pasos"][1])
        self.assertEqual(updated["diagnostic_report"], diagnostic_report)

    def test_full_diagnose_and_replan_checkpoint_persistence(self):
        mock_runner = MagicMock(return_value="Respuesta de ejecucion con reparacion")
        response, metrics = self.controller.run(
            user_goal="Refactoriza módulo X",
            agent_runner=mock_runner,
            level=ExecutionLevel.LEVEL_4_FULL,
            session_id=self.session_id
        )

        self.assertIn("Resultado Agéntico v4.4 Enterprise", response)

        # Cargar checkpoint guardado en sesión
        session_data = self.repo.load_session(self.session_id)
        self.assertIsNotNone(session_data)
        checkpoint = session_data.get("memory", {}).get("working", {}).get("state_checkpoint")
        self.assertIsNotNone(checkpoint)
        self.assertIn("current_state", checkpoint)


if __name__ == "__main__":
    unittest.main()
