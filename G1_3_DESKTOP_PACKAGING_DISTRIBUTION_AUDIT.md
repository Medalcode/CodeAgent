# CODEAGENT — PHASE G1.3: DESKTOP PACKAGING & DISTRIBUTION ARCHITECTURE AUDIT

## 1. Objective
Determine the smallest safe architecture for distributing CodeAgent as a real Windows Desktop application, defining the strict boundaries between installation files, user data, and external toolchains, without prematurely writing the installer.

## 2. Baseline
- 223 pytest tests passed.
- 0 collection errors.
- SDD: PASS.
- Architecture and paths previously proven portable (G1.1 & G1.2).

## 3. Desktop Entrypoint Analysis
- **Entrypoint**: `desktop_app.py` serves as the primary launcher.
- **Boot Sequence**: `desktop_app.py` executes `main()`, automatically spins up `ollama` in the background (if installed), spawns `localcode_server.py` via `subprocess.Popen(sys.executable)`, and initializes the Native Window via `pywebview`.
- **Conclusion**: `desktop_app.py` is the only script that needs to be exposed as an executable/launcher.

## 4. Dependency Closure
- **MANDATORY_CORE**: `fastapi`, `uvicorn`, `sse_starlette`, `python-multipart`, `pywebview`, `requests`, `smolagents`.
- **DEVELOPMENT_ONLY**: `ruff`. (Used exclusively via internal `ast.parse` fallbacks in `agent_pipeline.py`; external CLI is not strictly bundled).
- **MANDATORY_BUNDLED_TOOL**: `pytest`. (Crucial: `agent_pipeline.py` currently invokes `[os.sys.executable, "-m", "pytest"]` directly against the user workspace. Thus, pytest *must* be included in the portable Python environment).

## 5. LiteLLM Classification
- **Classification**: **MANDATORY_CORE**. 
- **Evidence**: `test_local_model_provider` failures in G1.1 demonstrated that `smolagents.models.LiteLLMModel` relies unconditionally on the `litellm` library. This is the application's central router for OpenAI, Anthropic, Gemini, and Ollama. It must be explicitly included in the packaging manifest.

