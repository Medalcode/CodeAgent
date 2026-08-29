# Conformance Audit: SDD Contract System

## Executive Summary

**Status:** ?? PENDING

**Date:** 2026-08-28

**Scope:** Verification that existing CodeAgent code complies with `.kiro/specs/codeagent-sdd-contract/requirements.md`

**Finding:** Current implementation has **TWO parallel architectures** coexisting:
1. NEW SDD Contract System (`sdd_contract/`)
2. LEGACY CodeAgent (`agent_pipeline.py`)

This creates risk of inconsistent behavior where different components make contradictory decisions.

---

## Audit Results by Requirement

### Requirement 1: Task Classification

| Status | Details |
|--------|---------|
| **NOT_IMPLEMENTED** | New `sdd_contract.task_router.TaskRouter` exists but NOT integrated with `agent_pipeline.py`. Legacy `ComplexityRiskEvaluator` still used in `AgentStateMachineController.infer_execution_level()`. |

**Files:**
- `sdd_contract/task_router.py` - New implementation (? written)
- `mis_agentes_inteligentes/agent_pipeline.py` - Still uses `ComplexityRiskEvaluator.evaluate()` (? not migrated)

**Evidence:**
```python
# agent_pipeline.py (line ~200)
def infer_execution_level(self, user_goal: str) -> ExecutionLevel:
    """Determina el Nivel de Ejecución óptimo usando la evaluación de complejidad y riesgo."""
    return ComplexityRiskEvaluator.evaluate(user_goal)  # ? NOT using TaskRouter
```

---

### Requirement 2: CHAT Task Contract

| Status | Details |
|--------|---------|
| **PARTIALLY_IMPLEMENTED** | `sdd_contract.task_contract.ChatTaskContract` implemented correctly. BUT `agent_pipeline.py` still has `LEVEL_1_CHAT` path with direct agent execution bypassing verification. |

**Files:**
- `sdd_contract/task_contract.py` (? written)
- `mis_agentes_inteligentes/agent_pipeline.py` (? NOT migrated)

**Issue:** `agent_pipeline.py` line ~300 has "ultra-fast shortcut" for LEVEL_1_CHAT that:
- Does NOT call verification
- Does NOT use `ChatTaskContract`
- Bypasses `TaskRouter` classification

---

### Requirement 3: ACTION Task Contract

| Status | Details |
|--------|---------|
| **NOT_IMPLEMENTED** | No integration with new `ActionTaskContract`. Legacy code uses `ComplexityRiskEvaluator.build_contract()` which returns old `TaskContract` dataclass. |

**Files:**
- `sdd_contract/task_contract.py` (? written)
- `mis_agentes_inteligentes/agent_pipeline.py` (? NOT migrated)

**Evidence:**
```python
# agent_pipeline.py (line ~150)
@staticmethod
def build_contract(user_goal: str) -> TaskContract:
    level = ComplexityRiskEvaluator.evaluate(user_goal)
    if level == ExecutionLevel.LEVEL_2_ACTION:
        return TaskContract(
            task_type=TaskType.ACTION,
            execution_level=level,
            requires_code_verification=True,  # ? Old contract
            requires_tests=False,
            requires_execution=True,
            tools_allowed=True,
            files_allowed=True
        )
```

---

### Requirement 4: FEATURE Task Contract

| Status | Details |
|--------|---------|
| **NOT_IMPLEMENTED** | No integration with new `FeatureTaskContract`. Legacy `LEVEL_3_FEATURE` and `LEVEL_4_FULL` use old contract system. |

**Files:**
- `sdd_contract/task_contract.py` (? written)
- `mis_agentes_inteligentes/agent_pipeline.py` (? NOT migrated)

---

### Requirement 5: RECOVERY Task Contract

| Status | Details |
|--------|---------|
| **NOT_IMPLEMENTED** | New `sdd_contract.task_contract.RecoveryTaskContract` exists but NO integration. Legacy code has NO `RECOVERY` task type. |

**Files:**
- `sdd_contract/task_contract.py` (? written)
- `mis_agentes_inteligentes/agent_pipeline.py` (? NOT migrated)

**Evidence:** `ExecutionLevel` enum in `agent_pipeline.py` only has:
- `LEVEL_1_CHAT`
- `LEVEL_2_ACTION`
- `LEVEL_3_FEATURE`
- `LEVEL_4_FULL`

No `RECOVERY` level exists.

---

### Requirement 6: Verification States

