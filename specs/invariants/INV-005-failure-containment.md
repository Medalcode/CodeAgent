# INV-005 — Failure Containment

## Status
CERTIFIED

## Statement
Un fallo o excepción interna dentro de `AgentPipeline` no puede provocar bypass ni fallback hacia la ejecución directa o descontrolada del agente fuera del gobierno del contrato y de la telemetría.

## Scope
- `mis_agentes_inteligentes/main.py` (`ejecutar_agentes`)
- `mis_agentes_inteligentes/agent_pipeline.py`

## Preconditions
- Ocurre una excepción o fallo no esperado durante la ejecución de `pipeline.run_pipeline()`.

## Required Behavior
- `main.ejecutar_agentes()` captura la excepción en su bloque `try...except`, formatea la respuesta de error para el usuario y establece `metricas["verifier_passed"] = False` y `metricas["error"] = str(e)`.
- El agente no continúa ejecutando iteraciones adicionales fuera del control del pipeline.

## Forbidden Behavior
- Reintentar silenciosamente la ejecución mediante `agente.run()` descartando el contrato `TaskContract` o las métricas de fallo.

## Evidence
- Static: Manejo de excepciones en `mis_agentes_inteligentes/main.py#L162-L170`.
- Tests: `tests/test_diagnose_root_cause.py`.
- Runtime: Evaluación adversarial inyectando `RuntimeError("Fallo Provocado")` en `run_pipeline()`.
- OS/Filesystem: N/A

## Related Tests
- `tests/test_diagnose_root_cause.py::TestDiagnoseRootCause::test_diagnose_captures_ast_errors`

## Related Modules
- `mis_agentes_inteligentes/main.py`
- `mis_agentes_inteligentes/agent_pipeline.py`

## Audit
- Audit Candidate: v5.0.0 Release Candidate Audit
- Audit Date: 2026-08-29
- Verdict: PASS

## Certification
- Certified Release: v5.0.0
- Commit SHA: `b0157240d41d3a81c0b3c68b94d2e3a46c90f874`
