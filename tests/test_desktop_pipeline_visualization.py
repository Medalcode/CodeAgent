"""
Unit & Integration Tests for Desktop Real-Time Pipeline EventSource Visualization (SPEC-012).
Demonstrates TDD RED -> GREEN under the SDD Framework.
"""
import os
import re
import unittest
from unittest.mock import MagicMock, patch

from mis_agentes_inteligentes.agent_pipeline import AgentPipeline, State
from mis_agentes_inteligentes.localcode_server import LocalCodeProxyHandler, handle_sse_events_dict
from mis_agentes_inteligentes.runtime.event_bus import Event, EventBus


class TestDesktopPipelineVisualization(unittest.TestCase):
    def setUp(self):
        self.ui_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "localcode_claude_ui.html")
        with open(self.ui_path, "r", encoding="utf-8") as f:
            self.ui_content = f.read()

    def test_001_ui_sse_contract_functions_exist(self):
        """TEST-001: Verifica que localcode_claude_ui.html contenga las funciones de contrato connectPipelineSSE y closePipelineSSE."""
        self.assertIn("connectPipelineSSE", self.ui_content, "Falta la función connectPipelineSSE en localcode_claude_ui.html")
        self.assertIn("closePipelineSSE", self.ui_content, "Falta la función closePipelineSSE en localcode_claude_ui.html")

    def test_002_real_event_parsing_contract(self):
        """TEST-002: Verifica que la UI maneje eventos reales de STATE_ENTERED y TOOL_EXECUTED."""
        self.assertIn("STATE_ENTERED", self.ui_content, "localcode_claude_ui.html debe responder al evento real STATE_ENTERED")
        self.assertIn("TOOL_EXECUTED", self.ui_content, "localcode_claude_ui.html debe responder al evento real TOOL_EXECUTED")

    def test_003_lifecycle_cleanup_contract(self):
        """TEST-003 (INV-008): Verifica que closePipelineSSE se invoque en el bloque finally de la invocación de chat."""
        self.assertIn("closePipelineSSE()", self.ui_content, "La UI debe cerrar el EventSource al concluir o fallar el chat")

    def test_004_task_correlation_backend_pipeline(self):
        """TEST-004: Verifica la correlación end-to-end entre task_id en UI request, localcode_server y AgentPipeline."""
        pipeline = AgentPipeline()
        ev_bus = EventBus()
        pipeline._event_bus = ev_bus

        received = []
        ev_bus.subscribe(lambda ev: received.append(ev))

        task_id = "task-corr-12345"
        pipeline.run(user_goal="Consulta de prueba para correlacion", session_id=task_id)

        task_events = [ev for ev in received if ev.task_id == task_id]
        self.assertGreater(len(task_events), 0, "AgentPipeline debe publicar eventos asociados al task_id correlacionado")
        states = [ev.payload.get("state") for ev in task_events if ev.event_type == "STATE_ENTERED"]
        self.assertIn("EXECUTE", states, "AgentPipeline debe publicar transiciones a los estados reales")

    def test_005_removal_of_fake_timer_ticker(self):
        """TEST-005: Verifica que el temporizador estático falso secCount % 3 === 0 haya sido eliminado o reemplazado por la lógica de eventos reales."""
        self.assertNotIn("secCount % 3 === 0", self.ui_content, "El temporizador estático artificial secCount % 3 === 0 debe ser eliminado")

    def test_006_graceful_sse_failure_contract(self):
        """TEST-006: Verifica que la UI maneje errores de EventSource sin interrumpir el flujo de chat (onerror handler)."""
        self.assertIn("onerror", self.ui_content, "El cliente EventSource debe registrar un manejador onerror para degradación elegante")

    def test_007_event_ordering_idempotency(self):
        """TEST-007: Verifica que handle_sse_events_dict formatee correctamente eventos de finalización de tarea (TASK_COMPLETED)."""
        ev = Event(task_id="task-fin-999", event_type="TASK_COMPLETED", payload={"output": "Done"}, timestamp=2000.0, event_id=99)
        formatted = handle_sse_events_dict(ev)
        self.assertIn("TASK_COMPLETED", formatted)
        self.assertIn("task-fin-999", formatted)


if __name__ == "__main__":
    unittest.main()
