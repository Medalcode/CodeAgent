import contextlib
import os
import tempfile
import time
import unittest

from runtime.event_bus import EventBus
from runtime.runtime import CodeAgentRuntime
from storage.database import DatabaseManager


class TestRuntimeRecoveryAndPauseSemantics(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_recovery_codeagent.db")
        self.db = DatabaseManager(db_path=self.db_path)
        self.bus = EventBus(db_manager=self.db)
        self.runtime = CodeAgentRuntime(db_manager=self.db, event_bus=self.bus)

    def tearDown(self):
        with contextlib.suppress(Exception):
            self.temp_dir.cleanup()

    def test_pause_vs_cancel_semantics(self):
        def slow_runner(_prompt):
            time.sleep(0.1)
            return "Slow execution step"

        # 1. Test Pause
        task_id = self.runtime.start_task(
            goal="Refactoriza el modulo auth",
            project_path=self.temp_dir.name,
            agent_runner=slow_runner
        )

        res_pause = self.runtime.pause_task(task_id)
        self.assertTrue(res_pause)

        task_after_pause = self.runtime.get_task(task_id)
        self.assertIsNotNone(task_after_pause)
        self.assertEqual(task_after_pause["status"], "PAUSED")

        # 2. Test Cancel
        task_id2 = self.runtime.start_task(
            goal="Genera reportes de pruebas",
            project_path=self.temp_dir.name,
            agent_runner=slow_runner
        )
        time.sleep(0.05)
        res_cancel = self.runtime.cancel_task(task_id2)
        self.assertTrue(res_cancel)

        task_after_cancel = self.runtime.get_task(task_id2)
        self.assertIsNotNone(task_after_cancel)
        self.assertEqual(task_after_cancel["status"], "CANCELLED")

    def test_intermediate_checkpoints_per_phase(self):
        from agent_pipeline import AgentStateMachineController, ExecutionLevel, State

        controller = AgentStateMachineController(workspace_dir=self.temp_dir.name, db_manager=self.db, event_bus=self.bus)
        task_id = "task-checkpoints-101"
        self.db.create_task(task_id, self.temp_dir.name, "Actualizar dependencias", "LEVEL_4_FULL")

        # Simular transiciones de fase
        controller._save_checkpoint(task_id, State.PLAN, ExecutionLevel.LEVEL_4_FULL, "Actualizar dependencias", 0)
        chk_plan = self.db.get_latest_checkpoint(task_id)
        self.assertEqual(chk_plan["state"], "PLAN")

        controller._save_checkpoint(task_id, State.EXECUTE, ExecutionLevel.LEVEL_4_FULL, "Actualizar dependencias", 0)
        chk_exec = self.db.get_latest_checkpoint(task_id)
        self.assertEqual(chk_exec["state"], "EXECUTE")

        controller._save_checkpoint(task_id, State.VERIFY, ExecutionLevel.LEVEL_4_FULL, "Actualizar dependencias", 0)
        chk_ver = self.db.get_latest_checkpoint(task_id)
        self.assertEqual(chk_ver["state"], "VERIFY")

    def test_ui_disconnect_does_not_cancel_task(self):
        # Simula que la UI se cierra pero la tarea sigue registrada y activa en SQLite
        task_id = self.db.create_task("task-headless-999", self.temp_dir.name, "Tarea de fondo", "LEVEL_3_FEATURE")["id"]
        self.db.update_task_status(task_id, "RUNNING", current_state="EXECUTE")
        self.db.save_checkpoint(task_id, "EXECUTE", plan="Plan headless", failed_verification=None, replans_count=0)

        # Simular reconexión de UI consultando SQLite directamente
        reconnected_task = self.runtime.get_task(task_id)
        self.assertIsNotNone(reconnected_task)
        self.assertEqual(reconnected_task["status"], "RUNNING")
        self.assertEqual(reconnected_task["checkpoint"]["state"], "EXECUTE")

    def test_task_recovery_from_checkpoint(self):
        task_id = self.db.create_task("task-resume-202", self.temp_dir.name, "Reanudar tarea", "LEVEL_4_FULL")["id"]
        self.db.save_checkpoint(task_id, "EXECUTE", plan="Plan de reanudación", failed_verification=None, replans_count=1)
        self.db.update_task_status(task_id, "PAUSED", current_state="EXECUTE")

        def mock_runner(_prompt):
            return "Reanudación exitosa"

        resumed = self.runtime.resume_task(task_id, agent_runner=mock_runner)
        self.assertTrue(resumed)

        time.sleep(0.2)
        task_after = self.runtime.get_task(task_id)
        self.assertIn(task_after["status"], ("RUNNING", "COMPLETED"))


if __name__ == "__main__":
    unittest.main()
