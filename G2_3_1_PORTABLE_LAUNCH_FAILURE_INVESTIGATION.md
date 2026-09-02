# CODEAGENT — G2.3.1: PORTABLE DESKTOP LAUNCH FAILURE INVESTIGATION

## 1. Objective
Investigate the root cause of the HTTP 404 error encountered when launching the portable CodeAgent Desktop package (`launch_codeagent.bat`), without modifying any code.

## 2. Observed Failure
When launching the portable desktop package, the PyWebView window opens but displays:
```
Error response
Error code: 404
Message: File not found
Error code explanation: 404 - Nothing matches the given URI
```

## 3. Reproduction
Running `dist\CodeAgent\launch_codeagent.bat` starts the embedded Python runtime, boots the local server on port 8000, and opens PyWebView. The server logs the startup but the GUI displays the 404 error. 

## 4. Exact Failing URI
`GET /localcode_claude_ui.html`
Which `desktop_app.py` constructs as: `http://localhost:<port>/localcode_claude_ui.html`

## 5. Evidence
- `desktop_app.py` defines `SERVER_URL = f"http://localhost:{port}/localcode_claude_ui.html"`.
- `localcode_server.py` explicitly intercepts `clean_path in ("/", "", "/ui", "/localcode_claude_ui.html")` and rewrites `self.path = "/localcode_claude_ui.html"`, passing it to `super().do_GET()`.
- `SimpleHTTPRequestHandler` joins the requested path with `self.directory` (`BASE_DIR`).
- `BASE_DIR` is correctly resolved as the repository/package root (`os.path.dirname(os.path.dirname(__file__))`).
- In the repository, two copies of the HTML file exist: one in `CodeAgent/` (root, outdated) and one in `mis_agentes_inteligentes/` (canonical, updated in G2.2).
- The packaging manifest (`manifest.json`) explicitly copies `mis_agentes_inteligentes/` but does NOT list the root HTML file in `app_files`.

## 6. Package Contents
Inside `dist\CodeAgent\`:
- `desktop_app.py` (exists in root)
- `launch_codeagent.bat` (exists in root)
- `mis_agentes_inteligentes\localcode_server.py` (exists)
- `mis_agentes_inteligentes\localcode_claude_ui.html` (exists)
- `localcode_claude_ui.html` (MISSING FROM ROOT)

## 7. Development vs Portable Comparison
**Development Environment**:
- `BASE_DIR` points to the repository root.
- `localcode_server.py` looks for `BASE_DIR/localcode_claude_ui.html`.
- The file exists in the repository root (as a stray/outdated copy).
- The GUI loads successfully, masking the fact that it is loading the *wrong* file (which lacks the G2.2 UX features).

**Portable Package**:
- `BASE_DIR` points to `dist\CodeAgent\`.
- `localcode_server.py` looks for `dist\CodeAgent\localcode_claude_ui.html`.
- The packaging script only copied the `mis_agentes_inteligentes` directory, omitting the stray root copy.
- The file does not exist in the package root.
- The server correctly throws a 404.

## 8. Routing Analysis
The routing logic in `localcode_server.py` hardcodes the path to the root directory by relying on `SimpleHTTPRequestHandler`'s default behavior, rather than mapping to the canonical file inside `mis_agentes_inteligentes/`.

## 9. Root Cause
```text
GUI requests /localcode_claude_ui.html
      ↓
desktop_app.py constructs http://localhost:<port>/localcode_claude_ui.html
      ↓
server receives GET /localcode_claude_ui.html
      ↓
route resolves to BASE_DIR/localcode_claude_ui.html
      ↓
BASE_DIR/localcode_claude_ui.html DOES NOT EXIST in portable package (manifest.json only copies mis_agentes_inteligentes/)
      ↓
HTTP 404
```

## 10. Classification
**RESOURCE PATH DEFECT**. 
The server route is resolving to a physical filesystem path that is not included in the portable package due to file duplication in the development repository.

## 11. Cancellation Separation
CANCELLATION:
Known separate P1 defect (stub function instead of REST call).
Not modified in G2.3.1.

## 12. Tests
Automated tests (Pytest/SDD) bypass the PyWebView GUI initialization and test the backend pipeline directly, explaining why the test suite passed 100% despite the GUI being fundamentally broken in the packaged build.
- Collected: 223
- Passed: 223
- Failed: 0
- Errors: 0

## 13. SDD
PASS

## 14. Changes
NONE

## 15. Non-Changes
- `localcode_claude_ui.html`
- `desktop_app.py`
- `localcode_server.py`
- `agent_pipeline.py`
- `cognitive_directives.py`
- `sdd_contract/`
- `DatabaseManager` / SQLite
- `graph_context.py`
- `EventBus`
- `packaging/manifest.json`

## 16. Risk
Until fixed, the portable distribution artifact is completely unusable by end users because the GUI cannot load. Furthermore, developers running from source are unknowingly loading an outdated HTML copy that lacks the G2.2 UX improvements.

## 17. Recommended Minimal Fix
1. Delete the outdated `localcode_claude_ui.html` from the repository root to prevent future shadowing.
2. In `localcode_server.py`, update the routing block to explicitly map the GUI route to the canonical location:
```python
        if clean_path in ("/", "", "/ui", "/app", "/index.html", "/chat", "/editor", "/localcode_claude_ui.html"):
            self.path = "/mis_agentes_inteligentes/localcode_claude_ui.html"
            super().do_GET()
```

## 18. Final Decision
**A — ROOT CAUSE CONFIRMED**
Clear root cause established; minimal fix identified.
