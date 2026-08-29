# INV-007 — Conditional Verification

## Status
CERTIFIED

## Statement
Cuando `contract.requires_code_verification == False` (en peticiones conversacionales `CHAT`), no deben ejecutarse análisis AST, linter Ruff, suites de prueba (`pytest`, `unittest`) ni diffs de Git.

## Scope
- `mis_agentes_inteligentes/agent_pipeline.py` (`_stage_verifier`)

## Preconditions
- El prompt del usuario es clasificado con `task_type == "CHAT"`.

## Required Behavior
- `_stage_verifier` retorna de inmediato con `ast_status = "NOT_REQUIRED"`, `tests_status = "NOT_REQUIRED"`, `ruff_status = "NOT_REQUIRED"`.
- Se omiten todas las llamadas a subprocesos OS (`subprocess.run`).

## Forbidden Behavior
- Lanzar procesos `pytest`, `ruff` o `git diff` para peticiones que no modifican código ni requieren verificación.

## Evidence
- Static: Check temprano `if contract.task_type.value == "CHAT": return {"ast_status": "NOT_REQUIRED", ...}` en `agent_pipeline.py#L645`.
- Tests: `tests/test_sdd_conformance.py`.
- Runtime: Monitoreo de subprocesos OS durante ejecuciones CHAT en runtime real.
- OS/Filesystem: Cero comandos invocados en la terminal del sistema operativo.

## Related Tests
- `tests/test_sdd_conformance.py::TestSDDConformance::test_chat_contract_fast_path`

## Related Modules
- `mis_agentes_inteligentes/agent_pipeline.py`

## Audit
- Audit Candidate: v5.0.0 Release Candidate Audit
- Audit Date: 2026-08-29
- Verdict: PASS

## Certification
- Certified Release: v5.0.0
- Commit SHA: `b0157240d41d3a81c0b3c68b94d2e3a46c90f874`
