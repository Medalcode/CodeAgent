"""
Tests de regresión de negaciones para TaskRouter y ComplexityRiskEvaluator.
Verifica que las restricciones secundarias no cancelen las acciones primarias positivas.
"""
import unittest
from sdd_contract.task_router import TaskRouter, TaskType
from mis_agentes_inteligentes.agent_pipeline import ComplexityRiskEvaluator, ExecutionLevel


class TestTaskRouterNegations(unittest.TestCase):

    def setUp(self):
        self.router = TaskRouter()

    def test_case_a_chat(self):
        """Caso A — CHAT: Directiva de conversación con prohibiciones primarias."""
        prompt = "Responde únicamente con OK. No ejecutes ninguna herramienta. No crees archivos."
        classification = self.router.classify(prompt)
        contract = ComplexityRiskEvaluator.build_contract(prompt)

        self.assertEqual(classification.task_type.value, "CHAT")
        self.assertEqual(contract.task_type.value, "CHAT")
        self.assertEqual(contract.execution_level, ExecutionLevel.LEVEL_1_CHAT)
        self.assertFalse(contract.tools_allowed)

    def test_case_b_action_with_secondary_constraints(self):
        """Caso B — ACTION: Acción primaria con prohibiciones secundarias de verificadores."""
        prompt = "Crea action_final.py y ejecuta python action_final.py. No ejecutes pytest, Ruff ni análisis AST."
        classification = self.router.classify(prompt)
        contract = ComplexityRiskEvaluator.build_contract(prompt)

        self.assertEqual(classification.task_type.value, "ACTION")
        self.assertEqual(contract.task_type.value, "ACTION")
        self.assertEqual(contract.execution_level, ExecutionLevel.LEVEL_2_ACTION)
        self.assertTrue(contract.tools_allowed)

    def test_case_c_action_uppercase_accents(self):
        """Caso C — ACTION: Mayúsculas y acentos con prohibición de linter/AST."""
        prompt = "CREA action_final.py. EJECÚTALO. No ejecutes RUFF ni análisis AST."
        classification = self.router.classify(prompt)
        contract = ComplexityRiskEvaluator.build_contract(prompt)

        self.assertEqual(classification.task_type.value, "ACTION")
        self.assertEqual(contract.task_type.value, "ACTION")
        self.assertEqual(contract.execution_level, ExecutionLevel.LEVEL_2_ACTION)

    def test_case_d_chat_negated_mutational_verbs(self):
        """Caso D — CHAT: Verbos mutacionales negados."""
        prompt = "Responde OK. No crees, modifiques, borres ni ejecutes ningún archivo."
        classification = self.router.classify(prompt)
        contract = ComplexityRiskEvaluator.build_contract(prompt)

        self.assertEqual(classification.task_type.value, "CHAT")
        self.assertEqual(contract.task_type.value, "CHAT")
        self.assertEqual(contract.execution_level, ExecutionLevel.LEVEL_1_CHAT)

    def test_case_e_chat_explicit_prohibition_primary_action(self):
        """Caso E — CHAT: Prohibición explícita de acción primaria."""
        prompt = "No crees archivos. No ejecutes comandos. Responde únicamente OK."
        classification = self.router.classify(prompt)
        contract = ComplexityRiskEvaluator.build_contract(prompt)

        self.assertEqual(classification.task_type.value, "CHAT")
        self.assertEqual(contract.task_type.value, "CHAT")
        self.assertEqual(contract.execution_level, ExecutionLevel.LEVEL_1_CHAT)

    def test_full_action_prompt_requirement_4(self):
        """Prueba del prompt ACTION exacto del requerimiento 4."""
        prompt = (
            'Crea únicamente action_final.py con este contenido exacto: print("ACTION_OK"). '
            'Ejecuta exactamente: python action_final.py. Verifica que el código de salida sea 0 '
            'y stdout sea exactamente ACTION_OK. No ejecutes pytest, unittest, Ruff ni análisis AST. '
            'No hagas replanificación si la ejecución es correcta. No crees ningún otro archivo. Termina inmediatamente.'
        )
        classification = self.router.classify(prompt)
        contract = ComplexityRiskEvaluator.build_contract(prompt)

        self.assertEqual(classification.task_type.value, "ACTION")
        self.assertEqual(contract.task_type.value, "ACTION")
        self.assertEqual(contract.execution_level, ExecutionLevel.LEVEL_2_ACTION)


if __name__ == "__main__":
    unittest.main()
