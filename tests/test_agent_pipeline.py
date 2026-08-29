import unittest
from unittest.mock import MagicMock

from mis_agentes_inteligentes.agent_pipeline import AgentPipeline


class TestAgentPipeline(unittest.TestCase):

    def test_pipeline_execution(self):
        pipeline = AgentPipeline()
        mock_runner = MagicMock(return_value="Respuesta de prueba del runner")

        response, metrics = pipeline.run_pipeline("Crear script de prueba", agent_runner=mock_runner)

        self.assertIn("CodeAgent — Task Result", response)
        self.assertIn("Respuesta de prueba del runner", response)
        self.assertIn("Evidencia de Verificación Tri-Estado", response)

        self.assertIsInstance(metrics, dict)
        self.assertIn("execution_level", metrics)
        self.assertIn("verifier_passed", metrics)
        self.assertIn("kpis", metrics)


if __name__ == '__main__':
    unittest.main()
