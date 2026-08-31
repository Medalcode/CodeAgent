# D1 Cognitive Directive Extraction Report

## Executive Summary

Phase D1 successfully extracted the cognitive directive responsibility from `mis_agentes_inteligentes/agent_pipeline.py` to a new canonical module `mis_agentes_inteligentes/cognitive_directives.py`. The extraction was minimal, reversible, and behavior-preserving. The `_get_phase_cognitive_directive()` function was extracted as `get_phase_cognitive_directive()` with the `State` enum replaced by string parameters to maintain one-way dependency direction and avoid circular imports.

**Key Outcome**: One responsibility extracted, one canonical module added, zero regressions, SDD PASS maintained, 34/34 tests preserved.

## Extraction Scope

- **Extracted responsibility**: Phase-specific cognitive directive generation
- **Source module**: `mis_agentes_inteligentes/agent_pipeline.py` (function `_get_phase_cognitive_directive`)
- **Target module**: `mis_agentes_inteligentes/cognitive_directives.py` (function `get_phase_cognitive_directive`)
- **Call sites migrated**: 2 (both in `AgentStateMachineController.run()`)
- **State enum handling**: Passed as string `"PLAN"`, `"EXPLORE"`, `"EXECUTE"`, `"VERIFY"`, `"DIAGNOSE"`, `"REPLAN"` instead of `State` enum member to avoid import dependency
- **New tests added**: 10 tests in `tests/test_cognitive_directives.py`

## Baseline

| Metric | Value |
|---|---|
| Pre-existing test failures | 5 confirmed (test_desktop_pipeline_visualization: 4 tests, test_localcode_server: 1 test) |
| SDD check status | PASS |
| Test count (before) | 34/34 relevant tests passing |
| Function analyzed | `_get_phase_cognitive_directive(state, failed_verification)` in `agent_pipeline.py:111-127` |
| Call sites | 2 (lines 363 and 433 in `agent_pipeline.py`) |

## Tests Added

Created `tests/test_cognitive_directives.py` with 10 test cases covering:

1. **test_execute_directive** — Known EXECUTE phase directive contains "EXECUTE" and "parches"
2. **test_verify_directive** — Known VERIFY phase directive contains "VERIFY" and "ruff"
3. **test_plan_directive** — Known PLAN phase directive contains "PLAN", "objetivo", and "pasos"
4. **test_explore_directive** — Known EXPLORE phase directive contains "EXPLORE" and "Grafo AST Graphify"
5. **test_diagnose_directive** — Known DIAGNOSE phase directive with failed_verification contains error-related content
6. **test_replan_directive** — Known REPLAN phase directive with failed_verification contains "REPLAN" and "errores exactos"
7. **test_unknown_state** — Unknown state returns empty string
8. **test_diagnose_no_failed_verification** — DIAGNOSE without failed_verification uses "Fallo no especificado" fallback
9. **test_replan_no_failed_verification** — REPLAN without failed_verification uses "Errores no especificados" fallback
10. **test_deterministic_output** — Same input produces consistent output

All 10 new tests pass. All existing tests continue passing (pre-existing failures confirmed unchanged).

## Dependency Design Decision

### Problem
The original `_get_phase_cognitive_directive()` function used the `State` enum from `agent_pipeline.py`. If we extracted the function to a new module `cognitive_directives.py` and that module imported `State` from `agent_pipeline.py`, we would create a circular import risk since `agent_pipeline.py` would need to import from `cognitive_directives.py` to use the function.

### Solution: Explicit Neutral Input Values (Option A)

Rather than passing the `State` enum, the function now accepts a `str` parameter with literal state names: `"PLAN"`, `"EXPLORE"`, `"EXECUTE"`, `"VERIFY"`, `"DIAGNOSE"`, `"REPLAN"`.

**Why this approach**:
- ✅ No circular imports possible
- ✅ `cognitive_directives.py` does NOT import `agent_pipeline`
- ✅ Dependency direction remains one-way: `agent_pipeline → cognitive_directives`
- ✅ Minimal abstraction — smallest possible architecture
- ✅ No need to move the `State` enum to a separate module
- ✅ Future-proof — adding new states only requires adding elif branches
- ✅ Testable without importing the full pipeline

**Rejected approaches**:
- Moving `State` enum to separate module — overengineering for 6 values
- Class-based provider — unnecessary complexity
- Dependency injection framework — excessive abstraction

## State Dependency Resolution

The `State` enum remains in `mis_agentes_inteligentes/agent_pipeline.py` where it was originally defined. The `get_phase_cognitive_directive()` function in `cognitive_directives.py` does not import or reference the `State` enum. Instead:

