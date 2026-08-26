import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../mis_agentes_inteligentes')))

from rag_tools import CHROMA_AVAILABLE, indexar_directorio_local, preguntar_a_repositorio


class TestRagTools(unittest.TestCase):
    def test_indexar_directorio_invalido(self):
        if CHROMA_AVAILABLE:
            resultado = indexar_directorio_local("path_inexistente_12345")
            self.assertIn("Error", resultado)
            self.assertIn("no es un directorio válido", resultado)
        else:
            resultado = indexar_directorio_local(".")
            self.assertIn("Error: Las librerías RAG no están instaladas", resultado)

    def test_preguntar_a_repositorio_fallback(self):
        if not CHROMA_AVAILABLE:
            resultado = preguntar_a_repositorio("¿Qué hace la función main?")
            self.assertIn("Error: Las librerías RAG no están instaladas", resultado)

    def test_preguntar_a_repositorio_cache(self):
        import rag_tools
        rag_tools._RAG_CACHE["test_key"] = "cached result"
        res = preguntar_a_repositorio("Test_Key")
        self.assertEqual(res, "cached result")


if __name__ == '__main__':
    unittest.main()
