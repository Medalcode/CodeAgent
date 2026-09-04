# CODEAGENT — G2.5 DESKTOP NEXT-PHASE ARCHITECTURE AUDIT

## 1. Objective
Audit the post-G2.4 desktop architecture to determine if technical debt or product gaps exist that justify a G2.5 phase.

## 2. Baseline
Desktop UI interacts with `localcode_server.py`, which orchestrates `AgentPipeline` synchronously. `desktop_app.py` exposes native PyWebView APIs for file system access.

## 3. Architecture Map
```text
User 
 ↓
Desktop UI (PyWebView + HTML/JS)
 ↓
[1. File Dialogs] -> PyWebView API -> desktop_app.py
[2. Execution]    -> HTTP POST /api/agent/chat -> localcode_server.py -> main.py (Synchronous)
[3. Cancellation] -> HTTP POST /api/tasks/<id>/cancel -> runtime.py (Asynchronous Engine)
```

## 4. Evidence
- `desktop_app.py:DesktopIDEApi.open_folder_dialog` incorrectly returns `None` after successfully updating the workspace.
- `localcode_claude_ui.html` JS expects a dictionary with `path`. Since it receives `None`, it triggers a fallback browser `<input type="file" webkitdirectory>` dialog, resulting in a double-picker UX.
- `localcode_server.py` contains 3 duplicated PowerShell dialog implementations (`_ps_file_dialog`, etc.) and endpoints (e.g. `/api/fs/open_folder_dialog`) that the frontend NEVER calls. The frontend uses PyWebView for opening and standard POST for saving.
- The frontend execution invokes `/api/agent/chat` (synchronous), completely bypassing the `runtime.py` asynchronous engine.
- Clicking "Cancel" simply aborts the frontend HTTP fetch and flags the SQLite DB, but the `ejecutar_agentes` synchronous thread cannot be pre-empted mid-execution, causing zombie tasks on the server.

## 5. Findings
- **A. Confirmed Bug**: Double Folder Picker UX. The native dialog opens, then the fallback browser dialog opens because of the missing return statement in `desktop_app.py`.
- **B. Architectural Risk**: Broken Cancellation. Synchronous HTTP execution prevents true thread pre-emption, creating zombie execution tasks that burn LLM resources after the user cancels.
- **C. Maintainability Issue**: Dead code and duplicated native OS dialogs inappropriately placed in the HTTP server (`localcode_server.py`).

## 6. Protected Areas
- `AgentPipeline` and `Verification Engine` logic (INV-001, INV-007).
- SDD Contracts and Task Classification.

## 7. Candidate Improvements
### Candidate 1: Repair Workspace Picker UX & Purge Native Dialogs from Server
- **Problem**: Double picker UX due to `None` return; HTTP server bloated with unused Desktop native dialogs.
- **Impact**: Frustrating UX, dead code.
- **Boundary**: `desktop_app.py`, `localcode_server.py`.
- **Risk**: Low.
- **Expected Benefit**: Clean server layer, single picker UX.
- **Minimal Change**: Add the return dictionary in `desktop_app.py` and delete `_ps_*` functions from `localcode_server.py`.

### Candidate 2: Asynchronous UI Execution for True Cancellation
- **Problem**: Cancel button does not stop the agent on the server mid-execution.
- **Impact**: High resource consumption (zombie agents).
- **Boundary**: `localcode_claude_ui.html`, `localcode_server.py`.
- **Risk**: Medium. Requires changing `/api/agent/chat` to delegate to `runtime.start_task` (which is already fully built and tested).
- **Expected Benefit**: Actual pre-emptive cancellation and unblocked HTTP server.

## 8. Risk Assessment
Candidate 1 is highly localized and trivial to fix. Candidate 2 requires careful alignment between the UI event loop and the existing REST API, but relies entirely on the already-built `runtime.py` engine, making it fundamentally safe and architecturally coherent.

## 9. Testing Impact
Candidate 1 requires no new tests. Candidate 2 would benefit from ensuring `test_regression.py` supports asynchronous task initiation.

## 10. Recommended G2.5 Scope
Proceed with **Candidate 1** and **Candidate 2**. They directly address glaring bugs in the Desktop experience (UX flow and Cancellation).

## 11. Explicitly Rejected Work
**WHAT WE SHOULD NOT DO:**
- **Refactoring AgentPipeline**: Do not refactor `agent_pipeline.py` into smaller files. There is no evidence of a boundary that justifies the risk. The current orchestration is stable.
- **Removing Web Fallbacks**: Do not remove the HTML `<input type="file">` fallback elements. They remain necessary when the UI is accessed via a standard Chrome browser instead of the Desktop app.
- **Modifying Verification**: Verification is working perfectly and should not be touched.

## 12. No Changes
No code was modified during this audit phase.

## 13. Conclusion
G2.5 is formally justified by observable Product Gaps (Broken Cancellation) and Confirmed Bugs (Double Picker UX).