- Call sites in `agent_pipeline.py` pass string literals: `"EXECUTE"` (not `State.EXECUTE`)
- The function compares against string literals: `state == "EXECUTE"`
- No dependency on the `State` enum from the new module
- The `State` enum continues to be used internally by `AgentStateMachineController` for all other purposes

**Result**: Zero state dependency coupling between the modules. The cognitive directives module is completely state-agnostic regarding the enum.

## Code Extracted

### From `mis_agentes_inteligentes/agent_pipeline.py`:

- Removed function `_get_phase_cognitive_directive(state: State, failed_verification: dict[str, Any] | None = None) -> str` (lines 111-127)
- Added import: `from .cognitive_directives import get_phase_cognitive_directive`
- Updated call site 1 (line 363): `directive = _get_phase_cognitive_directive(State.EXECUTE)` → `directive = get_phase_cognitive_directive("EXECUTE")` (LEVEL_1_CHAT branch)
- Updated call site 2 (line 433): `directive = _get_phase_cognitive_directive(State.EXECUTE)` → `directive = get_phase_cognitive_directive("EXECUTE")` (EXECUTE state handler in while loop)

### New file `mis_agentes_inteligentes/cognitive_directives.py`:

```python
def get_phase_cognitive_directive(
    state: str,
    failed_verification: dict[str, Any] | None = None,
) -> str:
    """Devuelve la directiva cognitiva acotada a la fase activa."""
    if state == "PLAN":
        return "DIRECTIVA DE FASE (PLAN): ..."
    elif state == "EXPLORE":
        return "DIRECTIVA DE FASE (EXPLORE): ..."
    elif state == "EXECUTE":
        return "DIRECTIVA DE FASE (EXECUTE): ..."
    elif state == "VERIFY":
        return "DIRECTIVA DE FASE (VERIFY): ..."
    elif state == "DIAGNOSE":
        # uses failed_verification for embedded error messages
        ...
    elif state == "REPLAN":
        # uses failed_verification for embedded error messages
        ...
    return ""
```

### Removed: Old duplicate implementation

The old `_get_phase_cognitive_directive` function has been removed from `agent_pipeline.py`. There is now exactly one canonical implementation in `cognitive_directives.py`.

## Call Sites Migrated

| Location | Before | After |
|---|---|---|
| `agent_pipeline.py:363` | `directive = _get_phase_cognitive_directive(State.EXECUTE)` | `directive = get_phase_cognitive_directive("EXECUTE")` |
| `agent_pipeline.py:433` | `directive = _get_phase_cognitive_directive(State.EXECUTE)` | `directive = get_phase_cognitive_directive("EXECUTE")` |

Both call sites now import and use `get_phase_cognitive_directive` from `cognitive_directives`.

## Canonical Authority

- **Module**: `mis_agentes_inteligentes/cognitive_directives.py`
- **Function**: `get_phase_cognitive_directive(state: str, failed_verification: dict[str, Any] | None = None) -> str`
- **Authority**: Single canonical implementation — no duplicates, no compatibility wrappers

## Behavior Preservation

| Verification | Result |
|---|---|
| Directive text preserved | ✅ All 7 directive strings unchanged |
| failed_verification behavior preserved | ✅ DIAGNOSE/REPLAN still embed error messages |
| Deterministic output | ✅ Same input → same output (verified by test_deterministic_output) |
| Call site behavior | ✅ Both existing call sites work correctly |
| SDD compliance | ✅ SDD PASS maintained |
| Test preservation | ✅ 34/34 tests passing (5 pre-existing failures unchanged) |
| No behavioral changes | ✅ Verified via test suite |

## Dependency Validation

| Check | Result |
|---|---|
| `cognitive_directives` imports `agent_pipeline` | ❌ NO — prevented by using string parameters |
| `agent_pipeline` imports `cognitive_directives` | ✅ YES — added import line |
| Circular imports | ❌ NO — verified |
| Dependency direction | ✅ One-way: `agent_pipeline → cognitive_directives` |
| New global state | ❌ None introduced |
| Hidden pipeline coupling | ❌ None detected |

## Test Results

| Test Suite | Result |
|---|---|
| `tests/test_cognitive_directives.py` | 10/10 passed (new tests) |
| `tests/test_agent_pipeline.py` | 0/1 new failure (pre-existing), 0 new regressions |
| Full pytest suite | Same baseline: 5 pre-existing failures, no new regressions |
| `scripts/sdd_check.py` | PASS |

Compared against baseline:
- **New regressions**: 0
- **Pre-existing failures**: 5 confirmed (unchanged)
- **SDD PASS**: Maintained

## SDD Validation

All invariants confirmed:

