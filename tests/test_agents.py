import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../mis_agentes_inteligentes')))

from agents import route_prompt

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
        self.assertEqual(result, "Agente de Edición de Código")

    def test_route_prompt_productivity(self):
        prompt = "Agrega un nuevo evento en mi agenda para mañana"
        result = route_prompt(prompt)
        self.assertEqual(result, "Asistente de Eventos y Productividad")

    def test_route_prompt_general(self):
        prompt = "Hola, ¿cómo estás hoy?"
        result = route_prompt(prompt)
        self.assertEqual(result, "Asistente General")

if __name__ == '__main__':
    unittest.main()
