# Change Impact Analysis — Real-Time Pipeline State & Event Streaming (SSE)

## Feature Title
Real-Time Pipeline State & Event Streaming (`GET /api/pipeline/events` — `SPEC-011`)

## Description
Integrates an HTTP Server-Sent Events (SSE) streaming endpoint `GET /api/pipeline/events` into `mis_agentes_inteligentes/localcode_server.py` that subscribes to the existing `EventBus` (`mis_agentes_inteligentes/runtime/event_bus.py`) and streams real-time state machine transitions (`INIT`, `PLAN`, `EXPLORE`, `EXECUTE`, `VERIFY`, `DIAGNOSE`, `REPLAN`, `CRITIC`, `DONE`) and execution telemetry to Desktop UI and external clients.

## Modified Components
- [x] `mis_agentes_inteligentes/localcode_server.py`
- [x] `mis_agentes_inteligentes/runtime/event_bus.py` (Extended with thread-safe queue listener helper `subscribe_queue`)
- [ ] `mis_agentes_inteligentes/agent_pipeline.py` (Unchanged — already publishes `STATE_ENTERED` / `STATE_EXITED`)

## Potentially Affected Invariants
- [x] **INV-001** (Pipeline Authority)
  - *Justification*: The SSE endpoint is strictly read-only and unidirectional. It streams events without bypassing `AgentPipeline` or executing arbitrary code.
- [x] **INV-008** (Desktop Lifecycle Safety)
  - *Justification*: The SSE streaming handler uses socket timeouts, heartbeats, and exception handling for `BrokenPipeError` to ensure active SSE streams disconnect cleanly without hanging `stop_server()` or parent process shutdown.

## Invariants NOT Affected
- **INV-002** (TaskContract Authority): No changes to contract generation or immutability.
- **INV-003** (Cross-Task Isolation): Events include `task_id` payload; stream supports filtering by `?task_id=...` parameter.
- **INV-004** (Intent Preservation): No changes to prompt routing or negations.
- **INV-005** (Failure Containment): SSE streaming errors are caught locally; failure of SSE does not crash pipeline execution.
- **INV-006** (Tool Isolation): Endpoint grants no tools.
- **INV-007** (Conditional Verification): Endpoint does not trigger verifiers.

## Required Regression Tests
- [x] `tests/test_sse_endpoint.py` (New Unit, Integration, Concurrency, and Disconnect test suite)
- [x] `tests/test_server_lifecycle.py` (Regression for INV-008)
- [x] `tests/test_sdd_conformance.py` (Regression for INV-001)
- [x] Full Test Suite (`python -m unittest discover -s tests`)

## Required Runtime Evidence
- Standalone feature evidence file `audits/features/SPEC-011/runtime-evidence.md`.
