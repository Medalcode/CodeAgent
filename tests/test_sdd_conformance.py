import contextlib
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mis_agentes_inteligentes.agent_pipeline import AgentStateMachineController
from sdd_contract.evidence_logger import EvidenceLogger
from sdd_contract.task_contract import ActionTaskContract, ChatTaskContract
from sdd_contract.task_router import TaskRouter
from sdd_contract.ui_manager import UIManager
from sdd_contract.verification_engine import VerificationCriterion, VerificationEngine


class TestSDDConformance(unittest.TestCase):
    def setUp(self):
        os.environ["SKIP_SUBPROCESS_TESTS"] = "1"
        self.temp_dir = tempfile.TemporaryDirectory()
        self.controller = AgentStateMachineController(workspace_dir=self.temp_dir.name)
        self.task_router = TaskRouter()

    def tearDown(self):
        with contextlib.suppress(Exception):
            self.temp_dir.cleanup()

    def test_requirement_1_classifies_chat_task_correctly(self):
        user_goal = "Responde unicamente con OK. No ejecutes herramientas."
        classification = self.task_router.classify(user_goal)
        self.assertEqual(classification.task_type.value, "CHAT")
        self.assertGreater(classification.confidence, 0.8)

    def test_requirement_1_classifies_action_task_correctly(self):
        user_goal = "Crea un archivo test.py con contenido."
        classification = self.task_router.classify(user_goal)
        self.assertEqual(classification.task_type.value, "ACTION")

    def test_requirement_2_chat_task_contract(self):
        contract = ChatTaskContract()
        self.assertFalse(contract.can_verify())
        self.assertFalse(contract.can_replan())
        self.assertEqual(contract.get_max_iterations(), 1)

    def test_requirement_3_action_task_contract(self):
        contract = ActionTaskContract()
        self.assertTrue(contract.can_verify())
        self.assertTrue(contract.can_replan())
        self.assertEqual(contract.get_max_iterations(), 3)

    def test_requirement_6_verification_states(self):
        engine = VerificationEngine()
        criteria = [
            VerificationCriterion(
                id="c1", name="Test 1", description="Test 1", required=True, expected="PASS"
            ),
            VerificationCriterion(
                id="c2", name="Test 2", description="Test 2", required=False, expected="PASS"
            ),
        ]
        results = {"c1": "PASS", "c2": "NOT_REQUIRED"}
        verification_result = engine.verify(criteria, results)
        self.assertTrue(verification_result.success)

    def test_requirement_7_evidence_logger(self):
        logger = EvidenceLogger()
        evidence = logger.log_verification_fail(
            task_id="test-123",
            criterion_name="test_execution",
            expected="exit_code=0",
            actual="exit_code=1",
            difference="Program returned non-zero exit code"
        )
        self.assertIsNotNone(evidence)
        self.assertEqual(evidence.task_id, "test-123")

    def test_requirement_10_ui_manager_single_instance(self):
        ui_manager = UIManager()
        ui_manager.create_instance("session-123", "console")
        with self.assertRaises(ValueError):
            ui_manager.create_instance("session-123", "window")


if __name__ == "__main__":
    unittest.main()
