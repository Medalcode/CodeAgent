import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../mis_agentes_inteligentes')))

import tools as mis_herramientas
from main import _construir_contexto_workspace, get_herramientas


class TestMainPipeline(unittest.TestCase):
    def test_get_herramientas_mapping(self):
        seleccionadas = ["Archivos Locales", "Git", "Terminal Integrada"]
        herramientas = get_herramientas(seleccionadas)

        self.assertTrue(len(herramientas) > 0)
        # Debe incluir siempre la herramienta de memoria base guardar_reporte
        self.assertIn(mis_herramientas.guardar_reporte, herramientas)

    def test_get_herramientas_vacia(self):
        herramientas = get_herramientas([])
        self.assertEqual(len(herramientas), 1)
        self.assertEqual(herramientas[0], mis_herramientas.guardar_reporte)

    def test_construir_contexto_workspace(self):
        contexto = _construir_contexto_workspace()
        self.assertIn("CONTEXTO", contexto)
        self.assertIn("WORKSPACE", contexto)


if __name__ == '__main__':
    unittest.main()