| Status | Details |
|--------|---------|
| **PARTIALLY_IMPLEMENTED** | New `VerificationState` enum (PASS/NOT_REQUIRED/FAIL/ERROR) exists. BUT legacy `_stage_verifier()` returns dictionary with different status keys. |

**Files:**
- `sdd_contract/verification_engine.py` (? written)
- `mis_agentes_inteligentes/agent_pipeline.py` (? NOT migrated)

**Evidence:**
```python
# agent_pipeline.py (line ~500)
def _stage_verifier(self, user_goal: str = "") -> dict[str, Any]:
    # Returns dictionary with keys:
    # - "success" (bool)
    # - "ast_status" (str: "PASS"/"FAIL"/"NOT_RUN")
    # - "tests_status" (str: "PASS"/"FAIL"/"NOT_REQUIRED")
    # - "program_passed" (bool)
    # NOT using VerificationState enum!
```

**Risk:** Two separate verification systems could produce conflicting results:
- Legacy: `verification["success"]` based on internal logic
- New: `VerificationResult.success` based on `VerificationEngine.compute_success()`

---

### Requirement 7: Verification Evidence

| Status | Details |
|--------|---------|
| **PARTIALLY_IMPLEMENTED** | New `EvidenceLogger` exists. BUT `_stage_verifier()` still collects `ast_errors` in dictionary instead of logging through `EvidenceLogger`. |

**Files:**
- `sdd_contract/evidence_logger.py` (? written)
- `mis_agentes_inteligentes/agent_pipeline.py` (? NOT migrated)

**Evidence:**
```python
# agent_pipeline.py (line ~600)
ast_errors = []
# ... collect errors ...
return {
    "success": success,
    "ast_errors": ast_errors,  # ? NOT logged to EvidenceLogger
    # ...
}
```

**Missing:** Call `evidence_logger.log_verification_fail()` when verification fails.

---

### Requirement 8: Tool Policy by Task Type

| Status | Details |
|--------|---------|
| **NOT_IMPLEMENTED** | New `ToolPolicyEnforcer` exists. BUT `agent_pipeline.py` has NO tool policy enforcement. Tools are granted based on old `TaskContract.tools_allowed` boolean. |

**Files:**
- `sdd_contract/tool_policy.py` (? written)
- `mis_agentes_inteligentes/agent_pipeline.py` (? NOT migrated)

**Evidence:** No integration of `ToolPolicyEnforcer.is_tool_allowed()` anywhere in `agent_pipeline.py`.

---

### Requirement 9: Replanning Constraints

| Status | Details |
|--------|---------|
| **PARTIALLY_IMPLEMENTED** | New `Replanner` exists. Legacy `_stage_replan()` still used without evidence requirement. |

**Files:**
- `sdd_contract/replanner.py` (? written)
- `mis_agentes_inteligentes/agent_pipeline.py` (? NOT migrated)

**Issue:** Legacy code replans based on `replans_count < self.max_replans` WITHOUT requiring `diagnostic_report` with evidence first.

---

### Requirement 10: UI Lifecycle Policy

| Status | Details |
|--------|---------|
| **NOT_IMPLEMENTED** | New `UIManager` exists. BUT `agent_pipeline.py` has NO UI lifecycle management. |

**Files:**
- `sdd_contract/ui_manager.py` (? written)
- `mis_agentes_inteligentes/agent_pipeline.py` (? NOT migrated)

**Evidence:** No reference to `UIManager` anywhere in `agent_pipeline.py`. The `desktop_app.py` UI creation logic is NOT controlled by SDD contract.

---

### Requirement 11: Evidence Requirement for Diagnosis

| Status | Details |
|--------|---------|
| **NOT_IMPLEMENTED** | New `EvidenceLogger.log_diagnosis()` exists. Legacy `_stage_diagnose()` returns dictionary without logging evidence. |

**Files:**
- `sdd_contract/evidence_logger.py` (? written)
- `mis_agentes_inteligentes/agent_pipeline.py` (? NOT migrated)

**Evidence:**
```python
# agent_pipeline.py (line ~400)
def _stage_diagnose(self, verification_res: dict, _user_goal: str) -> dict:
    return {
        "root_cause": err_str,
        "strategy_change": "...",
        # ? No evidence logged to EvidenceLogger
    }
```

---

### Requirement 12: Bounded Execution

| Status | Details |
|--------|---------|
| **PARTIALLY_IMPLEMENTED** | Legacy `max_replans` exists. New `TaskContract.get_max_iterations()` exists. BUT not integrated. |

**Files:**
- `sdd_contract/task_model.py` (? written)
- `mis_agentes_inteligentes/agent_pipeline.py` (? NOT migrated)

