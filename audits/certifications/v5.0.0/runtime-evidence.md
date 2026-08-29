# Runtime Audit Evidence — Release v5.0.0

## Certified Commit
- **Commit SHA**: `b0157240d41d3a81c0b3c68b94d2e3a46c90f874`
- **Execution Environment**: Windows x64, Python 3.11

## 1. Fast-Path CHAT Execution Telemetry (`INV-001`, `INV-002`, `INV-006`, `INV-007`)
```json
{
  "user_prompt": "Responde únicamente con OK.",
  "task_type": "CHAT",
  "execution_level": "Nivel 1 (Chat Directo)",
  "tool_calls_count": 0,
  "execution_count": 0,
  "replans_count": 0,
  "verification_results": {
    "ast_status": "NOT_REQUIRED",
    "tests_status": "NOT_REQUIRED",
    "ruff_status": "NOT_REQUIRED"
  },
  "active_workspace_tools": []
}
```

## 2. Multi-Request Cross-Task Isolation Telemetry (`INV-003`)
```text
Sequence Executed in Memory (Same Backend Process):
1. Request A (ACTION: "Crea script1.py y ejecuta python script1.py"):
   - tool_calls_count: 1
   - execution_count: 1
   - TERMINAL_TASKS_BUFFER size: 1

2. Request B (CHAT: "Responde únicamente con OK."):
   - clear_terminal_tasks_buffer() executed at AgentPipeline.run() entry
   - tool_calls_count: 0  <-- (Clean isolation)
   - execution_count: 0
   - TERMINAL_TASKS_BUFFER size: 0
```

## 3. Desktop Concurrency & Lifecycle Telemetry (`INV-008`)
```text
Scenario 1 — Simultaneous Startup:
- Desktop A: Port=52630, PID=16444, Backend PID=1048
- Desktop B: Port=52631, PID=10388, Backend PID=16852
- Verdict: PASS (Independent dynamic TCP ports & UUIDs)

Scenario 5 — Abrupt Parent Crash:
- Desktop A (PID 16616) killed via TerminateProcess / SIGKILL.
- Backend A (Port 52672) parent monitor _is_parent_alive() -> False.
- Auto-shutdown completed in < 4 seconds. Port 52672 freed.
- Desktop B (Port 52673) remained 100% active and un-affected.
- Verdict: PASS (Zero orphan backend processes)
```