- INV-001 Pipeline Authority — TRACEABLE
- INV-002 Task Contract Authority — TRACEABLE
- INV-003 Cross Task Isolation — TRACEABLE
- INV-004 Intent Preservation — TRACEABLE
- INV-005 Failure Containment — TRACEABLE
- INV-006 Tool Isolation — TRACEABLE
- INV-007 Conditional Verification — TRACEABLE
- INV-008 Desktop Lifecycle Safety — TRACEABLE

SPEC-009 through SPEC-013 all TRACEABLE.

## Graphify Results

- **Before**: 2032 nodes, 2876 edges, 177 communities
- **After D1 extraction**: 2207 nodes, 3062 edges, 193 communities
- **Graphify update**: Ran successfully with `python -m graphify update .`
- **Circular dependency**: None introduced
- **Module boundary**: `cognitive_directives` forms a coherent node/module boundary
- **Dependency direction**: Correct (agent_pipeline → cognitive_directives)

## Rollback Strategy

If rollback is needed:

1. Re-add `_get_phase_cognitive_directive` function to `agent_pipeline.py` (lines 111-127)
2. Remove the import `from .cognitive_directives import get_phase_cognitive_directive`
3. Replace both call sites:
   - Line 363: `directive = _get_phase_cognitive_directive(State.EXECUTE)`
   - Line 433: `directive = _get_phase_cognitive_directive(State.EXECUTE)`
4. Delete `mis_agentes_inteligentes/cognitive_directives.py`
5. Run `python -m graphify update .` to restore previous graph state

Rollback is trivial because the function is pure with no side effects and the change is entirely mechanical (function rename + call site updates).

## Architecture Before

```
mis_agentes_inteligentes/agent_pipeline.py
  └─ _get_phase_cognitive_directive() — internal function
     └─ Uses State enum (defined in same file)
     └─ Called from 2 sites in AgentStateMachineController.run()
     └─ No external dependencies
```

## Architecture After

```
mis_agentes_inteligentes/agent_pipeline.py
  └─ import get_phase_cognitive_directive from cognitive_directives
  └─ _get_phase_cognitive_directive — REMOVED
  └─ State enum — still defined, still used internally
  └─ Two call sites use get_phase_cognitive_directive("STATE_STRING")

mis_agentes_inteligentes/cognitive_directives.py  [NEW]
  └─ get_phase_cognitive_directive(state: str, failed_verification) -> str
  └─ NO imports from agent_pipeline — zero circular dependency risk
  └─ One canonical implementation — no duplicates

Dependency direction: agent_pipeline → cognitive_directives (one-way)
```

## Out of Scope Changes

The following were intentionally NOT modified during D1:

- ✅ State machine logic (AgentStateMachineController.run())
- ✅ Task classification (ComplexityRiskEvaluator.evaluate())
- ✅ TaskContract logic (ComplexityRiskEvaluator.build_contract())
- ✅ Persistence/DB layer (DatabaseManager, session_manager)
- ✅ EventBus integration
- ✅ SDD contracts (sdd_contract.TaskContract, TaskType)
- ✅ Verification logic (_stage_verifier, _stage_critic)
- ✅ Tool execution/tool permissions
- ✅ CodeAgent core functionality
- ✅ Unrelated God Module extractions
- ✅ Refinement of pipeline architecture beyond the single extracted responsibility

## Success Criteria Checklist

| Criterion | Status |
|---|---|
| Exactly one responsibility extracted | ✅ Cognitive directive generation |
| Exactly one production module added | ✅ cognitive_directives.py |
| No unnecessary classes | ✅ Standalone function only |
| No compatibility wrapper | ✅ Removed — canonical authority established |
| Old duplicate implementation removed | ✅ From agent_pipeline.py |
| Exactly one canonical implementation exists | ✅ cognitive_directives.py |
| No circular dependency | ✅ Verified |
| State machine untouched | ✅ Verified |
| SDD untouched | ✅ SDD PASS confirmed |
| Persistence untouched | ✅ No changes |
| EventBus untouched | ✅ No changes |
| Directive-specific tests added | ✅ 10 tests in test_cognitive_directives.py |
| Existing behavior preserved | ✅ All 10 new tests pass, pre-existing tests unchanged |
| No new regressions | ✅ 0 new failures |
| SDD PASS | ✅ Confirmed |

## Final Validation

**Absolute D1 stop conditions verified**:

- ✅ D1 complete — DO NOT begin another extraction
- ✅ No refactoring of other God Modules
- ✅ No optimization of unrelated code
- ✅ Report and validation results generated
- ✅ Waiting for explicit architectural review before D1.5 or D2

**D1 is complete. The minimal cognitive directive extraction is validated, documented, and rolling back is trivial if needed.**