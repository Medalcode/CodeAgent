import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../mis_agentes_inteligentes')))

from main import ejecutar_agentes


class TestIntegrationPipeline(unittest.TestCase):
    @patch('main.get_model')
    @patch('main.crear_agente')
    def test_ejecutar_agentes_modo_conversacion(self, mock_crear_agente, mock_get_model):
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.return_value = "Respuesta de prueba mock"
        mock_crear_agente.return_value = mock_agent_instance
        mock_get_model.return_value = MagicMock()

        resultado, metricas = ejecutar_agentes(
            user_prompt="Hola, asistente",
            provider="Ollama (Local)",
            model_name="qwen2.5-coder:14b",
            api_key="",
            agent_type="Asistente General",
            selected_tools=[],
        )

        self.assertIn("Respuesta de prueba mock", resultado)
        self.assertIsInstance(metricas, dict)
        self.assertIn("tiempo_segundos", metricas)
        self.assertEqual(metricas["modelo"], "qwen2.5-coder:14b")

    @patch('main.get_model')
    @patch('main.crear_agente')
    def test_ejecutar_agentes_auto_router(self, mock_crear_agente, mock_get_model):
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.return_value = "Resultado de edición mock"
        mock_crear_agente.return_value = mock_agent_instance
        mock_get_model.return_value = MagicMock()

        resultado, metricas = ejecutar_agentes(
            user_prompt="Por favor refactoriza la función en tools.py para arreglar el bug",
            provider="Ollama (Local)",
            model_name="qwen2.5-coder:14b",
            api_key="",
            agent_type="Auto (Enrutador Automático) 🌟",
            selected_tools=[],
        )

        self.assertIn("Resultado de edición mock", resultado)
        self.assertTrue(
            "CodeAgent Developer" in metricas["agentes_usados"] or "Agente de Edición" in metricas["agentes_usados"]
        )


if __name__ == '__main__':
    unittest.main()
