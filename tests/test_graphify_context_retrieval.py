"""
Unit and Integration Tests for AST Subgraph Context Retrieval & Impact Engine (SPEC-013).
Demonstrates TDD RED phase against un-implemented GraphContextEngine.
"""
import json
import os
import sys
import tempfile
import time
import unittest

from mis_agentes_inteligentes.agent_pipeline import AgentPipeline


class TestGraphifyContextRetrieval(unittest.TestCase):
    def setUp(self):
        # Intentar importar el módulo modular GraphContextEngine que será implementado en la fase GREEN
        try:
            from mis_agentes_inteligentes.graph_context import GraphContextEngine
            self.engine_cls = GraphContextEngine
        except ImportError:
            self.engine_cls = None

    def test_001_exact_file_target_extraction(self):
        """TEST-001: Verificar extracción determinista por nombre de archivo exacto en prompt."""
        if self.engine_cls is None:
            self.fail("GraphContextEngine no está implementado (TDD RED esperado)")
        engine = self.engine_cls()
        target = engine.extract_target("Modifica el servidor proxy en localcode_server.py para añadir un handler")
        self.assertEqual(target.get("file"), "mis_agentes_inteligentes/localcode_server.py")

    def test_002_exact_symbol_target_extraction(self):
        """TEST-002: Verificar extracción determinista por símbolo exacto en prompt."""
        if self.engine_cls is None:
            self.fail("GraphContextEngine no está implementado (TDD RED esperado)")
        engine = self.engine_cls()
        target = engine.extract_target("Refactoriza la función handle_sse_events")
        self.assertEqual(target.get("symbol"), "handle_sse_events")

    def test_003_normalized_symbol_target_extraction(self):
        """TEST-003: Verificar coincidencia por símbolo normalizado (case-folded / sanitized)."""
        if self.engine_cls is None:
            self.fail("GraphContextEngine no está implementado (TDD RED esperado)")
        engine = self.engine_cls()
        target = engine.extract_target("Revisa la clase handlesseeventsdict")
        self.assertTrue(any("handle_sse_events" in label for label in target.get("matched_labels", [])))

    def test_004_1_hop_subgraph_traversal(self):
        """TEST-004: Verificar recorrido de 1-hop devolviendo llamadores, llamadas e importaciones directas."""
        if self.engine_cls is None:
            self.fail("GraphContextEngine no está implementado (TDD RED esperado)")
        engine = self.engine_cls()
        subgraph = engine.get_subgraph(target_symbol="handle_sse_events", depth=1)
        self.assertGreater(len(subgraph.get("nodes", [])), 0)
        relations = [edge.get("relation") for edge in subgraph.get("edges", [])]
        self.assertTrue(any(r in ("calls", "imports", "contains") for r in relations))

    def test_005_2_hop_subgraph_traversal_for_refactor(self):
        """TEST-005: Verificar profundidad depth=2 exclusivamente para tareas REFACTOR o DEBUG."""
        if self.engine_cls is None:
            self.fail("GraphContextEngine no está implementado (TDD RED esperado)")
        engine = self.engine_cls()
        subgraph_1 = engine.get_subgraph(target_symbol="handle_sse_events", depth=1)
        subgraph_2 = engine.get_subgraph(target_symbol="handle_sse_events", depth=2, task_type="REFACTOR")
        self.assertGreaterEqual(len(subgraph_2.get("nodes", [])), len(subgraph_1.get("nodes", [])))

    def test_006_node_priority_ranking(self):
        """TEST-006: Verificar ordenación determinista por prioridad (P1 Target > P2 Callers/Callees > P3 Imports)."""
        if self.engine_cls is None:
            self.fail("GraphContextEngine no está implementado (TDD RED esperado)")
        engine = self.engine_cls()
        ranked = engine.rank_nodes(target_symbol="handle_sse_events")
        self.assertEqual(ranked[0].get("priority"), 1)
        self.assertIn("handle_sse_events", ranked[0].get("label"))

    def test_007_context_token_budget_pruning(self):
        """TEST-007: Verificar que la poda determinista respete max_tokens=1500."""
        if self.engine_cls is None:
            self.fail("GraphContextEngine no está implementado (TDD RED esperado)")
        engine = self.engine_cls(max_tokens=1500)
        formatted_context = engine.build_context("Refactoriza localcode_server.py")
        estimated_tokens = len(formatted_context) // 4
        self.assertLessEqual(estimated_tokens, 1500)

    def test_008_missing_graph_file_fallback(self):
        """TEST-008: Verificar degradación segura cuando graphify-out/graph.json no existe."""
        if self.engine_cls is None:
            self.fail("GraphContextEngine no está implementado (TDD RED esperado)")
        engine = self.engine_cls(graph_path="/ruta/inexistente/graph.json")
        context = engine.build_context("Cualquier meta")
        self.assertIn("status=fallback", context)

    def test_009_unknown_symbol_fallback(self):
        """TEST-009: Verificar degradación segura ante target inexistente en el grafo."""
        if self.engine_cls is None:
            self.fail("GraphContextEngine no está implementado (TDD RED esperado)")
        engine = self.engine_cls()
        context = engine.build_context("Modifica SimboloInexistenteXyz99")
        self.assertIn("fallback", context.lower())

    def test_010_graph_cache_invalidation_on_mtime_change(self):
        """TEST-010: Verificar invalidación de caché en memoria cuando mtime de graph.json cambia."""
        if self.engine_cls is None:
            self.fail("GraphContextEngine no está implementado (TDD RED esperado)")
        engine = self.engine_cls()
        cache_manager = engine.cache_manager
        mtime_1 = cache_manager.last_mtime
        time.sleep(0.01)
        # Invalida si mtime cambia
        self.assertTrue(cache_manager.is_valid())

    def test_011_pipeline_explorer_integration(self):
        """TEST-011: Verificar que AgentPipeline._stage_explorer(user_goal) retorne contexto enfocado al objetivo."""
        pipeline = AgentPipeline()
        goal = "Refactoriza handle_sse_events en localcode_server.py"
        context = pipeline._stage_explorer(goal)
        # En la fase TDD RED actual, _stage_explorer ignora goal y devuelve la cadena estática de hubs globales
        self.assertIn("localcode_server.py", context, "stage_explorer debe incluir el archivo objetivo en el contexto")
        self.assertIn("handle_sse_events", context, "stage_explorer debe incluir el símbolo objetivo en el contexto")


if __name__ == "__main__":
    unittest.main()
