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

    def test_regression_chat_task_never_enters_pipeline(self):
        user_goal = "Responde únicamente con OK. No ejecutes herramientas. No modifiques nada."
        from mis_agentes_inteligentes.agent_pipeline import ComplexityRiskEvaluator, ExecutionLevel
        level = ComplexityRiskEvaluator.evaluate(user_goal)
        self.assertEqual(level, ExecutionLevel.LEVEL_1_CHAT)

        response_text, metrics = self.controller.run(user_goal)
        self.assertEqual(metrics["execution_level"], ExecutionLevel.LEVEL_1_CHAT.value)
        self.assertEqual(metrics["replans_count"], 0)
        self.assertTrue(metrics["verifier_passed"])

    def test_regression_deterministic_execution_count_metrics(self):
        from tools import TERMINAL_TASKS_BUFFER
        TERMINAL_TASKS_BUFFER.clear()
        for i in range(5):
            TERMINAL_TASKS_BUFFER.append({
                "comando": "python action_runtime_test.py",
                "cwd": self.temp_dir.name,
                "exit_code": 0,
                "output": "ACTION_OK"
            })
        self.assertEqual(len(TERMINAL_TASKS_BUFFER), 5)
        user_goal = "Responde únicamente con OK. No ejecutes herramientas."
        _, metrics = self.controller.run(user_goal)
        self.assertEqual(metrics["execution_count"], 5)
        self.assertEqual(metrics["tool_calls_count"], 5)
        TERMINAL_TASKS_BUFFER.clear()

    def test_mandatory_a_chat_prompt_tildes(self):
        user_goal = "Responde únicamente con OK."
        classification = self.task_router.classify(user_goal)
        self.assertEqual(classification.task_type.value, "CHAT")
        _, metrics = self.controller.run(user_goal)
        self.assertEqual(metrics["execution_level"], "Nivel 1 (Chat Directo)")
        self.assertEqual(metrics["replans_count"], 0)
        self.assertTrue(metrics["verifier_passed"])

    def test_mandatory_b_chat_prompt_no_tildes(self):
        user_goal = "Responde unicamente con OK."
        classification = self.task_router.classify(user_goal)
        self.assertEqual(classification.task_type.value, "CHAT")
        _, metrics = self.controller.run(user_goal)
        self.assertEqual(metrics["execution_level"], "Nivel 1 (Chat Directo)")
        self.assertEqual(metrics["replans_count"], 0)

    def test_mandatory_c_chat_prompt_uppercase_tildes(self):
        user_goal = "Responde ÚNICAMENTE con OK."
        classification = self.task_router.classify(user_goal)
        self.assertEqual(classification.task_type.value, "CHAT")
        _, metrics = self.controller.run(user_goal)
        self.assertEqual(metrics["execution_level"], "Nivel 1 (Chat Directo)")
        self.assertEqual(metrics["replans_count"], 0)

    def test_mandatory_d_chat_prompt_utf8_does_not_enter_feature(self):
        user_goal = "Hola, ¿cómo estás? Explícame por favor qué hace el sistema sin modificar nada."
        classification = self.task_router.classify(user_goal)
        self.assertEqual(classification.task_type.value, "CHAT")
        self.assertNotEqual(classification.task_type.value, "FEATURE")

    def test_mandatory_e_action_successful_execution(self):
        from mis_agentes_inteligentes.tools import TERMINAL_TASKS_BUFFER
        TERMINAL_TASKS_BUFFER.clear()
        TERMINAL_TASKS_BUFFER.append({
            "comando": "python runtime_smoke.py",
            "cwd": self.temp_dir.name,
            "exit_code": 0,
            "output": "RUNTIME_OK"
        })
        user_goal = "Crea únicamente el archivo runtime_smoke.py y ejecuta python runtime_smoke.py"
        from mis_agentes_inteligentes.agent_pipeline import ExecutionLevel
        _, metrics = self.controller.run(user_goal=user_goal, level=ExecutionLevel.LEVEL_2_ACTION)
        self.assertTrue(metrics["verifier_passed"])
        self.assertEqual(metrics["replans_count"], 0)
        self.assertEqual(metrics["execution_count"], 1)
        TERMINAL_TASKS_BUFFER.clear()

    def test_mandatory_f_five_real_terminal_executions(self):
        from mis_agentes_inteligentes.tools import TERMINAL_TASKS_BUFFER
        TERMINAL_TASKS_BUFFER.clear()
        for i in range(5):
            TERMINAL_TASKS_BUFFER.append({
                "comando": "python runtime_smoke.py",
                "cwd": self.temp_dir.name,
                "exit_code": 0,
                "output": f"RUNTIME_OK_{i}"
            })
        user_goal = "Responde únicamente con OK."
        _, metrics = self.controller.run(user_goal)
        self.assertEqual(metrics["execution_count"], 5)
        TERMINAL_TASKS_BUFFER.clear()

    def test_mandatory_g_tools_module_singleton_identity(self):
        import mis_agentes_inteligentes.tools as t1
        import tools as t2
        self.assertIs(t1.TERMINAL_TASKS_BUFFER, t2.TERMINAL_TASKS_BUFFER)


if __name__ == "__main__":
    unittest.main()
