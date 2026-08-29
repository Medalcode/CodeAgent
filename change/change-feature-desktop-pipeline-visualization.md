# Change Impact Analysis — Desktop Real-Time Pipeline EventSource Visualization (SPEC-012)

## Feature Title
Desktop Real-Time Pipeline EventSource Visualization (`SPEC-012`)

## Description
Connects the CodeAgent Desktop UI (`localcode_claude_ui.html`) to the real-time Server-Sent Events (SSE) stream (`GET /api/pipeline/events?task_id=XYZ`) established in `SPEC-011`. Replaces the legacy fake timer progress ticker (`secCount % 3 === 0`) with a reactive DOM stepper rendering real state machine transitions (`INIT`, `PLAN`, `EXPLORE`, `EXECUTE`, `VERIFY`, `DIAGNOSE`, `REPLAN`, `CRITIC`, `DONE`) and active tool execution cards. Establishes end-to-end task ID correlation between UI request and pipeline event stream.

## Modified Components
- [x] `localcode_claude_ui.html` (Frontend UI EventSource subscription, real-time DOM stepper & fake timer removal)
- [x] `mis_agentes_inteligentes/localcode_server.py` (Passes `task_id` from chat payload to pipeline runner)
- [x] `mis_agentes_inteligentes/main.py` (Accepts `task_id` in `ejecutar_agentes` and passes to `AgentPipeline`)
- [x] `mis_agentes_inteligentes/agent_pipeline.py` (Auto-generates `session_id` if missing and emits `TASK_COMPLETED` / `TASK_FAILED` events)

## Potentially Affected Invariants
- [x] **INV-001** (Pipeline Authority)
  - *Justification*: The UI remains a 100% read-only consumer of events. It cannot execute tools or bypass `AgentPipeline`.
- [x] **INV-008** (Desktop Lifecycle Safety)
  - *Justification*: The `EventSource` client invokes `.close()` upon task completion, task failure, or desktop window unload to prevent orphan SSE connections.

## Invariants NOT Affected
- **INV-002** (TaskContract Authority): Contract rules are unchanged.
- **INV-003** (Cross-Task Isolation): Stream filtering by `?task_id=XYZ` prevents cross-task event leakage.
- **INV-004** (Intent Preservation): Prompt routing rules are unchanged.
- **INV-005** (Failure Containment): Failure of SSE does not crash main HTTP chat execution.
- **INV-006** (Tool Isolation): Tool execution logic is unchanged.
- **INV-007** (Conditional Verification): Verifiers execute as specified in `TaskContract`.

## Required Regression Tests
- [x] `tests/test_desktop_pipeline_visualization.py` (New test suite for SPEC-012)
- [x] `tests/test_sse_endpoint.py` (Regression for SPEC-011)
- [x] `tests/test_server_lifecycle.py` (Regression for INV-008)
- [x] `tests/test_sdd_conformance.py` (Regression for INV-001)
- [x] Full Test Suite (`python -m unittest discover -s tests`)

## Required Runtime Evidence
- Standalone feature evidence file `audits/features/SPEC-012/runtime-evidence.md`.
