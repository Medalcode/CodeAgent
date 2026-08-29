"""
Unit & Integration Tests for SDD Checker Engine (SPEC-010)
Validates dynamic invariant/feature discovery, schema validation, and error detection.
"""
import os
import tempfile
import unittest
from scripts.sdd_check import (
    validate_sdd_governance,
    discover_invariants,
    discover_features,
    validate_feature_spec_schema,
    parse_traceability_table
)


class TestSDDCheckerEngine(unittest.TestCase):
    def setUp(self):
        self.tmpdir_obj = tempfile.TemporaryDirectory()
        self.tmpdir = self.tmpdir_obj.name
        
        # Structure
        os.makedirs(os.path.join(self.tmpdir, "specs", "invariants"), exist_ok=True)
        os.makedirs(os.path.join(self.tmpdir, "specs", "features"), exist_ok=True)
        os.makedirs(os.path.join(self.tmpdir, "audits", "certifications", "v5.0.0"), exist_ok=True)
        os.makedirs(os.path.join(self.tmpdir, "audits", "features", "SPEC-009"), exist_ok=True)
        os.makedirs(os.path.join(self.tmpdir, "change"), exist_ok=True)
        os.makedirs(os.path.join(self.tmpdir, "mis_agentes_inteligentes"), exist_ok=True)
        os.makedirs(os.path.join(self.tmpdir, "tests"), exist_ok=True)
        
        # Files
        with open(os.path.join(self.tmpdir, "specs", "invariants", "INV-001-pipeline-authority.md"), "w") as f:
            f.write("# INV-001\n")
            
        with open(os.path.join(self.tmpdir, "specs", "features", "SPEC-009-sdd-health-telemetry.md"), "w") as f:
            f.write("# SPEC-009\n## Intent\n## Preconditions\n## Postconditions\n## Invariants\n## Failure Behavior\n## Observability\n## Testability\n## Traceability\n")
            
        with open(os.path.join(self.tmpdir, "audits", "certifications", "v5.0.0", "certification.md"), "w") as f:
            f.write("OK\n")
        with open(os.path.join(self.tmpdir, "audits", "features", "SPEC-009", "runtime-evidence.md"), "w") as f:
            f.write("OK\n")
        with open(os.path.join(self.tmpdir, "change", "change-feature-sdd-telemetry.md"), "w") as f:
            f.write("OK\n")
        with open(os.path.join(self.tmpdir, "mis_agentes_inteligentes", "localcode_server.py"), "w") as f:
            f.write("print('hello')\n")
        with open(os.path.join(self.tmpdir, "tests", "test_sdd_health_endpoint.py"), "w") as f:
            f.write("def test_foo(): pass\n")
            
        # Traceability
        with open(os.path.join(self.tmpdir, "specs", "traceability.md"), "w") as f:
            f.write("| Invariant ID | Name | Spec | Source | Tests | Evidence | Status |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :---: |\n")
            f.write("| **INV-001** | Pipeline Authority | specs/invariants/INV-001-pipeline-authority.md | mis_agentes_inteligentes/localcode_server.py | tests/test_sdd_health_endpoint.py | audits/certifications/v5.0.0/certification.md | CERTIFIED |\n\n")
            f.write("| Feature ID | Name | Spec | Source | Tests | Change | Evidence | Status |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |\n")
            f.write("| **SPEC-009** | Health Telemetry | specs/features/SPEC-009-sdd-health-telemetry.md | mis_agentes_inteligentes/localcode_server.py | tests/test_sdd_health_endpoint.py::test_foo | change/change-feature-sdd-telemetry.md | audits/features/SPEC-009/runtime-evidence.md | VERIFIED |\n")

    def tearDown(self):
        self.tmpdir_obj.cleanup()

    def test_dynamic_discovery_invariants_and_features(self):
        """UNIT: Verifica que discover_invariants() y discover_features() detecten dinámicamente archivos specs/."""
        invs, _ = discover_invariants(self.tmpdir)
        specs, _ = discover_features(self.tmpdir)
        
        self.assertIn("INV-001", invs)
        self.assertIn("SPEC-009", specs)

    def test_valid_governance_mock_repo_passes(self):
        """INTEGRATION: Verifica que un repositorio válido pase la validación completa."""
        ok, errors = validate_sdd_governance(self.tmpdir, verbose=False)
        self.assertTrue(ok, f"Expected PASS but got errors: {errors}")
        self.assertEqual(len(errors), 0)

    def test_feature_spec_schema_validation(self):
        """UNIT: Verifica que validate_feature_spec_schema rechace archivos sin secciones requeridas."""
        spec_file = os.path.join(self.tmpdir, "specs", "features", "SPEC-009-sdd-health-telemetry.md")
        ok, _ = validate_feature_spec_schema(spec_file)
        self.assertTrue(ok)
        
        # Corromper esquema
        with open(spec_file, "w") as f:
            f.write("# SPEC-009\n## Intent\n")
        ok, err = validate_feature_spec_schema(spec_file)
        self.assertFalse(ok)
        self.assertIn("Missing required schema section", err)


if __name__ == "__main__":
    unittest.main()
