import contextlib
import os
import tempfile
import unittest

from agent_pipeline import AgentStateMachineController
from runtime.runtime import CodeAgentRuntime
from storage.database import DatabaseManager


class TestVerifierEvidenceAndWorkspaceIsolation(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        with contextlib.suppress(Exception):
            self.temp_dir.cleanup()

    def test_verifier_returns_not_run_for_empty_workspace(self):
        empty_dir = os.path.join(self.temp_dir.name, "empty_proj")
        os.makedirs(empty_dir, exist_ok=True)

        controller = AgentStateMachineController(workspace_dir=empty_dir)
        verification = controller._stage_verifier()

        self.assertEqual(verification["ast_status"], "NOT_RUN")
        self.assertEqual(verification["ruff_status"], "NOT_RUN")
        self.assertEqual(verification["tests_status"], "NOT_RUN")
        self.assertEqual(verification["py_files_count"], 0)

        # Probar respuesta formateada
        response, metrics = controller.run(
            user_goal="Crear proyecto de prueba",
            session_id="session-test-empty-1"
        )
        self.assertIn("NO_CODE_FOUND", response)
        self.assertIn("NOT_RUN", response)

    def test_workspace_isolation_across_tasks(self):
        db_path = os.path.join(self.temp_dir.name, "test_workspace_db.db")
        db = DatabaseManager(db_path=db_path)
        runtime = CodeAgentRuntime(db_manager=db)

        proj_a = os.path.join(self.temp_dir.name, "proj_a")
        os.makedirs(proj_a, exist_ok=True)

        # Crear archivo en proj_a
        with open(os.path.join(proj_a, "main.py"), "w", encoding="utf-8") as f:
            f.write("print('Hello Project A')\n")

        task_id = runtime.start_task(goal="Desarrollar App A", project_path=proj_a)
        task_data = runtime.get_task(task_id)

        self.assertIsNotNone(task_data)
        self.assertEqual(os.path.abspath(task_data["project_path"]), os.path.abspath(proj_a))

        controller_a = AgentStateMachineController(workspace_dir=proj_a, db_manager=db)
        verification_a = controller_a._stage_verifier()
        self.assertEqual(verification_a["ast_status"], "PASS")
        self.assertEqual(verification_a["py_files_count"], 1)


if __name__ == "__main__":
    unittest.main()
