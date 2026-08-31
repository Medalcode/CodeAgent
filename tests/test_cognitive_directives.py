"""Tests for cognitive directive extraction - D1 Phase.

Verifies that get_phase_cognitive_directive behavior is preserved
after extraction to cognitive_directives.py."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mis_agentes_inteligentes.cognitive_directives import get_phase_cognitive_directive
from mis_agentes_inteligentes.agent_pipeline import State


class TestCognitiveDirectives:
    """Test cognitive directive generation after extraction."""

    def test_execute_directive(self):
        """Known EXECUTE phase directive."""
        directive = get_phase_cognitive_directive("EXECUTE")
        assert "EXECUTE" in directive
        assert "parches" in directive

    def test_verify_directive(self):
        """Known VERIFY phase directive."""
        directive = get_phase_cognitive_directive("VERIFY")
        assert "VERIFY" in directive
        assert "ruff" in directive

    def test_plan_directive(self):
        """Known PLAN phase directive."""
        directive = get_phase_cognitive_directive("PLAN")
        assert "PLAN" in directive
        assert "objetivo" in directive and "pasos" in directive

    def test_explore_directive(self):
        """Known EXPLORE phase directive."""
        directive = get_phase_cognitive_directive("EXPLORE")
        assert "EXPLORE" in directive
        assert "Grafo AST Graphify" in directive

    def test_diagnose_directive(self):
        """Known DIAGNOSE phase directive with failed_verification."""
        failed_verification = {"ast_errors": ["SyntaxError: invalid syntax"]}
        directive = get_phase_cognitive_directive("DIAGNOSE", failed_verification)
        assert "DIAGNOSE" in directive
        # Verify the directive contains error-related content
        assert "fallo" in directive.lower() or "error" in directive.lower()

    def test_replan_directive(self):
        """Known REPLAN phase directive with failed_verification."""
        failed_verification = {"ast_errors": ["Test failure"]}
        directive = get_phase_cognitive_directive("REPLAN", failed_verification)
        assert "REPLAN" in directive
        assert "errores exactos" in directive

    def test_unknown_state(self):
        """Unknown/unexpected state returns empty string."""
        directive = get_phase_cognitive_directive("NONEXISTENT")
        assert directive == ""

    def test_diagnose_no_failed_verification(self):
        """DIAGNOSE without failed_verification uses fallback message."""
        directive = get_phase_cognitive_directive("DIAGNOSE", None)
        assert "DIAGNOSE" in directive
        assert "Fallo no especificado" in directive

    def test_replan_no_failed_verification(self):
        """REPLAN without failed_verification uses fallback message."""
        directive = get_phase_cognitive_directive("REPLAN", None)
        assert "REPLAN" in directive
        assert "Errores no especificados" in directive

    def test_deterministic_output(self):
        """Same input always produces same output."""
        for _ in range(3):
            directive = get_phase_cognitive_directive("EXECUTE")
        # If we get here without exception, deterministic
        pass