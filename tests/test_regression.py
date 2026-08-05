import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../mis_agentes_inteligentes')))

import app
import session_manager
from tools import editar_archivo_search_replace, git_diff, git_status


class TestRegressionSuite(unittest.TestCase):
    def test_truncar_markdown_corto(self):
        texto = "Texto corto"
        res = app._truncar_markdown(texto, max_chars=50)
        self.assertEqual(res, texto)

    def test_truncar_markdown_largo_con_codigo_abierto(self):
        texto = "```python\ndef test():\n    print('Hello World')\n    return 42"
        res = app._truncar_markdown(texto, max_chars=30)
        self.assertIn("```", res)
        self.assertIn("[resumido]", res)

    def test_session_manager_invalid_inputs(self):
        # Operaciones con None/strings vacíos no deben lanzar excepciones descontroladas
        self.assertIsNone(session_manager.load_session(None))
        self.assertIsNone(session_manager.load_session(""))
        self.assertEqual(session_manager.export_session_to_markdown(None), "")
        session_manager.save_session(None, {})
        session_manager.delete_session("")

    def test_editar_archivo_search_replace_exact_match(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "sample.py")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("def alpha():\n    return 10\n")

            res = editar_archivo_search_replace(filepath, "return 10", "return 20")
            self.assertIn("Éxito", res)
            self.assertIn("diff", res)

            with open(filepath, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("return 20", content)

    def test_git_tools_en_directorio_temporal(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            status = git_status(tmpdir)
            self.assertIsNotNone(status)
            diff = git_diff(tmpdir)
            self.assertIsNotNone(diff)


if __name__ == '__main__':
    unittest.main()
