"""
Tests de resolución del verificador de pruebas con sys.executable -m pytest.
Garantiza que la verificación no dependa del binario global pytest en el PATH del SO.
"""
import os
import sys
import shutil
import tempfile
import unittest
from mis_agentes_inteligentes.agent_pipeline import AgentPipeline


class TestPytestVerifierResolution(unittest.TestCase):

    def setUp(self):
        self.old_skip = os.environ.pop("SKIP_SUBPROCESS_TESTS", None)
        self.temp_dir = tempfile.mkdtemp(prefix="test_verifier_res_")
        self.pipeline = AgentPipeline(workspace_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        if self.old_skip is not None:
            os.environ["SKIP_SUBPROCESS_TESTS"] = self.old_skip
        else:
            os.environ.pop("SKIP_SUBPROCESS_TESTS", None)

    def test_stage_verifier_with_sys_executable_pytest(self):
        """
        Verifica que _stage_verifier use sys.executable -m pytest para descubrir y
        ejecutar pruebas unitarias válidas sin fallos falsos por PATH.
        """
        # Crear módulo de código Python
        mod_path = os.path.join(self.temp_dir, "mi_modulo.py")
        with open(mod_path, "w", encoding="utf-8") as f:
            f.write("def duplicar(x: int) -> int:\n    return x * 2\n")

        # Crear archivo de prueba en la raíz del workspace
        test_path = os.path.join(self.temp_dir, "test_mi_modulo.py")
        with open(test_path, "w", encoding="utf-8") as f:
            f.write("from mi_modulo import duplicar\ndef test_duplicar(): assert duplicar(4) == 8\n")

        prompt = "Refactoriza la función en mi_modulo.py. Haz que los tests pasen. Escribe pruebas unitarias en test_mi_modulo.py y ejecuta pytest."

        res = self.pipeline._stage_verifier(user_goal=prompt)

        self.assertTrue(res.get("ast_valid"), "AST debe ser válido")
        self.assertEqual(res.get("ast_status"), "PASS")
        self.assertTrue(res.get("tests_passed"), "Las pruebas deben pasar usando el ejecutable actual de Python")
        self.assertEqual(res.get("tests_status"), "PASS")
        self.assertTrue(res.get("success"), "Verificación global debe pasar")


if __name__ == "__main__":
    unittest.main()
