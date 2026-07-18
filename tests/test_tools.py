import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../mis_agentes_inteligentes')))

from tools import listar_directorio_local, leer_archivo_local, escribir_archivo_local, ejecutar_comando_terminal

class TestTools(unittest.TestCase):
    def test_listar_directorio_local(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            with open(os.path.join(tmpdirname, 'dummy.txt'), 'w') as f:
                f.write('hello')
            
            resultado = listar_directorio_local(tmpdirname)
            self.assertIn('dummy.txt', resultado)
            self.assertIn(tmpdirname, resultado)

    def test_leer_archivo_local(self):
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as f:
            f.write("test content")
            file_path = f.name
        
        try:
            resultado = leer_archivo_local(file_path)
            self.assertEqual(resultado, "test content")
        finally:
            os.unlink(file_path)

    def test_escribir_archivo_local(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            file_path = os.path.join(tmpdirname, 'new_file.txt')
            resultado = escribir_archivo_local(file_path, "new content")
            
            self.assertIn("Éxito", resultado)
            self.assertTrue(os.path.exists(file_path))
            with open(file_path, 'r', encoding='utf-8') as f:
                self.assertEqual(f.read(), "new content")

    def test_ejecutar_comando_terminal_seguro(self):
        resultado = ejecutar_comando_terminal("echo 'hello world'")
        self.assertIn("Éxito", resultado)
        self.assertIn("hello world", resultado)

    def test_ejecutar_comando_terminal_blacklist(self):
        resultado = ejecutar_comando_terminal("rm -rf /")
        self.assertIn("Error de Seguridad", resultado)

if __name__ == '__main__':
    unittest.main()
