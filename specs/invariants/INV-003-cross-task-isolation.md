# INV-003 — Cross-Task Isolation

## Status
CERTIFIED

## Statement
Ninguna petición ejecutada en el backend puede heredar telemetría, buffers de herramientas (`TERMINAL_TASKS_BUFFER`), estado de ejecución o resultados de una petición previa dentro de la misma instancia de proceso.

## Scope
- `mis_agentes_inteligentes/agent_pipeline.py`
- `mis_agentes_inteligentes/tools.py` (`TERMINAL_TASKS_BUFFER`)

## Preconditions
- El backend ejecuta múltiples peticiones en la misma instancia de proceso (ej. `ACTION` seguida de `CHAT`).

## Required Behavior
- Al inicio de `AgentPipeline.run()` (cuando `initial_replans == 0`), se invoca automáticamente `clear_terminal_tasks_buffer()`.
- Toda petición `CHAT` consecutiva inicia con `tool_calls_count = 0`, `execution_count = 0` y residual buffer de 0 elementos.

## Forbidden Behavior
- Acumular eventos de terminal en `TERMINAL_TASKS_BUFFER` de forma persistente entre peticiones distintas, provocando que peticiones CHAT reporten invocaciones falsas de herramientas.

## Evidence
- Static: `clear_terminal_tasks_buffer()` al inicio de `AgentPipeline.run()` en `mis_agentes_inteligentes/agent_pipeline.py#L295-L298`.
- Tests: `tests/test_cross_task_telemetry_isolation.py`.
- Runtime: Demostración empírica en secuencia de runtime real `ACTION -> CHAT -> CHAT` en la misma instancia backend.
- OS/Filesystem: Verificación del estado en memoria de `TERMINAL_TASKS_BUFFER`.

## Related Tests
- `tests/test_cross_task_telemetry_isolation.py::TestCrossTaskTelemetryIsolation::test_telemetry_clean_reset_on_chat_after_action`

## Related Modules
- `mis_agentes_inteligentes/agent_pipeline.py`
- `mis_agentes_inteligentes/tools.py`

## Audit
- Audit Candidate: v5.0.0 Release Candidate Audit
- Audit Date: 2026-08-29
- Verdict: PASS (Aislamiento verificado en runtime real)

## Certification
- Certified Release: v5.0.0
- Commit SHA: `b0157240d41d3a81c0b3c68b94d2e3a46c90f874`
