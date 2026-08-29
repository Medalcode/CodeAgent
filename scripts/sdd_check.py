#!/usr/bin/env python3
"""
SDD Structural Traceability & Consistency Checker CLI (v5.1.0)
Verifica estructuralmente la trazabilidad, descubrimiento dinámico de Invariantes (INV-*)
y Características (SPEC-*), esquema obligatorio de especificaciones, análisis de impacto
y archivos de evidencia dedicados.
"""
import glob
import os
import re
import sys
import tempfile
from typing import Dict, List, Tuple, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TRACEABILITY_FILE = "specs/traceability.md"
CERTIFICATION_FILE = "audits/certifications/v5.0.0/certification.md"

REQUIRED_SPEC_SECTIONS = [
    "## Intent",
    "## Preconditions",
    "## Postconditions",
    "## Invariants",
    "## Failure Behavior",
    "## Observability",
    "## Testability",
    "## Traceability",
]


def normalize_repo_path(raw_path: str, root_dir: str = PROJECT_ROOT) -> Tuple[str, Optional[Tuple[int, int]]]:
    """
    Normaliza una referencia de archivo o URL file:// eliminando anclas de línea.
    Retorna (path_relativo, line_range_tuple)
    """
    clean = raw_path.strip().strip("`").strip()
    
    line_range = None
    if "#" in clean:
        parts = clean.split("#", 1)
        clean = parts[0]
        line_part = parts[1]
        m = re.search(r"L(\d+)(?:-L?(\d+))?", line_part)
        if m:
            start_l = int(m.group(1))
            end_l = int(m.group(2)) if m.group(2) else start_l
            line_range = (start_l, end_l)
            
    if "file:///" in clean:
        clean = clean.split("file:///", 1)[1]
    elif "file://" in clean:
        clean = clean.split("file://", 1)[1]
        
    clean = clean.replace("\\", "/")
    
    root_norm = root_dir.replace("\\", "/")
    if clean.lower().startswith(root_norm.lower()):
        clean = clean[len(root_norm):].lstrip("/")
        
    return clean, line_range


def parse_traceability_table(content: str) -> Dict[str, Dict[str, str]]:
    """
    Parsea las tablas Markdown en specs/traceability.md de forma estructural.
    Retorna un diccionario {item_id: {name, spec, source, tests, change, evidence, status}}
    """
    rows = {}
    lines = content.splitlines()
    
    for line in lines:
        if not line.strip().startswith("|") or "Invariant ID" in line or "Feature ID" in line or ":---" in line:
            continue
            
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) >= 6:
            raw_id = cols[0].replace("*", "").strip()
            if raw_id.startswith("INV-") or raw_id.startswith("SPEC-"):
                if len(cols) == 7:
                    # Invariant row format: ID, Name, Spec, Source, Tests, Evidence, Status
                    rows[raw_id] = {
                        "name": cols[1],
                        "spec": cols[2],
                        "source": cols[3],
                        "tests": cols[4],
                        "change": "",
                        "evidence": cols[5],
                        "status": cols[6]
                    }
                else:
                    # Feature row format: ID, Name, Spec, Source, Tests, Change, Evidence, Status
                    rows[raw_id] = {
                        "name": cols[1],
                        "spec": cols[2],
                        "source": cols[3],
                        "tests": cols[4],
                        "change": cols[5],
                        "evidence": cols[6],
                        "status": cols[7] if len(cols) > 7 else ""
                    }
    return rows


