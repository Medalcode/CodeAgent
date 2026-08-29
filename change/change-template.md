# SDD Change Impact Analysis Declaration

## Change Title
[Short title describing the proposed change]

## Description
[Detailed description of what is changing and technical motivation]

## Modified Components
- [ ] `mis_agentes_inteligentes/main.py`
- [ ] `mis_agentes_inteligentes/agent_pipeline.py`
- [ ] `desktop_app.py`
- [ ] `mis_agentes_inteligentes/localcode_server.py`
- [ ] `sdd_contract/`
- [ ] Other: [specify]

## Potentially Affected Invariants
- [ ] **INV-001** (Pipeline Authority)
- [ ] **INV-002** (TaskContract Authority)
- [ ] **INV-003** (Cross-Task Isolation)
- [ ] **INV-004** (Intent Preservation)
- [ ] **INV-005** (Failure Containment)
- [ ] **INV-006** (Tool Isolation)
- [ ] **INV-007** (Conditional Verification)
- [ ] **INV-008** (Desktop Lifecycle Safety)

## Required Regression Tests
- [ ] `tests/test_sdd_conformance.py`
- [ ] `tests/test_cross_task_telemetry_isolation.py`
- [ ] `tests/test_pytest_verifier_resolution.py`
- [ ] `tests/test_server_lifecycle.py`
- [ ] `tests/test_task_router_negations.py`
- [ ] `tests/test_state_machine.py`
- [ ] Full Test Suite (`python -m unittest discover -s tests`)

## Required Runtime Evidence
- [ ] Fast-Path CHAT telemetry verification
- [ ] Cross-task isolation multi-request sequence
- [ ] Desktop concurrency / process lifecycle check

## Certification Impact
- [ ] **No Invariants Affected** (Documentation / minor comment)
- [ ] **Existing Certification Remains Valid** (Regression suite passes 100%)
- [ ] **Partial Re-Certification Required** (Specific invariant evidence updated)
- [ ] **Full Re-Certification Required** (Major architecture refactor)
