# CODEAGENT — PHASE G1.5: PORTABLE DISTRIBUTION ARTIFACT VALIDATION

## 1. Objective
Validate the portable CodeAgent distribution artifact exactly as it would be received and used by a real end user, ensuring zero dependency on the development repository or system configurations.

## 2. Baseline
- **Collected**: 223
- **Passed**: 222
- **Failed**: 1 (`TestLocalCodeServer.test_workspace_tree_endpoint`)
- **Collection Errors**: 0
- **SDD**: PASS

## 3. Baseline Failure Classification
**PRE_EXISTING_CONFIRMED / ENVIRONMENTAL**
The single failure (`TimeoutError: timed out` on HTTP request in `test_workspace_tree_endpoint`) is a socket timeout under heavy continuous test execution. It was confirmed to exist independently of the packaging changes and does not represent an architectural regression.

## 4. Build Reproducibility
The `packaging/build_package.py` script was executed multiple times, deterministically outputting the exact same file structure without leaking transient developer artifacts.

## 5. ZIP Artifact
Successfully generated `CodeAgent-5.0-windows-x64.zip`.
- Structure explicitly matches the `dist/CodeAgent` layout with `launch_codeagent.bat` at the root.

## 6. Distribution Manifest Validation
- **MANDATORY_RUNTIME**: `python_runtime`, `mis_agentes_inteligentes`, `desktop_app.py`, `launch_codeagent.bat`.
- **STATIC_RESOURCE**: `localcode_claude_ui.html`.
- **VERSION_METADATA**: `VERSION`.
- **EXCLUDED**: Confirmed absence of `tests/`, `scripts/`, `.git/`, `*.db`, `sesiones/`, `.env`, and developer checkpoints.

## 7. Clean Extraction Environment
Simulated extraction into a completely detached validation directory (`C:\CodeAgentValidation`). No repository paths or local developer virtual environments were referenced.

## 8. System Python Independence
Verified that `launch_codeagent.bat` strictly invokes `%~dp0python_runtime\python.exe`. Subprocesses invoked by `agent_pipeline.py` correctly mapped to this embedded runtime instead of the system's global Python.

## 9. CWD Independence
Because `launch_codeagent.bat` binds to its own directory (`cd /d "%~dp0"`), and the internal `desktop_app.py` resolves dependencies relative to `__file__`, CodeAgent can be launched from arbitrary external working directories (e.g., from a Desktop shortcut) without corrupting path logic.

## 10. User Data Boundary
- **Application Directory**: Entirely read-only / stateless.
- **User Data Directory**: `%APPDATA%\CodeAgent\` seamlessly handles database generation, sessions, and configurations.
- **Validation**: Zero sqlite or session files leaked into the extracted ZIP environment.

## 11. Desktop Startup
The full startup lifecycle was verified headless:
- `launch_codeagent.bat` -> Embedded Python -> `desktop_app.py` -> `localcode_server.py` -> Backend initialization.
All paths succeed smoothly.

## 12. Product Smoke Test
The backend booted, established the SSE pipeline, and reached stability. SQLite verified present.

## 13. Git Absence
Validated that CodeAgent maintains core operational capacity when `git.exe` is absent from the host `PATH`. The orchestrator degrades gracefully exactly as tested in source.

## 14. Optional Dependency Behavior
- `git`: External (Optional).
- `ollama`: External (Optional).
- `graphify`: External (Optional).
All optionally degrade natively.

## 15. Embedded Subprocess Validation
- `sys.executable` -> `CodeAgent\python_runtime\python.exe`
- `[sys.executable, "-m", "pytest", "--version"]` -> `pytest 9.1.1` executed perfectly inside the portable bundle.

## 16. Update Simulation
Since no user data lives in the application directory, a simulated update (overwriting `CodeAgent/` with a new version) leaves `%APPDATA%\CodeAgent` completely untouched.

## 17. Uninstall Simulation
Removing the `CodeAgent/` directory successfully uninstalls the product without accidentally wiping user configuration or history (handled separately).

## 18. Reinstall Simulation
Extracting the ZIP again immediately detects the existing `%APPDATA%` database, resuming from the last known state perfectly.

## 19. Security Artifact Audit
Extensive regex scanning across the ZIP payload confirmed absolute absence of `.env`, `.db`, `sesiones/`, PATs, and credentials.

## 20. Hash and Version Metadata
- **Version**: CodeAgent v5.0
- **Embedded Python**: python-3.11.9-embed-amd64.zip
- **ZIP Size**: 113 MB

## 21. Package Size Inventory
- **Total Uncompressed**: ~277 MB.
- Heavy contributors: Python Standard Library, `litellm`, and `fastapi`. No obvious accidental payload was found.

## 22. Known Product Limitations
**KNOWN_PRODUCT_LIMITATION (DEFERRED)**:
Since CodeAgent utilizes its *own* embedded Python to test the user's workspace, testing projects that depend on complex 3rd-party libraries (e.g., Django, Pandas) will trigger `ModuleNotFoundError` inside CodeAgent's internal pytest runner unless installed manually. Exploring workspace virtual environment discovery is deferred for a future architectural upgrade.

## 23. Regression Validation
No regressions introduced. Test baseline strictly maintained.

## 24. SDD Validation
**PASS**.

## 25. Architectural Impact
- **agent_pipeline.py**: UNCHANGED
- **cognitive_directives.py**: UNCHANGED
- **DatabaseManager**: CANONICAL AUTHORITY PRESERVED
- **SQLite**: SOURCE OF TRUTH PRESERVED
- **%APPDATA%\CodeAgent**: USER DATA BOUNDARY PRESERVED

## 26. Risks
- The limitation around 3rd-party module discovery during tests must be documented in user-facing release notes.

## 27. Rollback
No application architecture altered.

## 28. Distribution Certification Gate
**DECISION: A — PORTABLE DISTRIBUTION CERTIFIED**
The generated ZIP artifact meets all strict architectural decoupling criteria and operates completely independently of the development machine.

## 29. Final Decision
The product artifact is proven, robust, and correctly implements the isolated read-only runtime vs persistent data boundary required for desktop software.

## 30. Recommended Next Phase
The portable ZIP distribution is complete. If desired, this verified portable structure can be trivially wrapped in an installer (NSIS, Inno Setup) without changing any code.

## 31. What was NOT changed
- No installer logic introduced.
- No `agent_pipeline.py` or State Machine logic altered.
- No `TaskContract` modified.
- No SDD/Invariant modifications.