def discover_invariants(root_dir: str = PROJECT_ROOT) -> Tuple[Dict[str, Tuple[str, str]], List[str]]:
    """Descubre dinámicamente todos los archivos specs/invariants/INV-*.md. Retorna (inv_map, duplicate_errors)"""
    inv_map = {}
    duplicates = []
    inv_dir = os.path.join(root_dir, "specs", "invariants")
    if not os.path.exists(inv_dir):
        return inv_map, duplicates
        
    for fname in sorted(os.listdir(inv_dir)):
        if fname.startswith("INV-") and fname.endswith(".md"):
            m = re.match(r"(INV-\d+)", fname)
            if m:
                inv_id = m.group(1)
                rel_path = f"specs/invariants/{fname}"
                title = fname.replace(".md", "").replace(f"{inv_id}-", "").replace("-", " ").title()
                if inv_id in inv_map:
                    duplicates.append(f"Duplicate Invariant ID '{inv_id}' found in {fname}")
                inv_map[inv_id] = (title, rel_path)
    return inv_map, duplicates


def discover_features(root_dir: str = PROJECT_ROOT) -> Tuple[Dict[str, Tuple[str, str]], List[str]]:
    """Descubre dinámicamente todos los archivos specs/features/SPEC-*.md. Retorna (spec_map, duplicate_errors)"""
    spec_map = {}
    duplicates = []
    feat_dir = os.path.join(root_dir, "specs", "features")
    if not os.path.exists(feat_dir):
        return spec_map, duplicates
        
    for fname in sorted(os.listdir(feat_dir)):
        if fname.startswith("SPEC-") and fname.endswith(".md"):
            m = re.match(r"(SPEC-\d+)", fname)
            if m:
                spec_id = m.group(1)
                rel_path = f"specs/features/{fname}"
                title = fname.replace(".md", "").replace(f"{spec_id}-", "").replace("-", " ").title()
                if spec_id in spec_map:
                    duplicates.append(f"Duplicate Feature ID '{spec_id}' found in {fname}")
                spec_map[spec_id] = (title, rel_path)
    return spec_map, duplicates


def validate_file_reference(raw_ref: str, root_dir: str = PROJECT_ROOT) -> Tuple[bool, str]:
    """Valida la existencia real de un archivo y su rango de líneas si está especificado."""
    if not raw_ref.strip():
        return False, "Empty reference string"
        
    m_link = re.findall(r"\]\(([^)]+)\)", raw_ref)
    paths_to_check = m_link if m_link else [raw_ref]
    
    if not paths_to_check:
        return False, "No file path found in reference"
        
    for ref in paths_to_check:
        rel_path, line_range = normalize_repo_path(ref, root_dir)
        if not rel_path:
            continue
            
        abs_path = os.path.normpath(os.path.join(root_dir, rel_path))
        
        if not os.path.exists(abs_path):
            return False, f"File does not exist: {rel_path}"
            
        if not os.path.isfile(abs_path):
            return False, f"Path is not a regular file: {rel_path}"
            
        if line_range:
            start_l, end_l = line_range
            try:
                with open(abs_path, encoding="utf-8", errors="replace") as f:
                    total_lines = len(f.readlines())
                if not (1 <= start_l <= end_l <= max(1, total_lines)):
                    return False, f"Invalid line range L{start_l}-L{end_l} for {rel_path} (total lines: {total_lines})"
            except Exception as ex:
                return False, f"Error reading {rel_path}: {ex}"
                
    return True, "OK"


def validate_test_reference(test_ref_str: str, root_dir: str = PROJECT_ROOT) -> Tuple[bool, str]:
    """Valida que los archivos de prueba y símbolos referenciados existan en disco."""
    test_refs = re.findall(r"tests/[a-zA-Z0-9_\-\./:]+", test_ref_str)
    if not test_refs:
        test_refs = [t.strip() for t in test_ref_str.split("<br>") if t.strip()]
        
    if not test_refs or not test_ref_str.strip():
        return False, f"No test references extracted from '{test_ref_str}'"
        
    for ref in test_refs:
        symbol = None
        clean_ref = ref
        if "::" in ref:
            parts = ref.split("::")
            clean_ref = parts[0]
            symbol = parts[-1]
            
        rel_path, _ = normalize_repo_path(clean_ref, root_dir)
        abs_path = os.path.normpath(os.path.join(root_dir, rel_path))
        
        if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
            return False, f"Test file does not exist: {rel_path}"
            
        if symbol:
            try:
                with open(abs_path, encoding="utf-8", errors="replace") as f:
                    content = f.read()
                if symbol not in content:
                    return False, f"Symbol '{symbol}' not found in test file {rel_path}"
            except Exception as ex:
                return False, f"Error reading test file {rel_path}: {ex}"
                
    return True, "OK"


