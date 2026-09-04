# CODEAGENT — G2.4.2 / VERIFICATION WORKSPACE & TEST DISCOVERY AUDIT

## 1. Objective
Investigate with strict evidence why a request to build a simple calculator in the external `Medalcode/Pruebas` workspace produced a `VERIFICATION_FAILED` status, detecting ~100 Python files (AST FAIL) and 0 test files (NOT_REQUIRED), despite `calculadora.py` and `test_calculadora.py` being properly created in the workspace.

## 2. Reproduction
The anomaly is fully reproducible conceptually and statically through the codebase execution trace.

## 3. Evidence
- Executor (smolagents) correctly wrote files to `Pruebas`.
- Verification (AgentPipeline) scanned 101 Python files.
- AST failed on `accidental_complexity.py` (a scratch file present in the CodeAgent root).
- `ComplexityRiskEvaluator.build_contract()` evaluates the task as an `ACTION` which legitimately bypasses tests.

## 4. Execution Trace
1. **User Prompt** -> `localcode_server.py` (`handle_agent_chat()`)
2. `localcode_server.py` calls `set_active_workspace(ACTIVE_WORKSPACE_DIR)` (Pruebas).
3. `localcode_server.py` calls `main.py` -> `ejecutar_agentes()`.
4. `main.py` instantiates `pipeline = AgentPipeline()` WITHOUT passing a `workspace_dir`.
5. `AgentStateMachineController.__init__` falls back to `self.workspace_dir = workspace_dir or os.getcwd()`.
6. `os.getcwd()` is the CodeAgent repository root.
7. `AgentPipeline._stage_verifier()` executes against the CodeAgent root.

## 5. Workspace Propagation
- **Requested Workspace**: `Pruebas`
- **Stored In**: `mis_agentes_inteligentes.tools.ACTIVE_WORKSPACE_DIR` via `set_active_workspace()`.
- **Transmitted to Executor**: Yes, executor tools implicitly call `get_active_workspace()`.
- **Transmitted to Verification**: NO. `main.py` fails to read the active workspace or receive it as a parameter, defaulting to `os.getcwd()`.

## 6. Verification Root
Verification Engine uses `self.workspace_dir` defined in `AgentStateMachineController`. Since no explicit path is passed by `main.py`, it resolves to `os.getcwd()` (CodeAgent root).

## 7. Test Discovery
- The test discovery mechanism (`_is_test_file`) was completely bypassed. 
- Reason: `tests_status = "NOT_REQUIRED"`.
- This occurred because `ComplexityRiskEvaluator.build_contract()` classified the prompt as `TaskType.ACTION`, for which `requires_tests` defaults to `False`. 

## 8. AST Discovery
- **Root Directory**: `CodeAgent/`
- **Glob**: `endswith('.py')`
- **Count**: 101 Python files found in CodeAgent.
- **Error**: The very first syntax check that failed was on `accidental_complexity.py` (line 61 unterminated string literal), causing `AST Syntax: FAIL`.

## 9. Task Classification
The prompt "puedes crear en esta carpeta una calculadora simple con las 4 operaciones basicas ?" legitimately classifies as an `ACTION` task. In `CodeAgent`, `ACTION` tasks do not strictly require test suites, hence `NOT_REQUIRED`.

## 10. Root Cause
**A — Workspace propagation bug**
The executor correctly accesses the intended workspace via `get_active_workspace()`, but the verification engine (`AgentPipeline`) is incorrectly instantiated in `main.py` without the `workspace_dir` argument, causing it to fallback to `os.getcwd()` (the CodeAgent repository root).

## 11. Architectural Boundary
The decoupling occurs between `localcode_server.py` (which knows the active workspace) and `main.py` (`ejecutar_agentes`). 
The interface `ejecutar_agentes()` does not currently accept a `workspace_dir` argument, causing `main.py` to instantiate `AgentPipeline` blindly. 

## 12. Risk Assessment
This bug completely breaks the Verification Engine for any workspace other than CodeAgent itself. All AST and Test verification attempts will run against CodeAgent, causing deterministic verification failures on valid external code.

## 13. Recommended Minimal Fix
In `mis_agentes_inteligentes/main.py`, inside `ejecutar_agentes()`:
Retrieve the active workspace before instantiating the pipeline:
```python
from mis_agentes_inteligentes.tools import get_active_workspace
ws_dir = get_active_workspace() or os.getcwd()
pipeline = AgentPipeline(workspace_dir=ws_dir)
```
This is the minimal change that correctly synchronizes the Verification workspace with the Executor workspace without altering public interfaces or contracts.

## 14. No Changes
- NO CODE CHANGES
- NO REFACTORING
- NO TEST CHANGES
- NO SDD CHANGES
- NO TASK CONTRACT CHANGES
- NO UI CHANGES
- NO CHANGES TO Pruebas

## 15. Validation
- Statically traced `AgentPipeline()` initialization in `main.py`.
- Ran AST python parser natively on the CodeAgent root which perfectly reproduced the exact `101 Python files` and `accidental_complexity.py` syntax failure.
- Ran `ComplexityRiskEvaluator.build_contract()` natively which confirmed `requires_tests: False` and `TaskType: ACTION`.

## 16. Conclusion
The observed anomaly is the result of a single missing constructor argument in `main.py`, compounded by a legitimate task classification bypassing the test discovery logic.
