import os
import tempfile
import unittest

from runtime.event_bus import EventBus
from runtime.runtime import CodeAgentRuntime
from storage.database import DatabaseManager


class TestRuntimeAndStorage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_codeagent.db")
        self.db = DatabaseManager(db_path=self.db_path)
        self.bus = EventBus(db_manager=self.db)
        self.runtime = CodeAgentRuntime(db_manager=self.db, event_bus=self.bus)

    def tearDown(self):
        import contextlib
        with contextlib.suppress(Exception):
            self.temp_dir.cleanup()

    def test_database_task_crud(self):
        task = self.db.create_task("task-123", self.temp_dir.name, "Fix login bug", "LEVEL_3_FEATURE")
        self.assertIsNotNone(task)
        self.assertEqual(task["id"], "task-123")
        self.assertEqual(task["status"], "CREATED")
        self.assertEqual(task["current_state"], "INIT")

        self.db.update_task_status("task-123", "RUNNING", current_state="EXECUTE")
        updated = self.db.get_task("task-123")
        self.assertEqual(updated["status"], "RUNNING")
        self.assertEqual(updated["current_state"], "EXECUTE")

        tasks = self.db.list_tasks()
        self.assertEqual(len(tasks), 1)

    def test_event_bus_publishing_and_sourcing(self):
        received_events = []

        def on_event(evt):
            received_events.append(evt)

        self.bus.subscribe(on_event)

        self.db.create_task("task-456", self.temp_dir.name, "Build dashboard", "LEVEL_4_FULL")
        self.bus.publish("task-456", "PLAN_CREATED", {"plan": "Step 1, Step 2"})

        self.assertEqual(len(received_events), 1)
        self.assertEqual(received_events[0].event_type, "PLAN_CREATED")
        self.assertEqual(received_events[0].payload["plan"], "Step 1, Step 2")

        # Test Event Sourcing retrieval from SQLite
        events_from_db = self.bus.get_events("task-456")
        self.assertEqual(len(events_from_db), 1)
        self.assertEqual(events_from_db[0]["event_type"], "PLAN_CREATED")

    def test_runtime_start_and_get_task(self):
        def dummy_runner(_prompt):
            return "Execution successful"

        task_id = self.runtime.start_task(
            goal="Formatea el codigo",
            project_path=self.temp_dir.name,
            agent_runner=dummy_runner
        )
        self.assertIsNotNone(task_id)

        task = self.runtime.get_task(task_id)
        self.assertIsNotNone(task)
        self.assertIn(task["status"], ("CREATED", "RUNNING", "COMPLETED"))


if __name__ == "__main__":
    unittest.main()
