# CODEAGENT — PHASE G1.0: DESKTOP PRODUCTIZATION READINESS AUDIT

## 1. Objective
Determine the readiness of the canonical CodeAgent Desktop UI for standalone productization, evaluating packaging feasibility, runtime dependencies, and architectural constraints without modifying production code.

## 2. Scope
- Desktop UI runtime path (`desktop_app.py` & `localcode_server.py`).
- Packaging constraints (PyInstaller, Nuitka).
- Dependency closure (Python, Git, Ollama).
- Desktop Lifecycle Safety and MVP definition.

## 3. Current Desktop Architecture
The architecture strictly follows the established canonical boundaries:
- **GUI Host**: `desktop_app.py` (PyWebView).
- **Backend API**: `localcode_server.py` (HTTP/SSE Server).
- **Frontend**: `localcode_claude_ui.html` (Vanilla JS/HTML).

## 4. Runtime Flow
1. User executes `desktop_app.py`.
2. App checks for Ollama (background launch if absent).
3. App spawns `localcode_server.py` via `subprocess.Popen` using `sys.executable`.
4. App creates PyWebView window pointing to `localhost:<port>`.
5. Frontend connects via HTTP/SSE to backend.
6. Backend orchestrates tasks using `agent_pipeline.py`, which spawns `pytest` and scripts using `os.sys.executable`.
7. Window close event triggers server shutdown.

## 5. Dependency Closure
- **Python Standard Library**: `os`, `sys`, `subprocess`, `threading`, `sqlite3`, etc.
- **Third-Party Python**: `webview` (PyWebView), `requests`, `pytest`.
- **External Executables**: `git.exe`, `ollama.exe`.
- **Repository-local**: `sdd_contract`, `cognitive_directives`, `storage`.
- **Assets**: `localcode_claude_ui.html`.
- **Generated**: `codeagent_desktop.db`, `sesiones/` JSONs.

## 6. External Dependencies
- **Git**: Hard requirement for workspace diffs and AST status (`subprocess.run(["git", "status"])`).
- **Ollama**: Hard requirement for local inference (`subprocess.Popen(["ollama", "serve"])`).

## 7. Filesystem Dependencies
- **Database**: `DB_FILE_PATH` is generated relative to the source repository (`mis_agentes_inteligentes/codeagent_desktop.db`).
- **Static Assets**: HTML paths are resolved via `BASE_DIR`.

## 8. Process/Lifecycle Model
- 1 Main UI Process.
- 1 Backend Server Process.
- N Ephemeral Subprocesses (pytest, Ruff, Python scripts, Git).
- 1 External Daemon (Ollama).

## 9. GUI Capability Matrix
| Capability | Status |
|------------|--------|
| Start a task | COMPLETE |
| Select workspace | COMPLETE (`open_folder_dialog`) |
| Display task progress | COMPLETE |
| Display agent events | COMPLETE (SSE) |
| Display tool execution | COMPLETE |
| Display verification | COMPLETE |
| Display failures/recovery | COMPLETE |
| Cancellation | COMPLETE (`/api/tasks/<task_id>/cancel`) |
| Session Lifecycle | COMPLETE |
| Error states | COMPLETE |

## 10. Standalone Execution Matrix
| Scenario | Result |
|----------|--------|
| Clean Windows Machine | FAILS (missing Python, Git, Ollama) |
| Without Dev Environment | FAILS (relies on `pytest` in `sys.executable`) |
| Without Git | FAILS (`agent_pipeline.py` crashes on status) |
| From different working dir | WORKS WITH CONFIGURATION |
| No pre-existing DB | WORKS (SQLite auto-initializes) |

## 11. Packaging Feasibility Matrix
| Strategy | Feasibility | Risk Level |
|----------|-------------|------------|
| PyInstaller | **FAILS STRUCTURALLY** | LEVEL D (Protected Block) |
| Nuitka | **FAILS STRUCTURALLY** | LEVEL D (Protected Block) |
| Portable Embedded Python | **WORKS** | LEVEL B (Controlled) |