## 6. Pytest / SDD Classification
- **pytest**: **PRODUCTION RUNTIME**. Included because CodeAgent uses its *own* embedded Python to test the user's workspace.
- **scripts/sdd_check.py**: **DEVELOPMENT_ONLY**. CodeAgent never calls this during the product workflow. It is for repository integrity. Excluded from distribution.
- **tests/**: **DEVELOPMENT_ONLY**. Excluded from distribution.

## 7. Graphify Classification
- **Classification**: **EXTERNAL_OPTIONAL**.
- **Evidence**: `agent_pipeline.py` initializes `GraphContextEngine(graph_path="graph.json")`. It merely reads the output artifact. It explicitly instructs the agent *not* to import it in Python because it's a CLI tool. CodeAgent does not execute the tool; it only reads the graph. It is an external dependency.

## 8. Git Classification
- **Classification**: **EXTERNAL_OPTIONAL**.
- **Evidence**: `subprocess.run(["git", "status", "--porcelain"])` is wrapped in `try-except Exception:` blocks within `agent_pipeline.py`. If Git is not installed, the orchestrator gracefully degrades by assuming an empty list of modified files. Git does not need to be bundled.

## 9. Resource Inventory
- **BUNDLED**: `localcode_claude_ui.html` is the only major static resource. It resolves safely relative to `__file__`.
- **EXTERNAL_USER_FILE**: `AGENTS.md` (read from the active workspace).
- **GENERATED_RUNTIME**: Checkpoints and sessions (safely pointed to `%APPDATA%`).

## 10. Python Runtime Strategy Comparison
- **Strategy A (Portable Embedded Python + Directory)**: Preserves `os.sys.executable` semantics natively. Child processes spin up correctly.
- **Strategies B/C/D (PyInstaller / Nuitka)**: Replace `sys.executable` with a bootloader (`codeagent.exe`), breaking `[sys.executable, "-m", "pytest"]`.
- **Decision**: **Strategy A** is the only architecturally viable option that avoids rewriting `agent_pipeline.py`.

## 11. One-File vs One-Folder Analysis
- **One-File**: Extracts the entire Portable Python distribution (~50MB) to `%TEMP%` on every startup. This causes severe latency and frequent Antivirus false positives.
- **One-Folder**: Instant startup. Matches the architecture flawlessly. Allows advanced users to `pip install` additional libraries into the embedded Python if they want CodeAgent to test their specific frameworks.
- **Decision**: **ONE-FOLDER**.

## 12. Installation Architecture
```text
C:\Program Files\CodeAgent\ (Read-Only Application Files)
 ├── python_runtime\         # Portable Python
 ├── mis_agentes_inteligentes\ # Source code
 │    └── localcode_claude_ui.html
 ├── desktop_app.py          # Entrypoint
 └── CodeAgent.bat/.exe      # Launcher
```

## 13. Update Architecture
Because G1.2 successfully migrated all persistent state (SQLite DB, Sessions, Reports) to `%APPDATA%\CodeAgent`, updates are structurally safe. 
- **UPDATE**: Simply overwrites the `C:\Program Files\CodeAgent` directory. 
- **USER DATA**: Remains untouched in AppData.

## 14. Clean-Machine Simulation
A Windows machine without Git, without Ollama, and without the repository will:
1. Start `desktop_app.py` instantly.
2. Initialize SQLite in `%APPDATA%\CodeAgent\database`.
3. Launch the SSE backend.
4. Open the Webview.
5. Gracefully skip Git checks during verification.
6. Still connect to Cloud LLMs via bundled `litellm`.

## 15. Production/Development Matrix
| Component | Production | Development | Test | Optional |
| --------- | ---------- | ----------- | ---- | -------- |
| `pytest` | YES | YES | YES | NO |
| `sdd_check.py` | NO | YES | YES | NO |
| `Graphify` CLI | NO | NO | NO | YES |
| `LiteLLM` | YES | YES | YES | NO |
| `Git` CLI | NO | YES | YES | YES |
| `Desktop UI` | YES | YES | YES | NO |

## 16. Packaging Manifest Proposal
**Include:**
- `python_runtime/`
- `mis_agentes_inteligentes/` (excluding temp/test artifacts)
- `desktop_app.py`
- Mandatory pip packages.

**Explicitly Exclude:**
- `.git/`, `.github/`, `.agents/`, `tests/`, `scripts/`
- `*.db` (e.g. `codeagent_desktop.db`, `MisEventos.db`)
- `sesiones/`, `tmp*/`, `historial_analisis.txt`, `metrics_benchmarks.json`
- `.env`

## 17. Security Audit
Verified that excluding the above artifacts guarantees no Developer API Keys, Personal Checkpoints, or Test Databases will be shipped to end-users.

## 18. Size Estimate
- Portable Python + Standard Lib: ~40MB
- Site-Packages (litellm, smolagents, fastapi, webview): ~60MB
- Application Source: ~1MB
- **Total Footprint**: ~100MB (Uncompressed)

## 19. Architectural Impact
- **agent_pipeline.py**: UNCHANGED.
- **sdd_contract**: UNCHANGED.
- **SQLite**: CANONICAL AUTHORITY PRESERVED.
- **Desktop UI**: CANONICAL PATH PRESERVED.
- **%APPDATA%**: USER DATA BOUNDARY CONFIRMED.

## 20. Risks
- **Extensibility**: Because CodeAgent uses its embedded Python to test the user's workspace, running tests that depend on third-party libraries (e.g. `django`) will fail unless the user installs them into CodeAgent's runtime. This is an existing architectural trait of the IDE, not a packaging flaw.

## 21. Rollback
No code was changed. Safe to discard this report if needed.

## 22. Implementation Gate
| Question                           | Result |
| ---------------------------------- | ------ |
| Entry point proven?                | YES    |
| Runtime dependencies proven?       | YES    |
| Optional dependencies classified?  | YES    |
| Git requirement proven?            | YES    |
| Resource closure proven?           | YES    |
| Application/data boundary proven?  | YES    |
| One-file vs one-folder decided?    | YES    |
| Packaging strategy justified?      | YES    |
| Clean-machine behavior understood? | YES    |
| Security boundary verified?        | YES    |

**DECISION: B — CONTROLLED PACKAGING IMPLEMENTATION JUSTIFIED**

## 23. Final Decision
A One-Folder distribution using a Portable Embedded Python runtime is structurally validated. The entrypoint, dependency matrix, and resource closure have been exactly mapped without violating orchestration authorities.

## 24. Recommended Next Phase
**G1.4: PACKAGING IMPLEMENTATION**
Create the definitive build script (`build_package.py` or `.ps1`) that automatically downloads Portable Python, installs the exact pip manifest, copies the filtered repository files, and zips the distribution.

## 25. What was NOT changed
- Zero source code changes.
- No refactoring.
- No new Manager/Service abstractions.
- No test suite modifications.
