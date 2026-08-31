import os
import sys
import unittest
from unittest.mock import MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../mis_agentes_inteligentes')))

from agent_pipeline import AgentStateMachineController, ExecutionLevel, State
from session_manager import JSONSessionRepository


class TestStateCheckpointing(unittest.TestCase):

    def setUp(self):
        import tempfile
        os.environ["SKIP_SUBPROCESS_TESTS"] = "1"
        self.temp_dir = tempfile.TemporaryDirectory()
        self.controller = AgentStateMachineController(workspace_dir=self.temp_dir.name)
        self.repo = JSONSessionRepository()
        self.session_id = self.repo.create_session("Sesión de Prueba Checkpointing")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_checkpoint_and_resume_session(self):
        # 1. Simular guardado de checkpoint en estado REPLAN
        self.controller._save_checkpoint(
            session_id=self.session_id,
            current_state=State.REPLAN,
            execution_level=ExecutionLevel.LEVEL_4_FULL,
            user_goal="Implementar autenticación JWT",
            replans_count=1,
            failed_verification={"ast_errors": ["tests/test_auth.py: line 14 AssertionError"]}
        )

        # 2. Verificar que la sesión persistida contenga el checkpoint
        data = self.repo.load_session(self.session_id)
        self.assertIsNotNone(data)
        checkpoint = data.get("memory", {}).get("working", {}).get("state_checkpoint")
        self.assertIsNotNone(checkpoint)
        self.assertEqual(checkpoint["current_state"], State.REPLAN.value)
        self.assertEqual(checkpoint["user_goal"], "Implementar autenticación JWT")

        # 3. Reanudar la sesión desde el checkpoint persistido
        mock_runner = MagicMock(return_value="Respuesta de reanudación")
        response, metrics = self.controller.resume_session(
            session_id=self.session_id,
            agent_runner=mock_runner
        )

        self.assertIn("Task Result", response)
        self.assertEqual(metrics["execution_level"], ExecutionLevel.LEVEL_4_FULL.value)
        self.assertTrue(metrics["verifier_passed"])

    def test_resume_session_not_found(self):
        response, metrics = self.controller.resume_session(session_id="id-inexistente-12345")
        self.assertIn("Error", response)
        self.assertEqual(metrics, {})


if __name__ == "__main__":
    unittest.main()
