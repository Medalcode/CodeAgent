# INV-002 — TaskContract Authority

## Status
CERTIFIED

## Statement
Los atributos de gobierno derivados del contrato de tarea (`TaskContract`) son inmutables durante el ciclo de ejecución de una petición. Ningún componente posterior puede relajar o alterar `task_type`, `tools_allowed`, `requires_code_verification`, `requires_tests`, `requires_execution` o `max_replans`.

## Scope
- `sdd_contract/task_contract.py`
- `sdd_contract/task_router.py`
- `mis_agentes_inteligentes/agent_pipeline.py` (`ComplexityRiskEvaluator`)

## Preconditions
- El prompt del usuario es clasificado por `ComplexityRiskEvaluator.build_contract(prompt)`.

## Required Behavior
- Si `task_type == "CHAT"`, `tools_allowed = False`, `requires_code_verification = False`, `requires_tests = False`.
- El nivel de ejecución derivado (`LEVEL_1_CHAT` para CHAT) rige estrictamente el flujo sin que la etapa de ejecución re-habilite herramientas prohibidas.

## Forbidden Behavior
- Modificar dinámicamente `contract.tools_allowed` de `False` a `True` durante la ejecución.
- Permitir que un contrato `CHAT` ejecute replanificaciones o verificaciones de código.

## Evidence
- Static: `ComplexityRiskEvaluator.build_contract` y `TaskContract` dataclass.
- Tests: `tests/test_sdd_conformance.py`.
- Runtime: Verificación empírica de inmutabilidad de contrato durante evaluación de prompts CHAT.
- OS/Filesystem: N/A

## Related Tests
- `tests/test_sdd_conformance.py::TestSDDConformance::test_chat_contract_fast_path`
- `tests/test_server_lifecycle.py::TestServerLifecycle::test_G_chat_prompt_behavior_intact`

## Related Modules
- `sdd_contract/task_contract.py`
- `sdd_contract/task_router.py`
- `mis_agentes_inteligentes/agent_pipeline.py`

## Audit
- Audit Candidate: v5.0.0 Release Candidate Audit
- Audit Date: 2026-08-29
- Verdict: PASS

## Certification
- Certified Release: v5.0.0
- Commit SHA: `b0157240d41d3a81c0b3c68b94d2e3a46c90f874`
