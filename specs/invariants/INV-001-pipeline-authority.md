# INV-001 — Pipeline Authority

## Status
CERTIFIED

## Statement
Toda ejecución productiva de agente debe estar gobernada obligatoriamente por la máquina de estados `AgentPipeline`. No debe existir ninguna ruta o entrypoint productivo que permita invocar directamente `agente.run()` fuera de su autoridad.

## Scope
- Runtime Agent Control (`main.ejecutar_agentes`)
- Fast-Path Conversacional y Nivel 4 Full Replan
- Servidores Proxy y API HTTP (`localcode_server.py`)

## Preconditions
- El usuario envía un prompt o petición al backend a través de la UI o API.

## Required Behavior
- `main.ejecutar_agentes()` debe instanciar `AgentPipeline()` e invocar `pipeline.run_pipeline()`.
- La máquina de estados controla la secuencia `INIT -> PLAN -> EXPLORE -> EXECUTE -> VERIFY -> DIAGNOSE -> REPLAN`.
- La invocación efectiva de `agente.run()` solo se produce en el runner encapsulado dentro del estado `EXECUTE`.

## Forbidden Behavior
- Invocar `agente.run()` directamente desde `main.py` o `localcode_server.py` ignorando la máquina de estados `AgentPipeline`.
- Retornar resultados de agente sin pasar por la evaluación de verifier y métricas del pipeline.

## Evidence
- Static: Invocación de `AgentPipeline().run_pipeline()` en `mis_agentes_inteligentes/main.py#L159-L160`.
- Tests: `tests/test_state_machine.py`, `tests/test_sdd_conformance.py`.
- Runtime: Inspección de traza de logs de pipeline durante peticiones CHAT y ACTION.
- OS/Filesystem: N/A

## Related Tests
- `tests/test_state_machine.py::TestStateMachine::test_pipeline_state_sequence`
- `tests/test_sdd_conformance.py::TestSDDConformance::test_chat_contract_fast_path`

## Related Modules
- `mis_agentes_inteligentes/main.py`
- `mis_agentes_inteligentes/agent_pipeline.py`

## Audit
- Audit Candidate: v5.0.0 Release Candidate Audit
- Audit Date: 2026-08-29
- Verdict: PASS (0 bypasses detected)

## Certification
- Certified Release: v5.0.0
- Commit SHA: `b0157240d41d3a81c0b3c68b94d2e3a46c90f874`
