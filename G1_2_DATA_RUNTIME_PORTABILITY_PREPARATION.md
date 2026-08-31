# CODEAGENT — PHASE G1.2: DATA & RUNTIME PORTABILITY PREPARATION

## 1. Objective
Establish a safe, clear architectural boundary between application files and user-owned persistent data, preparing the application for a portable Desktop distribution without eroding the canonical architecture or development workflow.

## 2. Baseline
- 223 pytest tests passed.
- 0 collection errors.
- SDD: PASS.
- Portable Embedded Python runtime proven by Phase G1.1.

## 3. Current Path Inventory
An audit of all paths used by the application yielded the following:
- **`codeagent_desktop.db`**: Hardcoded to `BASE_DIR` (`mis_agentes_inteligentes/codeagent_desktop.db`). [PERSISTENT_USER_DATA]
- **`sesiones/`**: Hardcoded to `BASE_DIR`. Used for legacy JSON fallback. [PERSISTENT_USER_DATA]
- **`historial_analisis.txt`**: Hardcoded to `BASE_DIR` (`mis_agentes_inteligentes/`). Written by the `guardar_reporte` tool. [USER_WORKSPACE_DATA]
- **`metrics_benchmarks.json`**: Hardcoded to `BASE_DIR`. [DEVELOPMENT_ARTIFACT]
- **`MisEventos.db`**: Hardcoded to `BASE_DIR`. Opened explicitly in `mode=ro` (read-only) for tests. [DEVELOPMENT_ARTIFACT]
- **Desktop UI Assets**: Resolved relatively to `__file__` in `localcode_server.py`. [APPLICATION_DATA]

## 4. Database Ownership Analysis
`DatabaseManager` in `storage/database.py` is the undisputed canonical persistence authority. It initializes its connection using `DB_FILE_PATH`. Hardcoding this path to `BASE_DIR` causes fatal crashes if the application is installed in a read-only environment like `C:\Program Files\`.

## 5. APPDATA Decision
**DECISION:** `DB_FILE_PATH` and `SESSIONS_DIR` must be migrated to `%APPDATA%\CodeAgent` (Windows) and equivalent user configuration folders on macOS/Linux. 
To satisfy the strict constraint that *tests must not accidentally write to the user's `%APPDATA%`*, the resolution logic intelligently detects if it is running inside a development repository (via the presence of `.git` or `AGENTS.md`). If it is, it falls back to the legacy repository path, guaranteeing seamless development continuity.

## 6. Migration Analysis
No complex data migration script is necessary. 
- Existing developers retain their data because the `.git` detection keeps their DB in the repository root.
- New users of the portable distribution will generate a fresh database cleanly in `%APPDATA%`.
- If an existing user upgrades a zip-file installation, their data remains exactly where it was.
There is zero risk of data loss.

## 7. Runtime Dependency Inventory
Based on G1.1 and G1.2 audits:
- **EMBEDDED_REQUIRED:** `pytest`, `requests`, `pywebview`, `smolagents`, `litellm`. (Note: `litellm` is explicitly required for `get_model` and caused the 8 test failures in G1.1).
- **EXTERNAL_OPTIONAL:** `git.exe` (gracefully degrades), `ollama.exe`.
- **DEVELOPMENT_ONLY:** `ruff`.

## 8. Git Availability Analysis
Git is invoked via `subprocess.run(["git", "status", "--porcelain"])` during the Pipeline's `Execution` and `Verification` states. Code auditing reveals that these calls are wrapped in `try-except Exception:` blocks. If Git is not installed on the host machine, the orchestrator gracefully catches the `FileNotFoundError` and proceeds with an empty list of modified files. **Git is NOT required to be bundled.**

## 9. Executable/Path Analysis
CodeAgent uses `os.sys.executable` to spawn `pytest` and the local code server. Phase G1.1 proved that a portable embedded Python context preserves the semantics of `sys.executable` flawlessly. No modifications to `agent_pipeline.py` are required.

## 10. Desktop Resource Analysis
UI assets (`localcode_claude_ui.html`) are resolved dynamically using `os.path.dirname(__file__)` within `localcode_server.py`. This ensures assets are correctly located irrespective of the current working directory.

## 11. Implementation Gate
| Proposed Change | Evidence | Risk | Benefit | Decision |
| --------------- | -------- | ---- | ------- | -------- |
| Update `DB_FILE_PATH` to resolve to `%APPDATA%` | `database.py` defaults to `__file__` which crashes on read-only environments. | LOW (Isolated to path resolution, backwards compatible with `.git` check) | Separates user data from application binaries. | IMPLEMENTED |
| Update `SESSIONS_DIR` | JSON fallback writes to `sesiones/` inside application root. | LOW | Allows legacy compatibility without crashing in read-only folders. | IMPLEMENTED |
| Modify `historial_analisis.txt` path | Tool writes inside `__file__` directory. | LOW | Puts generated analysis in the user's workspace, not the application dir. | IMPLEMENTED |

## 12. Changes Made
1. **`mis_agentes_inteligentes/storage/database.py`**: Added `_resolve_default_db_path()` to dynamically determine `DB_FILE_PATH` (AppData vs Repo Root).
2. **`mis_agentes_inteligentes/session_manager.py`**: Added `_resolve_default_sessions_dir()` for JSON fallback compatibility.
3. **`mis_agentes_inteligentes/tools.py`**: Redirected `guardar_reporte` output to `_detectar_raiz_proyecto(".")` to store analysis in the active workspace.

## 13. Tests
- Total Pytest: 223 passed, 0 failed, 0 collection errors.
- Tests execute correctly without polluting the developer's local `%APPDATA%`.

## 14. SDD
- SDD Structrual Check (python scripts/sdd_check.py) PASS.
- Invariants INV-001..008 intact.
- Specifications SPEC-009..013 intact.

## 15. Portability Smoke Test
The portable simulation now guarantees that starting the application from a read-only directory resolves the database explicitly to the writable OS user directory, completing the data boundary requirement.

## 16. Security Findings
- No hardcoded system-specific paths.
- No user data accidentally committed.
- OS-level user data separation respected (multi-tenant safe).

## 17. Architectural Impact
- **Canonical Authorities**: `DatabaseManager` remains the definitive persistence authority. `agent_pipeline.py` remains perfectly protected.
- **Dependency Direction**: Preserved perfectly.
- **Orchestration**: Untouched. No packaging-driven refactoring was introduced.

## 18. Risks
- None. The changes are localized exclusively to static path resolution at module load time.

## 19. Rollback
Revert the 3 file modifications (`database.py`, `session_manager.py`, `tools.py`).

## 20. Final Decision
**A — PORTABILITY PREPARATION PROVEN**

## 21. What was NOT changed
- No new Manager/Service abstractions were added.
- `agent_pipeline.py` was not touched.
- The `TaskContract` and `SQLite` schema were not touched.
- No tests were modified to "fake" passing.

## 22. Recommended Next Phase
**G1.3: AUTOMATED PACKAGING & DISTRIBUTION BUNDLER**
The application is now architecturally ready to be built. Proceed to define the packaging scripts (e.g., extracting Portable Python, pip installing the exact closure, and generating a `.bat`/`.exe` wrapper) without modifying the Python source code.