**Evidence:** Legacy code uses `self.max_replans` in `AgentStateMachineController.__init__()`. New `Task.max_iterations` is not used.

---

## Parallel Architecture Risk

### The Problem

Two verification systems could produce contradictory results:

```
+-------------------------------------------------------------+
¦                    OLD AGENT_PIPELINE                        ¦
¦                                                              ¦
¦  _stage_verifier()                                          ¦
¦    +- AST check (internal logic)                           ¦
¦    +- Ruff check (internal logic)                          ¦
¦    +- Tests check (internal logic)                         ¦
¦    +- Program execution (internal logic)                   ¦
¦    +- success = len(blocking_checks) == 0                  ¦
¦          ?                                                  ¦
¦    Returns: {"success": bool}                              ¦
+-------------------------------------------------------------+
                           +
+-------------------------------------------------------------+
¦                    NEW SDD CONTRACT                          ¦
¦                                                              ¦
¦  VerificationEngine.verify()                                ¦
¦    +- Evaluate each criterion                              ¦
¦    +- Assign PASS/FAIL/ERROR/NOT_REQUIRED                  ¦
¦    +- success = all required == PASS                       ¦
¦          ?                                                  ¦
¦    Returns: VerificationResult.success (bool)              ¦
+-------------------------------------------------------------+
```

**Risk:** Same task could be:
- `success=True` in legacy system
- `success=False` in new system

Resulting in:
- "Verification PASSED!" in UI
- But "VERIFICATION_FAILED" in metrics

### Same Risk with Other Components

1. **Task Classification:**
   - `ComplexityRiskEvaluator.evaluate()` vs `TaskRouter.classify()`
   - Could return different task types

2. **Replanning:**
   - Legacy: `replans_count < max_replans`
   - New: `should_replan() with evidence requirement`
   - Could allow replanning in different conditions

3. **UI Management:**
   - Legacy: No UI manager (desktop_app.py creates windows freely)
   - New: `UIManager` enforces single instance

---

## Recommendations

### IMMEDIATE (Blocker)

1. **Integrate TaskRouter** into `AgentStateMachineController`
   - Replace `ComplexityRiskEvaluator.evaluate()` with `TaskRouter.classify()`
   - Ensure one source of truth for task classification

2. **Integrate VerificationEngine** into `_stage_verifier()`
   - Replace internal verification logic with `VerificationEngine.verify()`
   - Ensure one source of truth for verification results

3. **Integrate ToolPolicyEnforcer** into tool execution
   - Call `enforce_tool_policy()` before any tool usage
   - Ensure tools are only used if allowed by task contract

### SHORT TERM (Critical)

4. **Add RECOVERY task type**
   - Extend `ExecutionLevel` or create new enum
   - Implement `RecoveryTaskContract` integration

5. **Integrate UI Manager**
   - Wrap UI creation in `UIManager.create_instance()`
   - Prevent multiple UI instances

6. **Migrate evidence logging**
   - Replace dictionary-based logging with `EvidenceLogger`
   - Ensure evidence exists for all failures

### MEDIUM TERM (High Priority)

7. **Create acceptance tests**
   - Test each requirement individually
   - Verify no parallel execution of old + new code

8. **Add migration documentation**
   - Document breaking changes
   - Provide upgrade path

---

## Conformance Matrix

| Requirement | Implemented | Tested | Notes |
|-------------|-------------|--------|-------|
| 1. Task Classification | ? | ? | New code exists, not integrated |
| 2. CHAT Contract | ?? | ? | New code exists, legacy path still used |
| 3. ACTION Contract | ? | ? | New code exists, not integrated |
| 4. FEATURE Contract | ? | ? | New code exists, not integrated |
| 5. RECOVERY Contract | ? | ? | New code exists, no integration |
| 6. Verification States | ?? | ? | New enum exists, not used |
| 7. Verification Evidence | ?? | ? | New logger exists, not used |
| 8. Tool Policy | ? | ? | New enforcer exists, not used |
| 9. Replanning | ?? | ? | New replanner exists, not integrated |
| 10. UI Lifecycle | ? | ? | New manager exists, not used |
| 11. Evidence for Diagnosis | ? | ? | New logger exists, not used |
| 12. Bounded Execution | ?? | ? | Max iterations exist, not integrated |

**Overall Score:** 2/12 requirements fully compliant (16.7%)

---

## Conclusion

The SDD Contract System has been **implemented as a parallel architecture** but NOT **integrated** into existing code. This creates significant risk of inconsistent behavior.

**Next step:** Do NOT add more features. First complete integration audit and migration.
