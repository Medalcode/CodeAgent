import json
import os
import sys
import unittest
import urllib.request
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../mis_agentes_inteligentes')))

import session_manager
from localcode_server import LocalCodeProxyHandler, ThreadedTCPServer


class TestE2ESystemSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadedTCPServer(("127.0.0.1", 0), LocalCodeProxyHandler)
        cls.port = cls.server.server_address[1]
        import threading
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_e2e_session_creation_and_chat_flow(self):
        # 1. Crear nueva sesión en el gestor
        session_id = session_manager.create_new_session("E2E Test Session")
        self.assertIsNotNone(session_id)

        # 2. Simular petición HTTP a /api/agent/chat con mock del agente
        payload = json.dumps({
            "prompt": "Escribir un script de prueba E2E",
            "provider": "OpenAI",
            "model": "gpt-4o-mini",
            "api_key": "sk-dummy-key-e2e",
            "agent_type": "CodeAgent Developer",
            "tools": ["Archivos Locales"]
        }).encode("utf-8")

        url = f"http://127.0.0.1:{self.port}/api/agent/chat"
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})

        with patch("main.crear_agente") as mock_crear:
            mock_agent_inst = MagicMock()
            mock_agent_inst.run.return_value = "Respuesta E2E Simulada Exitosa"
            mock_crear.return_value = mock_agent_inst

            with urllib.request.urlopen(req) as resp:
                self.assertEqual(resp.status, 200)
                data = json.loads(resp.read().decode("utf-8"))
                self.assertIn("respuesta", data)
                self.assertIn("Respuesta E2E Simulada Exitosa", data["respuesta"])
                self.assertIn("metricas", data)

        # 3. Limpiar sesión creada
        session_manager.delete_session(session_id)


if __name__ == "__main__":
    unittest.main()
