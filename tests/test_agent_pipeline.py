import unittest
from unittest.mock import MagicMock

from agent_pipeline import AgentPipeline


class TestAgentPipeline(unittest.TestCase):

    def test_pipeline_execution(self):
        pipeline = AgentPipeline()
        mock_runner = MagicMock(return_value="Respuesta de prueba del runner")

        response, metrics = pipeline.run_pipeline("Crear script de prueba", agent_runner=mock_runner)

        self.assertIn("Resultado de Ejecución Agéntica v3.0", response)
        self.assertIn("Respuesta de prueba del runner", response)
        self.assertIn("Reporte de Verificación de Calidad", response)

        self.assertIsInstance(metrics, dict)
        self.assertEqual(metrics["pipeline_stages"], 5)
        self.assertIn("verifier_passed", metrics)
        self.assertIn("ast_valid", metrics)
        self.assertIn("tests_passed", metrics)


if __name__ == '__main__':
    unittest.main()
