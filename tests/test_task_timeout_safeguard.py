import contextlib
import os
import tempfile
import time
import unittest

from runtime.runtime import CodeAgentRuntime
from storage.database import DatabaseManager
from tools import ejecutar_comando_terminal


class TestTaskTimeoutSafeguardAndCancellation(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_timeout_db.db")
        self.db = DatabaseManager(db_path=self.db_path)
        self.runtime = CodeAgentRuntime(db_manager=self.db)

    def tearDown(self):
        with contextlib.suppress(Exception):
            self.temp_dir.cleanup()

    def test_subprocess_stdin_devnull(self):
        # Ejecutar comando que consulte el sistema
        res = ejecutar_comando_terminal("echo DEVNULL_CHECK")
        self.assertIn("DEVNULL_CHECK", res)
        self.assertIn("✅ Éxito", res)

    def test_runtime_cancel_task_safeguard(self):
        def hanging_runner(_prompt):
            time.sleep(1.0)
            return "Hanging execution"

        task_id = self.runtime.start_task(
            goal="Ejecución de larga duración",
            project_path=self.temp_dir.name,
            agent_runner=hanging_runner
        )

        time.sleep(0.15)
        canceled = self.runtime.cancel_task(task_id)
        self.assertTrue(canceled)

        task = self.runtime.get_task(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task["status"], "CANCELLED")


if __name__ == "__main__":
    unittest.main()
