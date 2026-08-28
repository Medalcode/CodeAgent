import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mis_agentes_inteligentes")))

from tools import (
    PermissionLevel,
    _atomic_write_file,
    check_tool_permission,
    editar_archivo_search_replace,
    escribir_archivo_local,
)


class TestTechnicalQualityRefactor(unittest.TestCase):
    def test_atomic_write_file_success(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_atomic.py")
            _atomic_write_file(filepath, "print('hello')\n")
            self.assertTrue(os.path.exists(filepath))
            with open(filepath, encoding="utf-8") as f:
                self.assertEqual(f.read(), "print('hello')\n")

    def test_atomic_write_file_cleanup_on_error(self):
        with tempfile.TemporaryDirectory() as tmpdir, patch("os.replace", side_effect=OSError("Simulated IO Error")), self.assertRaises(OSError):
            filepath = os.path.join(tmpdir, "test_atomic_error.py")
            _atomic_write_file(filepath, "content")

    def test_escribir_y_editar_archivo_refactored(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "sample.py")
            res_write = escribir_archivo_local(filepath, "x = 10\n")
            self.assertIn("Éxito", res_write)

            res_edit = editar_archivo_search_replace(filepath, "x = 10", "x = 20")
            self.assertIn("Éxito", res_edit)

            with open(filepath, encoding="utf-8") as f:
                self.assertEqual(f.read(), "x = 20\n")

    def test_permission_levels(self):
        self.assertTrue(check_tool_permission("leer_archivo", PermissionLevel.LOW))
        self.assertTrue(check_tool_permission("ejecutar_comando_terminal", PermissionLevel.CRITICAL))
        self.assertFalse(check_tool_permission("ejecutar_comando_terminal", PermissionLevel.LOW))


if __name__ == "__main__":
    unittest.main()
