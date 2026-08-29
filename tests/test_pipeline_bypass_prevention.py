"""
Test de prevención de bypass para AgentPipeline en main.py.
Verifica que si AgentPipeline.run_pipeline arroja una excepción,
el runner/agente.run NO sea invocado como fallback y la excepción falle de forma segura.
"""
import unittest
from unittest.mock import patch, MagicMock
from mis_agentes_inteligentes.main import ejecutar_agentes


class TestPipelineBypassPrevention(unittest.TestCase):

    @patch("mis_agentes_inteligentes.agent_pipeline.AgentPipeline.run_pipeline")
    @patch("mis_agentes_inteligentes.main.crear_agente")
    @patch("mis_agentes_inteligentes.main.get_model")
    def test_agent_pipeline_exception_does_not_call_runner_fallback(
        self, mock_get_model, mock_crear_agente, mock_run_pipeline
    ):
        """
        Garantiza que una excepción dentro de AgentPipeline.run_pipeline
        capture el error de forma segura y NO invoque agente.run() o _runner().
        """
        mock_agente = MagicMock()
        mock_crear_agente.return_value = mock_agente
        
        # Simular una excepción crítica dentro de AgentPipeline.run_pipeline
        mock_run_pipeline.side_effect = RuntimeError("Error simulado en AgentPipeline")

        prompt = "Responde únicamente con OK."

        resultado, metricas = ejecutar_agentes(
            user_prompt=prompt,
            provider="Ollama (Local)",
            model_name="qwen2.5-coder:14b",
            api_key="mock-key",
            agent_type="CodeAgent Developer",
            selected_tools=[]
        )

        # 1. Verificar que mock_agente.run NUNCA fue llamado como fallback
        mock_agente.run.assert_not_called()

        # 2. Verificar que la respuesta capturó el error de forma segura y transparente
        self.assertIn("Error crítico en el pipeline agéntico", resultado)
        self.assertIn("Error simulado en AgentPipeline", resultado)

        # 3. Verificar que las métricas reflejen fallo controlado y no bypass
        self.assertTrue(metricas.get("pipeline_failed"))
        self.assertFalse(metricas.get("verifier_passed"))
        self.assertEqual(metricas.get("error"), "Error simulado en AgentPipeline")


if __name__ == "__main__":
    unittest.main()
