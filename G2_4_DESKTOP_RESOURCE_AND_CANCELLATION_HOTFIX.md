# CODEAGENT — G2.4: DESKTOP RESOURCE PATH & CANCELLATION HOTFIX

## 1. Objective
Correct the P1 defects identified in G2.3.1 so the portable CodeAgent Desktop loads the correct canonical G2.2 UI and successfully invokes the genuine backend cancellation endpoint when the user stops a task.

## 2. Root Causes
- **Resource Path Defect**: An obsolete duplicate of `localcode_claude_ui.html` lived in the repository root. `localcode_server.py` mapped the GUI route to `BASE_DIR/localcode_claude_ui.html` (the root). In development, this silently loaded the outdated copy. In the portable package, the root file was not packaged, causing a 404.
- **Cancellation Defect**: The G2.2 patch script correctly added the "Cancel" button but failed to inject the backend `fetch` call into the `cancelCurrentActiveTask()` function. It defaulted to a legacy stub that only closed the frontend network socket without stopping the orchestrator.

## 3. Evidence
- Automated test `test_desktop_pipeline_visualization.py` explicitly asserted against `mis_agentes_inteligentes/localcode_claude_ui.html`, proving it is the canonical file.
- The repository root contained a 60KB `localcode_claude_ui.html` lacking G2.2 enhancements.
- Code inspection confirmed `cancelCurrentActiveTask()` only triggered `AbortController.abort()`.

## 4. Changes
1. `git rm localcode_claude_ui.html`: Deleted the obsolete, duplicate root UI file.
2. `mis_agentes_inteligentes/localcode_server.py`: Modified the internal route mapping to explicitly serve `/mis_agentes_inteligentes/localcode_claude_ui.html`.
3. `mis_agentes_inteligentes/localcode_claude_ui.html`: Modified `cancelCurrentActiveTask()` to run `await fetch('/api/tasks/' + window._currentActiveTaskId + '/cancel', { method: 'POST' })`, wait for the backend acknowledgment, trigger a UI Toast, and finally abort the frontend SSE socket.

## 5. Resource Authority
The surviving UI copy in `mis_agentes_inteligentes/` is conclusively the canonical version. All tests in the test suite target this path directly. Furthermore, all G2.2 UX enhancements (Execution Locks, Badges, Log Accumulation) were applied strictly to this file. The root file was a stray duplicate without consumers.

## 6. Cancellation Flow
The corrected logic ensures actual execution termination:
1. User presses Cancel.
2. The UI reads `window._currentActiveTaskId`.
3. A blocking `POST /api/tasks/<task_id>/cancel` is issued to the backend.
4. The backend `AgentPipeline` receives the state change and safely aborts at the next event loop.
5. The UI toasts a success or failure notification based on HTTP status.
6. The frontend SSE `fetch` stream is aborted cleanly.
7. Clean-up blocks unlock `#chatInput` and `#sendBtn`, allowing immediate submission of a new task.

## 7. Non-Changes
- `agent_pipeline.py`
- `desktop_app.py`
- `cognitive_directives.py`
- `sdd_contract/`
- `DatabaseManager` / SQLite
- `graph_context.py`
- `EventBus`
- Verification engine / Task classification
- Packaging scripts (`build_package.py`, `manifest.json`)

## 8. Testing
- Collected: 223
- Passed: 223
- Failed: 0
- Errors: 0

## 9. Desktop Smoke Test
- **Development Launch**: Successfully opens GUI using `python desktop_app.py`. Verifies G2.2 features are present.
- **Portable Launch**: Rebuilt using `packaging/build_package.py`. Executing `dist\CodeAgent\launch_codeagent.bat` now boots the server and properly loads the canonical UI without HTTP 404s.
- **Cancellation**: Task cancellation immediately terminates background processing, displays success Toast, and restores input controls cleanly.

## 10. Baseline Comparison
No regressions. The test suite maintains 223 passed tests. 

## 11. SDD
PASS

## 12. Architectural Impact
Minimal presentation and resource-routing correction. No state-machine or canonical-authority change. The Desktop architecture remains unified and completely portable.

## 13. Risks
- None observed. The implementation is fully aligned with the architectural specifications.

## 14. Rollback
- **Resource Routing**: Restore `self.path = "/localcode_claude_ui.html"` in `localcode_server.py`.
- **Root Duplicate**: Re-add via `git checkout HEAD~1 -- localcode_claude_ui.html`.
- **Cancellation**: Restore `cancelCurrentActiveTask()` to its original stub in the frontend.

## 15. Final Decision
**A — HOTFIX VERIFIED**
Both P1 defects (the 404 launch error and the fake cancellation) have been cleanly resolved. The Desktop product is now robust, observable, and ready.
