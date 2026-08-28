import unittest

from tools import (
    ejecutar_comando_terminal,
    is_command_approved,
    is_sensitive_command,
    pre_approve_command,
)


class TestTerminalHITLApproval(unittest.TestCase):
    def test_safe_command_classification(self):
        self.assertFalse(is_sensitive_command("pytest tests/"))
        self.assertFalse(is_sensitive_command("python --version"))

    def test_sensitive_command_classification(self):
        self.assertTrue(is_sensitive_command("pip install requests"))
        self.assertTrue(is_sensitive_command("npm install express"))
        self.assertTrue(is_sensitive_command("git push origin main"))

    def test_sensitive_command_requires_approval_flow(self):
        cmd = "pip install dummy_package_test_123"
        # Antes de pre-aprobar debe requerir autorización
        res = ejecutar_comando_terminal(cmd)
        self.assertIn("⚠️ AUTORIZACIÓN REQUERIDA (HITL):", res)

        # Pre-aprobar comando y verificar ejecución
        pre_approve_command(cmd)
        self.assertTrue(is_command_approved(cmd))


if __name__ == "__main__":
    unittest.main()
