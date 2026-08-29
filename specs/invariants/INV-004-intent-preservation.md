# INV-004 — Intent Preservation

## Status
CERTIFIED

## Statement
Las restricciones negativas en el prompt ("no ejecutes pytest", "sin usar ruff", "no ejecutes AST") deben limitar únicamente la acción o herramienta prohibida específica, sin degradar indebidamente la tarea completa a `CHAT` ni cancelar la intención positiva principal.

## Scope
- `sdd_contract/task_router.py`
- `mis_agentes_inteligentes/agent_pipeline.py` (`_stage_verifier`)

## Preconditions
- El usuario proporciona un prompt mixto con acciones positivas (ej. "Crea action_final.py y ejecuta python action_final.py") y restricciones negativas sobre herramientas secundarias (ej. "No ejecutes pytest").

## Required Behavior
- `TaskRouter` identifica que existen palabras clave de acción/mutación activas sin ser anuladas por negaciones sobre la mutación misma.
- `TaskType` se clasifica como `ACTION` o `FEATURE` (no `CHAT`).
- `_stage_verifier` omite exclusivamente el paso prohibido (ej. no ejecuta `pytest` si `has_neg` detecta la negación de tests).

## Forbidden Behavior
- Interpretar que "no ejecutes pytest" invalida globalmente las palabras clave de mutación ("crea", "ejecuta"), clasificando erróneamente la tarea como `CHAT`.

## Evidence
- Static: Expresiones regulares con límites de palabra `\b(no\s+(añadas|crees|crear|ejecutes|corras)|sin)\s+(tests?|pruebas?|unittest|pytest)\b` en `agent_pipeline.py` y `task_router.py`.
- Tests: `tests/test_task_router_negations.py`.
- Runtime: Clasificación adversarial probada con 4 prompts mixtos reales.
- OS/Filesystem: N/A

## Related Tests
- `tests/test_task_router_negations.py::TestTaskRouterNegations::test_action_keywords_with_negative_verifications`

## Related Modules
- `sdd_contract/task_router.py`
- `mis_agentes_inteligentes/agent_pipeline.py`

## Audit
- Audit Candidate: v5.0.0 Release Candidate Audit
- Audit Date: 2026-08-29
- Verdict: PASS

## Certification
- Certified Release: v5.0.0
- Commit SHA: `b0157240d41d3a81c0b3c68b94d2e3a46c90f874`
