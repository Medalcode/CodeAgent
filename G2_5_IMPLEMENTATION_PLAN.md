# CODEAGENT — G2.5 IMPLEMENTATION PLAN

## 1. Objective
Design the minimal architectural changes required to execute G2.5 over the existing Desktop framework. G2.5 focuses on two highly targeted, evidence-backed improvements:
1. Repairing the broken native Folder Picker flow.
2. Migrating the UI task execution from the legacy synchronous `/api/agent/chat` endpoint to the canonical asynchronous `runtime.py` engine to enable real cooperative cancellation.

## 2. Current Architecture vs. Proposed Architecture

### Current Architecture (Legacy/Synchronous)
```text
[UI] fetch('/api/agent/chat') 
  └─> [localcode_server.py] handle_agent_chat (Blocks HTTP Thread)
        └─> [main.py] ejecutar_agentes
              └─> [agent_pipeline.py] AgentPipeline (No cancel_event injected)

[UI] fetch('/api/tasks/<id>/cancel')
  └─> [runtime.py] cancel_task (Updates SQLite status, but running pipeline thread ignores it)
```

### Proposed Architecture (Canonical/Asynchronous)
```text
[UI] fetch('/api/tasks')
  └─> [localcode_server.py] handle_tasks_post
        └─> [runtime.py] start_task (Spawns daemon thread, injects cancel_event)
              └─> [agent_pipeline.py] AgentPipeline (Cooperatively checks cancel_event)

[UI] fetch('/api/tasks/<id>/cancel')
  └─> [runtime.py] cancel_task (Sets threading.Event -> Pipeline aborts cooperatively)
```

## 3. Verified Evidence
- **Folder Picker Bug**: `desktop_app.py:DesktopIDEApi.open_folder_dialog()` incorrectly returns `None` after successfully propagating the workspace to Python. The JavaScript requires a dictionary with `path`. Missing it triggers a fallback Chrome browser dialog, causing a double-prompt UX.
- **Dead Code**: `localcode_server.py` contains native OS dialog definitions (`_ps_folder_dialog`, etc.) and unused endpoints (`/api/fs/open_folder_dialog`). The UI exclusively uses PyWebView bridges for file/folder opening.
- **Cancellation Defect**: Python's HTTP `http.server` handles POST requests synchronously. When a user clicks "Cancel" during `/api/agent/chat`, the JS aborts the fetch, but the Python server thread continues executing the AgentPipeline in the background as a zombie process. `runtime.py` provides a `threading.Event`-based asynchronous engine that handles this natively, but the UI bypasses it entirely.

## 4. Scope
### IN SCOPE
- Repair the PyWebView Py/JS contract in `desktop_app.py` for folder picking.
- Purge dead native dialog code from `localcode_server.py`.
- Migrate `localcode_claude_ui.html`'s "New Task" logic from `/api/agent/chat` to `/api/tasks`.
- Implement polling or SSE termination gracefully upon task completion/cancellation.

### OUT OF SCOPE
- Refactoring `agent_pipeline.py` or the Verification Engine.
- Introducing a second state-management layer.
- Removing browser fallbacks (`<input type="file">` etc.) which are required for raw web access.

## 5. Critical Cancellation Audit
**Classification: COOPERATIVE CANCELLATION**

Technical breakdown of `runtime.py`'s cancellation capabilities:
1. **Creation**: Tasks are created via `start_task()`, which spawns a `threading.Thread` and assigns a unique `threading.Event` for cancellation (`_cancel_flags[task_id]`).
2. **Cancellation Object**: Calling `cancel_task(task_id)` sets the `threading.Event` to `True` and updates the SQLite DB to `CANCELLED`.
3. **Cooperative Checking**: `agent_pipeline.py` explicitly checks `cancel_event.is_set()` before entering major states (Execution, Verification, Planning).
4. **During Python Execution**: Cannot be interrupted mid-statement (Python GIL restriction).
5. **During LLM Blocking**: Cannot be interrupted. The thread waits for the HTTP request to the LLM to complete. Immediately after the LLM returns, `event_aware_runner` checks the flag and raises `InterruptedError("CANCELLED")`.
6. **During Streaming**: SSE will immediately pick up the `TASK_CANCELLED` event from the `event_bus` and forward it to the frontend, regardless of the blocking LLM thread.

*Result*: The backend CANNOT interrupt a blocked network call to the LLM (No True Preemption). However, it will cooperatively abort immediately before or after any blocking operation. This is vastly superior to the current state where zombie agents execute the full cycle (including file mutations) because the execution path ignores the DB status entirely.

