"""
Tests de canonicalización del TaskContract.
Verifica que el evaluador de complejidad retorne contratos canónicos
de sdd_contract en lugar de implementaciones locales duplicadas.
"""
import unittest
from sdd_contract.task_types import TaskType
from sdd_contract.task_contract import ChatTaskContract, ActionTaskContract, FeatureTaskContract
from mis_agentes_inteligentes.agent_pipeline import ComplexityRiskEvaluator, ExecutionLevel, _ContractWrapper


class TestTaskContractCanonical(unittest.TestCase):
    """Verifica que build_contract() use la autoridad canónica sdd_contract."""

    def setUp(self):
        self.evaluator = ComplexityRiskEvaluator()

    def test_task_type_proviene_de_sdd_contract(self):
        """TaskType debe importarse y usarse desde sdd_contract.task_types."""
        self.assertEqual(TaskType.CHAT.value, "CHAT")
        self.assertEqual(TaskType.ACTION.value, "ACTION")
        self.assertEqual(TaskType.FEATURE.value, "FEATURE")

    def test_build_contract_returns_chat_contract(self):
        """Chat tasks deben retornar un wrapper sobre ChatTaskContract canónico."""
        contract = self.evaluator.build_contract("responde únicamente con OK")
        self.assertIsInstance(contract, _ContractWrapper)
        # Verificar a través del wrapper que los atributos esperados están presentes
        self.assertEqual(contract.task_type, TaskType.CHAT)
        self.assertEqual(contract.execution_level, ExecutionLevel.LEVEL_1_CHAT)
        self.assertFalse(contract.requires_code_verification)
        self.assertFalse(contract.requires_tests)
        self.assertFalse(contract.requires_execution)
        self.assertFalse(contract.tools_allowed)
        self.assertFalse(contract.files_allowed)

    def test_build_contract_returns_action_contract(self):
        """Action tasks deben retornar un wrapper sobre ActionTaskContract canónico."""
        contract = self.evaluator.build_contract("crea action_final.py y ejecútalo")
        self.assertIsInstance(contract, _ContractWrapper)
        self.assertEqual(contract.task_type, TaskType.ACTION)
        self.assertEqual(contract.execution_level, ExecutionLevel.LEVEL_2_ACTION)
        self.assertTrue(contract.requires_code_verification)
        self.assertFalse(contract.requires_tests)
        self.assertTrue(contract.requires_execution)
        self.assertTrue(contract.tools_allowed)
        self.assertTrue(contract.files_allowed)

    def test_build_contract_returns_feature_contract(self):
        """Feature tasks deben retornar un wrapper sobre FeatureTaskContract canónico."""
        contract = self.evaluator.build_contract("implementa un sistema completo de autenticación")
        self.assertIsInstance(contract, _ContractWrapper)
        self.assertEqual(contract.task_type, TaskType.FEATURE)
        self.assertEqual(contract.execution_level, ExecutionLevel.LEVEL_3_FEATURE)
        self.assertTrue(contract.requires_code_verification)
        self.assertTrue(contract.requires_tests)
        self.assertTrue(contract.requires_execution)
        self.assertTrue(contract.tools_allowed)
        self.assertTrue(contract.files_allowed)

    def test_compatibility_properties_chat(self):
        """Propiedades de compatibilidad para tareas CHAT."""
        contract = self.evaluator.build_contract("responde ok")
        self.assertFalse(contract.requires_code_verification)
        self.assertFalse(contract.requires_tests)
        self.assertFalse(contract.requires_execution)
        self.assertFalse(contract.tools_allowed)
        self.assertFalse(contract.files_allowed)

    def test_compatibility_properties_action(self):
        """Propiedades de compatibilidad para tareas ACTION."""
        contract = self.evaluator.build_contract("crea y ejecuta el archivo")
        self.assertTrue(contract.requires_code_verification)
        self.assertFalse(contract.requires_tests)
        self.assertTrue(contract.requires_execution)
        self.assertTrue(contract.tools_allowed)
        self.assertTrue(contract.files_allowed)

    def test_compatibility_properties_feature(self):
        """Propiedades de compatibilidad para tareas FEATURE."""
        contract = self.evaluator.build_contract("implementa sistema completo")
        self.assertTrue(contract.requires_code_verification)
        self.assertTrue(contract.requires_tests)
        self.assertTrue(contract.requires_execution)
        self.assertTrue(contract.tools_allowed)
        self.assertTrue(contract.files_allowed)

    def test_tool_permissions_unchanged(self):
        """Las permisos de herramientas deben permanecer consistentes."""
        chat_contract = self.evaluator.build_contract("hola, responde ok")
        action_contract = self.evaluator.build_contract("crea un archivo python")
        feature_contract = self.evaluator.build_contract("implementa un sistema completo de autenticacion")

        # CHAT: ninguna herramienta permitida
        self.assertFalse(chat_contract.tools_allowed)
        # ACTION: todas las herramientas principales permitidas
        self.assertTrue(action_contract.tools_allowed)
        # FEATURE: todas las herramientas incluyendo avanzadas permitidas
        self.assertTrue(feature_contract.tools_allowed)

    def test_risk_evaluation_unchanged(self):
        """La evaluación de riesgo no debe perder información."""
        # CHAT: nivel 1, sin verification, sin tests, sin ejecución
        chat_contract = self.evaluator.build_contract("hola")
        self.assertEqual(chat_contract.task_type, TaskType.CHAT)
        self.assertEqual(chat_contract.execution_level, ExecutionLevel.LEVEL_1_CHAT)
        self.assertFalse(chat_contract.requires_code_verification)

        # ACTION: nivel 2, verification requerida, ejecución requerida
        action_contract = self.evaluator.build_contract("crea un archivo python")
        self.assertEqual(action_contract.task_type, TaskType.ACTION)
        self.assertEqual(action_contract.execution_level, ExecutionLevel.LEVEL_2_ACTION)
        self.assertTrue(action_contract.requires_code_verification)
        self.assertFalse(action_contract.requires_tests)
        self.assertTrue(action_contract.requires_execution)

        # FEATURE: nivel 3, verification y tests requeridos, ejecución requerida
        feature_contract = self.evaluator.build_contract("implementa un sistema")
        self.assertEqual(feature_contract.task_type, TaskType.FEATURE)
        self.assertEqual(feature_contract.execution_level, ExecutionLevel.LEVEL_3_FEATURE)
        self.assertTrue(feature_contract.requires_code_verification)
        self.assertTrue(feature_contract.requires_tests)
        self.assertTrue(feature_contract.requires_execution)


if __name__ == "__main__":
    unittest.main()