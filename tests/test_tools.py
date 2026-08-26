import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../mis_agentes_inteligentes')))

from tools import (
    consultar_db,
    editar_archivo_search_replace,
    ejecutar_comando_terminal,
    escribir_archivo_local,
    guardar_reporte,
    leer_archivo_local,
    listar_directorio_local,
)


class TestTools(unittest.TestCase):
    def test_listar_directorio_local(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            with open(os.path.join(tmpdirname, 'dummy.txt'), 'w', encoding='utf-8') as f:
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
            if os.path.exists(file_path):
                os.unlink(file_path)

    def test_escribir_archivo_local(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            file_path = os.path.join(tmpdirname, 'new_file.txt')
            resultado = escribir_archivo_local(file_path, "new content")

            self.assertIn("Éxito", resultado)
            self.assertTrue(os.path.exists(file_path))
            with open(file_path, encoding='utf-8') as f:
                self.assertEqual(f.read(), "new content")

    def test_editar_archivo_search_replace_exito(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            file_path = os.path.join(tmpdirname, 'code.py')
            escribir_archivo_local(file_path, "def foo():\n    return 'old'\n")
            res = editar_archivo_search_replace(file_path, "return 'old'", "return 'new'")
            self.assertIn("Éxito", res)
            with open(file_path, encoding='utf-8') as f:
                self.assertIn("return 'new'", f.read())

    def test_editar_archivo_search_replace_no_encontrado(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            file_path = os.path.join(tmpdirname, 'code.py')
            escribir_archivo_local(file_path, "def foo():\n    pass\n")
            res = editar_archivo_search_replace(file_path, "nonexistent", "replacement")
            self.assertIn("Error: No se encontró el bloque exacto", res)

    def test_editar_archivo_search_replace_ambiguo(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            file_path = os.path.join(tmpdirname, 'code.py')
            escribir_archivo_local(file_path, "item = 1\nitem = 1\n")
            res = editar_archivo_search_replace(file_path, "item = 1", "item = 2")
            self.assertIn("Error: Se encontraron 2 coincidencias", res)

    def test_consultar_db_select_bloqueado(self):
        res = consultar_db("DELETE FROM eventos")
        self.assertIn("Error de Seguridad", res)

        res_drop = consultar_db("DROP TABLE eventos")
        self.assertIn("Error de Seguridad", res_drop)

    def test_guardar_reporte(self):
        res = guardar_reporte("Analisis de prueba unitaria")
        self.assertIn("Reporte guardado con éxito", res)

    def test_ejecutar_comando_terminal_seguro(self):
        resultado = ejecutar_comando_terminal("echo 'hello world'")
        self.assertIn("Éxito", resultado)
        self.assertIn("hello world", resultado)

    def test_ejecutar_comando_terminal_blacklist(self):
        resultado = ejecutar_comando_terminal("rm -rf /")
        self.assertIn("Error de Seguridad", resultado)

        resultado_win = ejecutar_comando_terminal("format c:")
        self.assertIn("Error de Seguridad", resultado_win)

    def test_escribir_archivo_local_directorio_anidado(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            file_path = os.path.join(tmpdirname, 'sub', 'dir', 'deep', 'nested.py')
            resultado = escribir_archivo_local(file_path, "print('nested')")
            self.assertIn("Éxito", resultado)
            self.assertTrue(os.path.exists(file_path))

    def test_verificar_sintaxis_post_edicion_warning(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            file_path = os.path.join(tmpdirname, 'broken.py')
            res = escribir_archivo_local(file_path, "def foo(\n")
            self.assertIn("ADVERTENCIA DE SINTAXIS POST-EDICIÓN", res)

    def test_ejecutar_comando_terminal_sandbox_strict(self):
        os.environ["STRICT_SANDBOX"] = "1"
        try:
            res = ejecutar_comando_terminal("powershell -Command Get-Process")
            self.assertIn("Error de Seguridad (Sandbox)", res)
        finally:
            os.environ.pop("STRICT_SANDBOX", None)

    def test_detectar_raiz_proyecto(self):
        from tools import _detectar_raiz_proyecto
        with tempfile.TemporaryDirectory() as tmpdirname:
            git_dir = os.path.join(tmpdirname, '.git')
            os.makedirs(git_dir, exist_ok=True)
            nested = os.path.join(tmpdirname, 'sub', 'folder')
            os.makedirs(nested, exist_ok=True)
            detected = _detectar_raiz_proyecto(nested)
            self.assertEqual(detected, os.path.abspath(tmpdirname))

    def test_obtener_contexto_workspace_graphify(self):
        from tools import obtener_contexto_workspace
        with tempfile.TemporaryDirectory() as tmpdirname:
            graph_dir = os.path.join(tmpdirname, 'graphify-out')
            os.makedirs(graph_dir, exist_ok=True)
            ctx = obtener_contexto_workspace(tmpdirname)
            self.assertIn("graphify query", ctx)


    def test_check_tool_permission(self):
        from tools import PermissionLevel, check_tool_permission
        self.assertTrue(check_tool_permission("leer_archivo", PermissionLevel.LOW))
        self.assertTrue(check_tool_permission("ejecutar_comando_terminal", PermissionLevel.CRITICAL))
        self.assertFalse(check_tool_permission("ejecutar_comando_terminal", PermissionLevel.LOW))


if __name__ == '__main__':
    unittest.main()