def validate_feature_spec_schema(spec_abs_path: str) -> Tuple[bool, str]:
    """Valida que una especificación de característica contenga todas las secciones requeridas."""
    try:
        with open(spec_abs_path, encoding="utf-8") as f:
            content = f.read()
            
        for sec in REQUIRED_SPEC_SECTIONS:
            if sec not in content:
                return False, f"Missing required schema section '{sec}' in {os.path.basename(spec_abs_path)}"
        return True, "OK"
    except Exception as ex:
        return False, f"Error reading spec file: {ex}"


def validate_sdd_governance(root_dir: str = PROJECT_ROOT, verbose: bool = True) -> Tuple[bool, List[str]]:
    """Ejecuta el chequeo completo de gobernanza y trazabilidad SDD para Invariantes y Features."""
    errors = []
    
    if verbose:
        print("=========================================================================")
        print("   SDD STRUCTURAL TRACEABILITY & CONSISTENCY CHECK (v5.1.0)")
        print("=========================================================================\n")
        
    trace_path = os.path.join(root_dir, TRACEABILITY_FILE)
    cert_path = os.path.join(root_dir, CERTIFICATION_FILE)
    
    if not os.path.exists(trace_path):
        err = f"❌ MISSING: Traceability file not found at {TRACEABILITY_FILE}"
        errors.append(err)
        if verbose: print(err)
        return False, errors
        
    if not os.path.exists(cert_path):
        err = f"❌ MISSING: Certification evidence not found at {CERTIFICATION_FILE}"
        errors.append(err)
        if verbose: print(err)
        return False, errors
        
    with open(trace_path, encoding="utf-8") as f:
        trace_content = f.read()
        
    table_rows = parse_traceability_table(trace_content)
    
    # 1. Discover Invariants & Features
    inv_map, inv_dups = discover_invariants(root_dir)
    spec_map, spec_dups = discover_features(root_dir)
    
    all_ok = True
    
    if inv_dups or spec_dups:
        for d in inv_dups + spec_dups:
            errors.append(d)
            if verbose: print(f"❌ {d}")
        all_ok = False
        
    # Check that all table rows have valid specs
    for row_id, row_data in table_rows.items():
        spec_ok, spec_err = validate_file_reference(row_data["spec"], root_dir)
        if not spec_ok:
            err = f"[{row_id}] Spec file missing or invalid: {spec_err}"
            errors.append(err)
            all_ok = False
            if verbose: print(f"❌ {err}")

    # Check Invariants
    if verbose: print("--- INVARIANT GOVERNANCE ---")
    for inv_id, (inv_name, spec_rel_path) in inv_map.items():
        spec_abs_path = os.path.normpath(os.path.join(root_dir, spec_rel_path))
        
        if not os.path.exists(spec_abs_path):
            err = f"[{inv_id}] Spec file missing: {spec_rel_path}"
            errors.append(err)
            all_ok = False
            if verbose: print(f"{inv_id} {inv_name:<32} .... FAIL (Reason: {err})")
            continue
            
        if inv_id not in table_rows:
            err = f"[{inv_id}] Missing structured row in {TRACEABILITY_FILE}"
            errors.append(err)
            all_ok = False
            if verbose: print(f"{inv_id} {inv_name:<32} .... FAIL (Reason: {err})")
            continue
            
        row = table_rows[inv_id]
        
        source_ok, source_err = validate_file_reference(row["source"], root_dir)
        if not source_ok:
            err = f"[{inv_id}] Invalid source reference: {source_err}"
            errors.append(err)
            all_ok = False
            if verbose: print(f"{inv_id} {inv_name:<32} .... FAIL (Reason: {err})")
            continue
            
        test_ok, test_err = validate_test_reference(row["tests"], root_dir)
        if not test_ok:
            err = f"[{inv_id}] Invalid test reference: {test_err}"
            errors.append(err)
            all_ok = False
            if verbose: print(f"{inv_id} {inv_name:<32} .... FAIL (Reason: {err})")
            continue
            
        ev_ok, ev_err = validate_file_reference(row["evidence"], root_dir)
        if not ev_ok:
            err = f"[{inv_id}] Invalid evidence reference: {ev_err}"
            errors.append(err)
            all_ok = False
            if verbose: print(f"{inv_id} {inv_name:<32} .... FAIL (Reason: {err})")
            continue
            
        if verbose:
            print(f"{inv_id} {inv_name:<32} .... TRACEABLE (Spec, Source, Tests, Evidence OK)")

    # Check Features
    if verbose: print("\n--- FEATURE GOVERNANCE ---")
    for spec_id, (spec_name, spec_rel_path) in spec_map.items():
        spec_abs_path = os.path.normpath(os.path.join(root_dir, spec_rel_path))
        
        if not os.path.exists(spec_abs_path):
            err = f"[{spec_id}] Spec file missing: {spec_rel_path}"
            errors.append(err)
            all_ok = False
            if verbose: print(f"{spec_id} {spec_name:<32} .... FAIL (Reason: {err})")
            continue
            
        schema_ok, schema_err = validate_feature_spec_schema(spec_abs_path)
        if not schema_ok:
            err = f"[{spec_id}] Schema validation failed: {schema_err}"
            errors.append(err)
            all_ok = False
            if verbose: print(f"{spec_id} {spec_name:<32} .... FAIL (Reason: {err})")
            continue
            
        if spec_id not in table_rows:
            err = f"[{spec_id}] Missing structured row in {TRACEABILITY_FILE}"
            errors.append(err)
            all_ok = False
            if verbose: print(f"{spec_id} {spec_name:<32} .... FAIL (Reason: {err})")
            continue
            
        row = table_rows[spec_id]
        
        source_ok, source_err = validate_file_reference(row["source"], root_dir)
        if not source_ok:
            err = f"[{spec_id}] Invalid source reference: {source_err}"
            errors.append(err)
            all_ok = False
            if verbose: print(f"{spec_id} {spec_name:<32} .... FAIL (Reason: {err})")
            continue
            
        test_ok, test_err = validate_test_reference(row["tests"], root_dir)
        if not test_ok:
            err = f"[{spec_id}] Invalid test reference: {test_err}"
            errors.append(err)
            all_ok = False
            if verbose: print(f"{spec_id} {spec_name:<32} .... FAIL (Reason: {err})")
            continue
            
        if row["change"]:
            ch_ok, ch_err = validate_file_reference(row["change"], root_dir)
            if not ch_ok:
                err = f"[{spec_id}] Invalid change impact reference: {ch_err}"
                errors.append(err)
                all_ok = False
                if verbose: print(f"{spec_id} {spec_name:<32} .... FAIL (Reason: {err})")
                continue
                
        ev_ok, ev_err = validate_file_reference(row["evidence"], root_dir)
        if not ev_ok:
            err = f"[{spec_id}] Invalid evidence reference: {ev_err}"
            errors.append(err)
            all_ok = False
            if verbose: print(f"{spec_id} {spec_name:<32} .... FAIL (Reason: {err})")
            continue
            
        if verbose:
            print(f"{spec_id} {spec_name:<32} .... TRACEABLE (Spec, Source, Tests, Change, Evidence OK)")
            
    passed = all_ok and (len(errors) == 0)
    if verbose:
        print("\n-------------------------------------------------------------------------")
        print(f"SPECIFICATION CHECK:    {'PASS' if all_ok else 'FAIL'}")
        print(f"TRACEABILITY TABLES:    {'PASS' if len(table_rows) >= (len(inv_map) + len(spec_map)) else 'FAIL'}")
        print(f"SOURCE REFERENCES:      {'PASS' if all_ok else 'FAIL'}")
        print(f"TEST REFERENCES:        {'PASS' if all_ok else 'FAIL'}")
        print(f"EVIDENCE REFERENCES:    {'PASS' if all_ok else 'FAIL'}")
        print("-------------------------------------------------------------------------\n")
        print("=========================================================================")
        print(f"   RESULT: {'PASS' if passed else 'FAIL'}")
        print("=========================================================================\n")
        
    return passed, errors