## 12. PyInstaller Assessment
**Verdict: STRUCTURAL FAILURE**
`agent_pipeline.py` explicitly uses `os.sys.executable` to spawn `pytest` and execute Python scripts (`[os.sys.executable, "-m", "pytest"]`). If packaged with PyInstaller, `sys.executable` points to the compiled bootloader (`CodeAgent.exe`), which cannot accept Python module arguments. Because `agent_pipeline.py` is **PROTECTED** and cannot be refactored merely to facilitate packaging, PyInstaller cannot be used natively without massive architectural violations.

## 13. Nuitka Assessment
**Verdict: STRUCTURAL FAILURE**
Fails for the exact same `sys.executable` reasons as PyInstaller.

## 14. Alternative Assessment: Portable Embedded Python
**Verdict: HIGHLY FEASIBLE**
By bundling the official Windows Python Embeddable package alongside the repository files and a lightweight wrapper launcher (`CodeAgent.exe` -> `python.exe desktop_app.py`), the runtime environment remains exactly the same as the development environment. `sys.executable` correctly resolves to a real `python.exe`, completely preserving the canonical `agent_pipeline.py` without a single line of modification.

## 15. Desktop Lifecycle Risk Assessment
- **Read-Only Installation Path**: Defaulting `CODEAGENT_DB_PATH` to the source directory will cause crashes if installed in `C:\Program Files`. The database must be moved to `%APPDATA%\CodeAgent`. (LEVEL C - HIGH RISK).
- **Orphan Processes**: If PyWebView crashes unexpectedly, the Python server background process may remain alive, locking ports. (LEVEL B - CONTROLLED).

## 16. Existing Test Coverage
- `test_e2e_real_desktop_lifecycle.py` and `test_localcode_server.py` validate API routes, startup, and task interactions.

## 17. Missing Test Evidence
- Clean-machine execution testing (requires a CI runner without Git/Python).
- Read-only filesystem database test (simulate `Program Files` locking).
- Standalone portable bundle execution test.

## 18. MVP-Desktop Definition
A standalone `.zip` containing:
1. Portable Python runtime (with required `site-packages`).
2. CodeAgent source code.
3. A `CodeAgent.exe` launcher.
*A user can unzip it anywhere, launch it, select a workspace, and run a task without manually installing Python.*

## 19. Executable Definition
A lightweight wrapper (C++ or Batch-to-Exe) that seamlessly locates the bundled `python.exe` and executes `desktop_app.py` while forwarding environment variables.

## 20. Risk Classification
- Reliance on `sys.executable` in `agent_pipeline.py`: **LEVEL D (PROTECTED)**
- Database inside source directory: **LEVEL C (HIGH RISK)**
- Implicit Git Requirement: **LEVEL C (HIGH RISK)**
- Implicit Ollama Requirement: **LEVEL B (CONTROLLED)**

## 21. Architectural Impact
The discovery that `agent_pipeline.py`'s protected status forbids PyInstaller is the most critical architectural finding. The Portable Embedded Python strategy is the only path that strictly respects the immutable nature of the state machine.

## 22. Recommended Packaging Strategy
**Portable Embedded Python Distribution.**
Bundle a fully functional Python runtime and launch it via a wrapper.

## 23. Minimum Implementation Plan
1. Shift `DB_FILE_PATH` to `%APPDATA%\CodeAgent\database` in `storage/database.py`.
2. Implement gracefully degraded startup alerts if `git.exe` is not found on the PATH.
3. Create a packaging script to download Python Embeddable, inject dependencies, copy the repo, and compile a wrapper launcher.

## 24. Rollback Strategy
Any preparation changes (like AppData path logic) will be non-destructive and fully compatible with the existing development setup. Git will be used to revert if instability occurs.

## 25. Explicit Non-Goals
No packaging tools were configured, no executables were built, and no code was modified during this audit.

## 26. Final Recommendation
Advance to controlled preparation (fixing AppData paths and missing Git alerts) before executing the packaging script.

---

# FINAL DECISION

**B — READY WITH CONTROLLED PREPARATION**
The canonical Desktop UI is functionally complete and highly capable. However, the database location and implicit environmental dependencies require minor preparatory adjustments before the Portable Python environment can be reliably bundled.
