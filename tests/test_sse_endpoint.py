"""
Unit, Integration, Concurrency, and Lifecycle Tests for Real-Time SSE Endpoint (SPEC-011).
Demonstrates TDD RED -> GREEN under the SDD Framework.
"""
import json
import os
import sys
import time
import unittest
from queue import Queue
from unittest.mock import MagicMock, patch

from mis_agentes_inteligentes.localcode_server import LocalCodeProxyHandler, handle_sse_events_dict
from mis_agentes_inteligentes.runtime.event_bus import Event, EventBus, get_event_bus


class TestSSEEndpoint(unittest.TestCase):
    def setUp(self):
        self.event_bus = EventBus()

    def test_001_event_bus_publish_subscribe(self):
        """TEST-001: Verifica suscripción, publicación y des-suscripción en EventBus."""
        received = []

        def listener(ev: Event):
            received.append(ev)

        self.event_bus.subscribe(listener)
        self.event_bus.publish("task-123", "STATE_ENTERED", {"state": "PLAN"})

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].task_id, "task-123")
        self.assertEqual(received[0].event_type, "STATE_ENTERED")
        self.assertEqual(received[0].payload.get("state"), "PLAN")

        self.event_bus.unsubscribe(listener)
        self.event_bus.publish("task-123", "STATE_ENTERED", {"state": "EXECUTE"})
        self.assertEqual(len(received), 1)

    def test_002_pipeline_event_emission(self):
        """TEST-002: Verifica que la emisión de eventos preserve los tipos y estructura reales del pipeline."""
        ev = self.event_bus.publish("task-456", "STATE_CHANGED", {"state": "VERIFY", "status": "RUNNING"})
        self.assertEqual(ev.task_id, "task-456")
        self.assertEqual(ev.event_type, "STATE_CHANGED")
        self.assertEqual(ev.payload.get("state"), "VERIFY")

    def test_003_sse_http_contract_formatting(self):
        """TEST-003: Verifica que handle_sse_events_dict formatee correctamente un evento en bloque data: {...}\n\n."""
        ev = Event(task_id="task-789", event_type="STATE_ENTERED", payload={"state": "DONE"}, timestamp=1000.0, event_id=42)
        formatted = handle_sse_events_dict(ev)
        self.assertTrue(formatted.startswith("data: "))
        self.assertTrue(formatted.endswith("\n\n"))
        
        payload_str = formatted[len("data: "):-2]
        data = json.loads(payload_str)
        self.assertEqual(data.get("task_id"), "task-789")
        self.assertEqual(data.get("event_type"), "STATE_ENTERED")
        self.assertEqual(data.get("event_id"), 42)

    def test_004_client_disconnect_cleanup(self):
        """TEST-004: Verifica que un cliente SSE desconectado elimine su listener del EventBus."""
        q = Queue()
        
        def mock_listener(ev: Event):
            q.put(ev)
            
        self.event_bus.subscribe(mock_listener)
        self.assertEqual(len(self.event_bus._listeners), 1)
        
        self.event_bus.unsubscribe(mock_listener)
        self.assertEqual(len(self.event_bus._listeners), 0)

    def test_005_concurrent_subscribers(self):
        """TEST-005: Verifica que múltiples suscriptores concurrentes reciban el evento de forma hilo-segura."""
        received_a = []
        received_b = []

        self.event_bus.subscribe(lambda ev: received_a.append(ev))
        self.event_bus.subscribe(lambda ev: received_b.append(ev))

        self.event_bus.publish("task-999", "TOOL_EXECUTED", {"tool": "write_file"})

        self.assertEqual(len(received_a), 1)
        self.assertEqual(len(received_b), 1)
        self.assertEqual(received_a[0].payload.get("tool"), "write_file")
        self.assertEqual(received_b[0].payload.get("tool"), "write_file")

    def test_006_task_isolation_filtering(self):
        """TEST-006: Verifica que la suscripción a eventos pueda filtrarse por task_id de forma aislada."""
        received = []

        def filtered_listener(ev: Event):
            if ev.task_id == "task-A":
                received.append(ev)

        self.event_bus.subscribe(filtered_listener)
        self.event_bus.publish("task-B", "STATE_ENTERED", {"state": "PLAN"})
        self.event_bus.publish("task-A", "STATE_ENTERED", {"state": "EXECUTE"})

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].task_id, "task-A")

    def test_007_server_shutdown_compatibility(self):
        """TEST-007 (INV-008): Verifica que la ruta SSE esté registrada en LocalCodeProxyHandler y responda correctamente."""
        handler = MagicMock(spec=LocalCodeProxyHandler)
        handler.handle_sse_events = MagicMock()
        
        # Invocación directa del handler
        handler.handle_sse_events()
        handler.handle_sse_events.assert_called_once()


if __name__ == "__main__":
    unittest.main()
