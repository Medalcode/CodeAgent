import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../mis_agentes_inteligentes')))

from agents import get_available_agents, get_model, load_subagents_from_disk, route_prompt


class TestAgents(unittest.TestCase):
    def test_route_prompt_github(self):
        prompt = "Please check the PR on this repo github.com/user/project"
        result = route_prompt(prompt)
        self.assertEqual(result, "Analista de Código (Experto Github)")

        prompt2 = "Here is my ghp_token for the repository"
        result2 = route_prompt(prompt2)
        self.assertEqual(result2, "Analista de Código (Experto Github)")

    def test_route_prompt_editor(self):
        prompt = "Please refactor the code in tools.py to fix the bug"
        result = route_prompt(prompt)
        self.assertIn(result, ["CodeAgent Developer", "Agente de Edición de Código"])

    def test_route_prompt_productivity(self):
        prompt = "Agrega un nuevo evento en mi agenda para mañana"
        result = route_prompt(prompt)
        self.assertEqual(result, "Asistente de Eventos y Productividad")

    def test_route_prompt_general(self):
        prompt = "Hola, ¿cómo estás hoy?"
        result = route_prompt(prompt)
        self.assertEqual(result, "Asistente General")

    def test_get_available_agents(self):
        agents = get_available_agents()
        self.assertIn("Agente de Edición de Código", agents)
        self.assertIn("Analista de Código (Experto Github)", agents)
        self.assertIn("Asistente de Eventos y Productividad", agents)
        self.assertIn("Asistente General", agents)

    def test_load_subagents_from_disk(self):
        subagents = load_subagents_from_disk()
        self.assertIsInstance(subagents, dict)

    def test_get_model_invalid_provider(self):
        with self.assertRaises(ValueError):
            get_model("ProveedorInvalido", "model_name")

    def test_route_prompt_subagents(self):
        prompt = "Necesito un experto en python pro para refactorizar este módulo"
        result = route_prompt(prompt)
        self.assertEqual(result, "python-pro")


    def test_crear_agente_planning_interval(self):
        from agents import crear_agente
        mock_model = MagicMock()
        mock_model.model_id = "test-model"
        agente = crear_agente("Asistente General", mock_model, [], planning_interval=3)
        self.assertEqual(getattr(agente, "planning_interval", 0), 3)


if __name__ == '__main__':
    unittest.main()
