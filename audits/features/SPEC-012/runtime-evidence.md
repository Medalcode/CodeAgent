# Feature Runtime Evidence — SPEC-012

## Summary
- **Feature ID**: `SPEC-012`
- **Title**: Desktop Real-Time Pipeline EventSource Visualization
- **Source Modules**: `desktop_app.py`, `mis_agentes_inteligentes/localcode_server.py`, `mis_agentes_inteligentes/agent_pipeline.py`
- **Test Suite**: `tests/test_desktop_pipeline_visualization.py`
- **Status**: **VERIFIED**

---

## 1. Desktop UI JavaScript SSE Contract
File: [`desktop_app.py`](file:///c:/Users/Jonatthan/Documents/Github/CodeAgent/desktop_app.py)

Functions Implemented:
```javascript
let currentPipelineEventSource = null;

function connectPipelineSSE(taskId) {
  closePipelineSSE();
  try {
    const sseUrl = '/api/pipeline/events?task_id=' + encodeURIComponent(taskId);
    currentPipelineEventSource = new EventSource(sseUrl);
    console.log('[CodeAgent UI] Connected to SSE pipeline stream for task_id: ' + taskId);
    ...
```

Fake Timer Removal Verification:
`secCount % 3 === 0` static timer completely removed from UI chat execution loop.

---

## 2. End-to-End Task-ID Correlation
Chain:
`desktop_app.py (task-ui-XYZ)` $\rightarrow$ `localcode_server.py (/api/agent/chat body task_id)` $\rightarrow$ `main.py (ejecutar_agentes task_id)` $\rightarrow$ `agent_pipeline.py (run session_id)` $\rightarrow$ `EventBus (session_id)` $\rightarrow$ `SSE GET /api/pipeline/events?task_id=task-ui-XYZ`

---

## 3. Automated Test Suite Execution
Executed `python -m unittest tests/test_desktop_pipeline_visualization.py`:
`Ran 7 tests in 32.730s. OK.`