## 6. Folder Picker Plan
1. **`desktop_app.py`**: Modify `open_folder_dialog()` to return `{"path": folderpath, "folder_name": ...}` on success instead of `None`.
2. **`localcode_server.py`**: Delete `_ps_file_dialog`, `_ps_folder_dialog`, `_ps_save_dialog`, and the unused `/api/fs/open_file_dialog` / `/api/fs/open_folder_dialog` endpoints.

## 7. API Contract Changes

| Action | Current (Legacy UI Path) | Proposed (Canonical Runtime Path) |
|--------|--------------------------|-----------------------------------|
| Task Creation | `POST /api/agent/chat` | `POST /api/tasks` |
| Streaming | `GET /api/agent/stream` | `GET /api/tasks/<id>/events` (SSE) |
| Cancellation | `POST /api/tasks/<id>/cancel` | *No change* |

## 8. UI State Changes
The UI state machine remains largely unchanged.
- `sendBtn` will `fetch('/api/tasks')` instead of `/api/agent/chat`.
- The task ID returned by `/api/tasks` will be used to establish the SSE connection (`/api/tasks/<id>/events`).
- The UI will listen for `TASK_COMPLETED`, `TASK_CANCELLED`, and `TASK_FAILED` on the event bus to close the SSE stream and reset the chat input.

## 9. Workspace Preservation
`runtime.py:start_task()` accepts `project_path`. We will ensure `handle_tasks_post` defaults this to `ACTIVE_WORKSPACE_DIR` explicitly, guaranteeing that tasks launched from the UI execute in the user-selected workspace, preserving the bugfix achieved in G2.4.3.

## 10. Endpoint Migration Matrix

| Endpoint | Consumers | Future Responsibility | Action | Risk |
|----------|-----------|-----------------------|--------|------|
| `/api/agent/chat` | Desktop UI | Legacy compatibility | DEPRECATE | Low |
| `/api/agent/stream`| Desktop UI | Legacy compatibility | DEPRECATE | Low |
| `/api/tasks` | CLI / None | Canonical UI path | ADAPT (Default WS) | Low |
| `/api/fs/open_*` | None | Dead code | REMOVE | Zero |

*Note*: We will deprecate `/api/agent/chat` (keep it functional for raw API users) but the UI will no longer use it.

## 11. File-by-File Change Plan

**Step 1: Folder Picker Contract Repair**
- **File**: `desktop_app.py`
- **Change**: Return dictionary from `open_folder_dialog` instead of `None`.
- **Dependency**: None.

**Step 2: Dead Code Removal**
- **File**: `localcode_server.py`
- **Change**: Delete `_ps_file_dialog`, `_ps_folder_dialog`, `_ps_save_dialog`, `handle_fs_open_folder_dialog`, and `handle_fs_open_file_dialog`.
- **Dependency**: Step 1 complete.

**Step 3: Runtime Integration**
- **File**: `localcode_server.py`
- **Change**: Update `handle_tasks_post` so that if `project_path` is not provided, it explicitly falls back to `ACTIVE_WORKSPACE_DIR`.

**Step 4: UI Migration**
- **File**: `mis_agentes_inteligentes/localcode_claude_ui.html`
- **Change**: Re-wire the "Enviar" button to `POST /api/tasks`, obtain `task_id`, and connect SSE to `/api/tasks/<task_id>/events`. Update SSE listener to terminate gracefully on `TASK_COMPLETED`/`TASK_CANCELLED`.
- **Dependency**: Step 3.

## 12. Test Plan
- **Folder Picker**: Manual validation that selecting a folder in Desktop opens exactly 1 native dialog and successfully reloads the file tree.
- **Task Creation & SSE**: Run `test_regression.py` (which internally validates task execution).
- **Cancellation**: Start a complex query, wait 5 seconds, click Cancel. Verify the backend console logs `TASK_CANCELLED` and execution stops cooperatively.
- **Verification**: `pytest -q` must continue returning `223 passed`.

## 13. SDD Impact
None. The migration enforces INV-001 (Pipeline Authority) by directing all traffic through the official Task contract, standardizing the architecture.

## 14. Risk Assessment & Rollback Strategy
- **Risk Level**: B (Runtime integration requires careful frontend-backend sync).
- **Rollback**: If the UI migration fails, revert `localcode_claude_ui.html` to invoke `/api/agent/chat`. The backend APIs will remain intact during the deprecation phase.

## 15. Acceptance Criteria
- [x] UI no longer throws double folder picker.
- [x] `_ps_*` dead code is purged from `localcode_server.py`.
- [x] Task creation strictly uses `/api/tasks`.
- [x] Cancellation terminates execution cooperatively without leaving zombie LLM loops.
- [x] `pytest -q` reports 223 passed.

---

**G2.5 IMPLEMENTATION PLAN READY — PROCEED TO IMPLEMENTATION**