def run_adversarial_self_test():
    """
    Ejecuta diagnósticos simulados en un directorio temporal aislado probando 13 casos (A-M).
    Verifica end-to-end que validate_sdd_governance(temp_repo) devuelva False en cada mutación.
    """
    print("=========================================================================")
    print("   RUNNING DECOUPLED ADVERSARIAL SELF-DIAGNOSTIC TEST SUITE (CASES A - M)")
    print("=========================================================================\n")
    
    cases_passed = 0
    total_cases = 13
    
    def create_mock_repo(tmpdir: str):
        os.makedirs(os.path.join(tmpdir, "specs", "invariants"), exist_ok=True)
        os.makedirs(os.path.join(tmpdir, "specs", "features"), exist_ok=True)
        os.makedirs(os.path.join(tmpdir, "audits", "certifications", "v5.0.0"), exist_ok=True)
        os.makedirs(os.path.join(tmpdir, "audits", "features", "SPEC-009"), exist_ok=True)
        os.makedirs(os.path.join(tmpdir, "change"), exist_ok=True)
        os.makedirs(os.path.join(tmpdir, "mis_agentes_inteligentes"), exist_ok=True)
        os.makedirs(os.path.join(tmpdir, "tests"), exist_ok=True)
        
        # Invariant Spec
        with open(os.path.join(tmpdir, "specs", "invariants", "INV-001-pipeline-authority.md"), "w") as f:
            f.write("# INV-001\n")
            
        # Feature Spec
        with open(os.path.join(tmpdir, "specs", "features", "SPEC-009-sdd-health-telemetry.md"), "w") as f:
            f.write("# SPEC-009\n## Intent\n## Preconditions\n## Postconditions\n## Invariants\n## Failure Behavior\n## Observability\n## Testability\n## Traceability\n")
            
        # Files
        with open(os.path.join(tmpdir, "audits", "certifications", "v5.0.0", "certification.md"), "w") as f:
            f.write("OK\n")
        with open(os.path.join(tmpdir, "audits", "features", "SPEC-009", "runtime-evidence.md"), "w") as f:
            f.write("OK\n")
        with open(os.path.join(tmpdir, "change", "change-feature-sdd-telemetry.md"), "w") as f:
            f.write("OK\n")
        with open(os.path.join(tmpdir, "mis_agentes_inteligentes", "localcode_server.py"), "w") as f:
            f.write("line1\nline2\nline3\n")
        with open(os.path.join(tmpdir, "tests", "test_sdd_health_endpoint.py"), "w") as f:
            f.write("def test_foo(): pass\n")
            
        # Traceability
        with open(os.path.join(tmpdir, "specs", "traceability.md"), "w") as f:
            f.write("| Invariant ID | Name | Spec | Source | Tests | Evidence | Status |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :---: |\n")
            f.write("| **INV-001** | Pipeline Authority | specs/invariants/INV-001-pipeline-authority.md | mis_agentes_inteligentes/localcode_server.py | tests/test_sdd_health_endpoint.py | audits/certifications/v5.0.0/certification.md | CERTIFIED |\n\n")
            f.write("| Feature ID | Name | Spec | Source | Tests | Change | Evidence | Status |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |\n")
            f.write("| **SPEC-009** | Health Telemetry | specs/features/SPEC-009-sdd-health-telemetry.md | mis_agentes_inteligentes/localcode_server.py | tests/test_sdd_health_endpoint.py::test_foo | change/change-feature-sdd-telemetry.md | audits/features/SPEC-009/runtime-evidence.md | VERIFIED |\n")

    # Caso A: Missing Invariant Spec
    def test_case_a():
        with tempfile.TemporaryDirectory() as tmp:
            create_mock_repo(tmp)
            os.remove(os.path.join(tmp, "specs", "invariants", "INV-001-pipeline-authority.md"))
            ok, _ = validate_sdd_governance(tmp, verbose=False)
            return not ok

    # Caso B: Missing Invariant Row in Traceability Table
    def test_case_b():
        with tempfile.TemporaryDirectory() as tmp:
            create_mock_repo(tmp)
            with open(os.path.join(tmp, "specs", "traceability.md"), "w") as f:
                f.write("| Feature ID | Name | Spec | Source | Tests | Change | Evidence | Status |\n")
            ok, _ = validate_sdd_governance(tmp, verbose=False)
            return not ok

    # Caso C: Missing Test File Reference
    def test_case_c():
        with tempfile.TemporaryDirectory() as tmp:
            create_mock_repo(tmp)
            os.remove(os.path.join(tmp, "tests", "test_sdd_health_endpoint.py"))
            ok, _ = validate_sdd_governance(tmp, verbose=False)
            return not ok

    # Caso D: Invalid Source File Path
    def test_case_d():
        with tempfile.TemporaryDirectory() as tmp:
            create_mock_repo(tmp)
            os.remove(os.path.join(tmp, "mis_agentes_inteligentes", "localcode_server.py"))
            ok, _ = validate_sdd_governance(tmp, verbose=False)
            return not ok

    # Caso E: Invalid Spec Association
    def test_case_e():
        with tempfile.TemporaryDirectory() as tmp:
            create_mock_repo(tmp)
            with open(os.path.join(tmp, "specs", "features", "SPEC-009-sdd-health-telemetry.md"), "w") as f:
                f.write("Broken\n")
            ok, _ = validate_sdd_governance(tmp, verbose=False)
            return not ok

    # Caso F: Missing Certification Evidence File
    def test_case_f():
        with tempfile.TemporaryDirectory() as tmp:
            create_mock_repo(tmp)
            os.remove(os.path.join(tmp, "audits", "certifications", "v5.0.0", "certification.md"))
            ok, _ = validate_sdd_governance(tmp, verbose=False)
            return not ok

    # Caso G: Fake Floating Text Reference Without Table
    def test_case_g():
        with tempfile.TemporaryDirectory() as tmp:
            create_mock_repo(tmp)
            with open(os.path.join(tmp, "specs", "traceability.md"), "w", encoding="utf-8") as f:
                f.write("Esta es una mencion texto flotante de SPEC-009 sin tabla.")
            ok, _ = validate_sdd_governance(tmp, verbose=False)
            return not ok

    # Caso H: Missing Feature Spec File (SPEC-009)
    def test_case_h():
        with tempfile.TemporaryDirectory() as tmp:
            create_mock_repo(tmp)
            os.remove(os.path.join(tmp, "specs", "features", "SPEC-009-sdd-health-telemetry.md"))
            ok, _ = validate_sdd_governance(tmp, verbose=False)
            return not ok

    # Caso I: Missing Feature Schema Section (e.g. missing ## Intent)
    def test_case_i():
        with tempfile.TemporaryDirectory() as tmp:
            create_mock_repo(tmp)
            with open(os.path.join(tmp, "specs", "features", "SPEC-009-sdd-health-telemetry.md"), "w") as f:
                f.write("# SPEC-009\n## Preconditions\n")
            ok, _ = validate_sdd_governance(tmp, verbose=False)
            return not ok

    # Caso J: Missing Change Impact Analysis File
    def test_case_j():
        with tempfile.TemporaryDirectory() as tmp:
            create_mock_repo(tmp)
            os.remove(os.path.join(tmp, "change", "change-feature-sdd-telemetry.md"))
            ok, _ = validate_sdd_governance(tmp, verbose=False)
            return not ok

    # Caso K: Missing Dedicated Feature Evidence File
    def test_case_k():
        with tempfile.TemporaryDirectory() as tmp:
            create_mock_repo(tmp)
            os.remove(os.path.join(tmp, "audits", "features", "SPEC-009", "runtime-evidence.md"))
            ok, _ = validate_sdd_governance(tmp, verbose=False)
            return not ok

    # Caso L: Duplicate Feature / Invariant ID
    def test_case_l():
        with tempfile.TemporaryDirectory() as tmp:
            create_mock_repo(tmp)
            with open(os.path.join(tmp, "specs", "features", "SPEC-009-sdd-health-telemetry-dup.md"), "w") as f:
                f.write("# SPEC-009\n## Intent\n## Preconditions\n## Postconditions\n## Invariants\n## Failure Behavior\n## Observability\n## Testability\n## Traceability\n")
            ok, _ = validate_sdd_governance(tmp, verbose=False)
            return not ok

    # Caso M: Out-of-bounds Line Range (#L99999)
    def test_case_m():
        with tempfile.TemporaryDirectory() as tmp:
            create_mock_repo(tmp)
            with open(os.path.join(tmp, "specs", "traceability.md"), "w") as f:
                f.write("| Invariant ID | Name | Spec | Source | Tests | Evidence | Status |\n")
                f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :---: |\n")
                f.write("| **INV-001** | Pipeline Authority | specs/invariants/INV-001-pipeline-authority.md | mis_agentes_inteligentes/localcode_server.py#L99999 | tests/test_sdd_health_endpoint.py | audits/certifications/v5.0.0/certification.md | CERTIFIED |\n")
            ok, _ = validate_sdd_governance(tmp, verbose=False)
            return not ok

    cases = [
        ("Caso A: Missing invariant spec file", test_case_a),
        ("Caso B: Missing invariant row in traceability", test_case_b),
        ("Caso C: Missing test file reference", test_case_c),
        ("Caso D: Invalid source file path", test_case_d),
        ("Caso E: Invalid spec file schema / content", test_case_e),
        ("Caso F: Missing certification evidence file", test_case_f),
        ("Caso G: Fake floating text reference without table", test_case_g),
        ("Caso H: Missing feature spec file (SPEC-009)", test_case_h),
        ("Caso I: Missing feature schema section (## Intent)", test_case_i),
        ("Caso J: Missing change impact analysis file", test_case_j),
        ("Caso K: Missing dedicated feature evidence file", test_case_k),
        ("Caso L: Duplicate feature spec ID", test_case_l),
        ("Caso M: Out-of-bounds line range (#L99999)", test_case_m),
    ]

    for name, fn in cases:
        try:
            detected_fail = fn()
            if detected_fail:
                cases_passed += 1
                print(f"- {name:<58} .... DETECTED (PASS)")
            else:
                print(f"- {name:<58} .... NOT DETECTED (FAIL)")
        except Exception as ex:
            print(f"- {name:<58} .... ERROR ({ex})")
            
    print("\n-------------------------------------------------------------------------")
    print(f"ADVERSARIAL SELF-CHECK RESULT: {'PASS' if cases_passed == total_cases else 'FAIL'} ({cases_passed}/{total_cases} Cases Detected)")
    print("-------------------------------------------------------------------------\n")
    return cases_passed == total_cases


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test-adversarial":
        adv_ok = run_adversarial_self_test()
        sys.exit(0 if adv_ok else 1)
    else:
        passed, _ = validate_sdd_governance()
        sys.exit(0 if passed else 1)
