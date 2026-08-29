import unittest
import os
import sys
import json
import time
import urllib.request
import subprocess
from unittest.mock import patch, MagicMock

# Configurar sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULE_DIR = os.path.join(PROJECT_ROOT, "mis_agentes_inteligentes")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

import desktop_app
from mis_agentes_inteligentes.version import CODEAGENT_VERSION
from mis_agentes_inteligentes.localcode_server import (
    SERVER_VERSION,
    SERVER_INSTANCE_ID,
    _is_parent_alive,
)
from mis_agentes_inteligentes.agent_pipeline import AgentPipeline, ComplexityRiskEvaluator, ExecutionLevel


class TestServerLifecycle(unittest.TestCase):
    def test_F_single_source_version(self):
        """Test F: Desktop y backend obtienen la versión exactamente desde la misma fuente (version.py)."""
        self.assertEqual(desktop_app.CODEAGENT_VERSION, CODEAGENT_VERSION)
        self.assertEqual(SERVER_VERSION, CODEAGENT_VERSION)
        self.assertEqual(desktop_app.CODEAGENT_VERSION, "5.0.0")

    def test_D_server_port_is_explicit(self):
        """Test D: El puerto seleccionado por Desktop se asigna de forma explícita al backend."""
        def _mock_verify(url=""):
            return {
                "service": "codeagent-backend",
                "version": CODEAGENT_VERSION,
                "base_dir": os.path.abspath(desktop_app.BASE_DIR),
                "parent_pid": os.getpid(),
                "parent_creation_time": desktop_app.get_process_creation_time(os.getpid()),
                "instance_id": desktop_app._EXPECTED_INSTANCE_ID,
            }

        with patch("subprocess.Popen") as mock_popen, \
             patch("desktop_app.verify_backend_identity", side_effect=_mock_verify):
            mock_popen.return_value = MagicMock()

            res = desktop_app.launch_server_bg(target_port=9876)
            self.assertTrue(res)
            self.assertEqual(desktop_app._CURRENT_BACKEND_PORT, 9876)

            # Verificar que se pasó --port 9876 a la línea de comandos
            args, kwargs = mock_popen.call_args
            cmd_list = args[0]
            self.assertIn("--port", cmd_list)
            self.assertIn("9876", cmd_list)
            self.assertEqual(kwargs["env"]["CODEAGENT_PORT"], "9876")

    def test_B_backend_ownership_requires_parent_identity(self):
        """Test B: Un backend con mismo workspace y versión pero distinto parent PID o creación no pertenece a Desktop."""
        different_parent_identity = {
            "service": "codeagent-backend",
            "version": CODEAGENT_VERSION,
            "base_dir": os.path.abspath(desktop_app.BASE_DIR),
            "parent_pid": os.getpid() + 99999,
            "parent_creation_time": 1000.0,
            "instance_id": "other-instance-id",
        }
        self.assertFalse(desktop_app.is_backend_compatible(different_parent_identity))

    def test_C_stop_server_is_idempotent(self):
        """Test C: Llamar a stop_server() múltiples veces es completamente seguro e idempotente."""
        mock_proc = MagicMock()
        desktop_app._SERVER_PROCESS = mock_proc
        desktop_app._IS_STOPPING = False

        desktop_app.stop_server()
        mock_proc.wait.assert_called()
        self.assertIsNone(desktop_app._SERVER_PROCESS)

        # Segunda llamada no debe arrojar error ni fallar
        desktop_app.stop_server()
        self.assertIsNone(desktop_app._SERVER_PROCESS)

    def test_E_parent_pid_reuse_is_detected(self):
        """Test E: Si el PID del proceso padre es reutilizado pero con diferente creation time, _is_parent_alive retorna False."""
        with patch("mis_agentes_inteligentes.localcode_server.PARENT_PID", os.getpid()), \
             patch("mis_agentes_inteligentes.localcode_server.PARENT_CREATION_TIME", 12345.678), \
             patch("mis_agentes_inteligentes.localcode_server._get_process_creation_time", return_value=99999.999):
            self.assertFalse(_is_parent_alive())

    def test_A_two_desktop_instances_do_not_share_backend(self):
        """Test A: Dos instancias Desktop tienen instance_ids y puertos dedicados independientes."""
        own_identity = {
            "service": "codeagent-backend",
            "version": CODEAGENT_VERSION,
            "base_dir": os.path.abspath(desktop_app.BASE_DIR),
            "parent_pid": os.getpid(),
            "parent_creation_time": desktop_app.get_process_creation_time(os.getpid()),
            "instance_id": "my-instance-id-123",
        }
        desktop_app._EXPECTED_INSTANCE_ID = "my-instance-id-123"
        self.assertTrue(desktop_app.is_backend_compatible(own_identity))

        # Otra instancia con instance_id diferente no es compatible
        other_identity = dict(own_identity, instance_id="other-instance-id-456")
        self.assertFalse(desktop_app.is_backend_compatible(other_identity))

    def test_G_chat_prompt_behavior_intact(self):
        """Test G: Garantiza que el contrato del prompt CHAT permanece intacto con métricas deterministas."""
        user_prompt = (
            "Responde únicamente con OK. No ejecutes ninguna herramienta. "
            "No abras terminal. No crees archivos. No modifiques el workspace. "
            "No ejecutes tests, Ruff ni análisis AST. No hagas planificación ni replanificación. "
            "Termina inmediatamente."
        )

        pipeline = AgentPipeline()
        respuesta, metricas = pipeline.run_pipeline(user_prompt, agent_runner=lambda p: "OK")

        contract = ComplexityRiskEvaluator.build_contract(user_prompt)
        self.assertEqual(contract.task_type.value, "CHAT")
        self.assertEqual(metricas.get("execution_level"), ExecutionLevel.LEVEL_1_CHAT.value)
        self.assertEqual(metricas.get("tool_calls_count"), 0)
        self.assertEqual(metricas.get("replans_count"), 0)

        verifier = metricas.get("verification_results", {})
        self.assertEqual(verifier.get("ast_status"), "NOT_REQUIRED")
        self.assertEqual(verifier.get("tests_status"), "NOT_REQUIRED")
        self.assertEqual(verifier.get("ruff_status"), "NOT_REQUIRED")


if __name__ == "__main__":
    unittest.main()
