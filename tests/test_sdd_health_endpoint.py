"""
Unit & Integration Tests for SDD Governance Telemetry Endpoint (GET /api/health/sdd)
Demonstrates TDD under the SDD Framework.
"""
import unittest
import json
from unittest.mock import patch, MagicMock
from mis_agentes_inteligentes.localcode_server import (
    get_sdd_health_dict, SERVER_VERSION, PARENT_PID, _is_parent_alive, LocalCodeProxyHandler
)


class TestSDDHealthEndpoint(unittest.TestCase):
    def test_sdd_health_dict_structure(self):
        """UNIT: Verifica que get_sdd_health_dict() retorne las métricas exactas del esquema de gobernanza SDD."""
        data = get_sdd_health_dict()
        
        self.assertEqual(data.get("status"), "OK")
        self.assertEqual(data.get("sdd_version"), SERVER_VERSION)
        self.assertEqual(data.get("certified_commit"), "b0157240d41d3a81c0b3c68b94d2e3a46c90f874")
        self.assertEqual(data.get("invariants_certified_count"), 8)
        self.assertEqual(data.get("parent_pid"), PARENT_PID)
        self.assertIsInstance(data.get("parent_alive"), bool)
        self.assertTrue(data.get("pipeline_authority_active"))

    def test_sdd_health_graceful_degradation(self):
        """UNIT: Verifica que si _is_parent_alive lanza una excepción, el dict degrade a status DEGRADED."""
        with patch("mis_agentes_inteligentes.localcode_server._is_parent_alive", side_effect=Exception("Simulated Error")):
            data = get_sdd_health_dict()
            self.assertEqual(data.get("status"), "DEGRADED")
            self.assertFalse(data.get("parent_alive"))

    def test_handler_sdd_health_routing(self):
        """INTEGRATION: Verifica que LocalCodeProxyHandler responde correctamente al invocar handle_sdd_health."""
        handler = MagicMock(spec=LocalCodeProxyHandler)
        handler._send_json = MagicMock()
        
        LocalCodeProxyHandler.handle_sdd_health(handler)
        
        handler._send_json.assert_called_once()
        sent_dict = handler._send_json.call_args[0][0]
        self.assertEqual(sent_dict.get("sdd_version"), SERVER_VERSION)
        self.assertEqual(sent_dict.get("invariants_certified_count"), 8)

    def test_handler_sdd_health_observability_log_trace(self):
        """INTEGRATION (R4): Verifica que handle_sdd_health emite la traza de log observada por SPEC-009."""
        handler = MagicMock(spec=LocalCodeProxyHandler)
        handler._send_json = MagicMock()
        
        with patch("mis_agentes_inteligentes.localcode_server._safe_print") as mock_print:
            LocalCodeProxyHandler.handle_sdd_health(handler)
            mock_print.assert_called_with("[LocalCode Server] GET /api/health/sdd")


if __name__ == "__main__":
    unittest.main()
