import os
import shutil
import tempfile
import unittest

from agent_pipeline import AgentStateMachineController
from runtime.event_bus import get_event_bus
from storage.database import get_db_manager


class TestTDDRecoveryLoop(unittest.TestCase):
    """Verifica la capacidad de autorecuperación TDD (FAIL -> DIAGNOSE -> REPLAN -> FIX -> PASS)."""

    def setUp(self):
        self.workspace_dir = tempfile.mkdtemp(prefix="codeagent_tdd_test_")
        with open(os.path.join(self.workspace_dir, "calculator.py"), "w", encoding="utf-8") as f:
            f.write('"""Modulo calculadora."""\n\n\ndef sumar(a: int, b: int) -> int:\n    """Devuelve la suma."""\n    return a - b  # BUG DELIBERADO\n')

        self.event_bus = get_event_bus()
        self.db = get_db_manager()

    def tearDown(self):
        shutil.rmtree(self.workspace_dir, ignore_errors=True)

    def test_tdd_recovery_flow(self):
        states_visited = []

        def on_event(event):
            if getattr(event, "event_type", "") == "STATE_ENTERED":
                states_visited.append(getattr(event, "payload", {}).get("state"))

        self.event_bus.subscribe(on_event)

        call_count = [0]

        def mock_runner(_prompt: str) -> str:
            call_count[0] += 1
            if call_count[0] == 1:
                tests_dir = os.path.join(self.workspace_dir, "tests")
                os.makedirs(tests_dir, exist_ok=True)
                with open(os.path.join(tests_dir, "test_calculator.py"), "w", encoding="utf-8") as f:
                    f.write('"""Suite de pruebas."""\nimport unittest\nfrom calculator import sumar\n\n\nclass TestCalc(unittest.TestCase):\n    """Pruebas."""\n\n    def test_sumar(self):\n        """Prueba sumar."""\n        self.assertEqual(sumar(5, 3), 8)\n')
                return "Creado test"
            else:
                with open(os.path.join(self.workspace_dir, "calculator.py"), "w", encoding="utf-8") as f:
                    f.write('"""Modulo calculadora."""\n\n\ndef sumar(a: int, b: int) -> int:\n    """Devuelve la suma."""\n    return a + b\n')
                return "Bug corregido"

        goal = "Analiza el proyecto bug_test. Añade una prueba para sumar. Si falla, identifica la causa, corrige la implementación y vuelve a ejecutar."
        controller = AgentStateMachineController(workspace_dir=self.workspace_dir, db_manager=self.db, event_bus=self.event_bus, max_replans=2)

        old_skip = os.environ.pop("SKIP_SUBPROCESS_TESTS", None)
        try:
            output, metrics = controller.run(user_goal=goal, agent_runner=mock_runner, session_id="tdd_unit_test")
            verif = controller._stage_verifier(goal)
        finally:
            if old_skip is not None:
                os.environ["SKIP_SUBPROCESS_TESTS"] = old_skip

        self.event_bus.unsubscribe(on_event)

        self.assertIn("DIAGNOSE", states_visited)
        self.assertIn("REPLAN", states_visited)
        self.assertEqual(verif["tests_status"], "PASS")


if __name__ == "__main__":
    unittest.main()
