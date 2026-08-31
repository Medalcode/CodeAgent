# CODEAGENT — PHASE E1: ARCHITECTURAL HARDENING CANDIDATE AUDIT

## 1. Objective
Perform an evidence-based architectural hardening assessment on the E0.8 high-confidence baseline. The goal is strictly to evaluate whether any structural extraction or refactoring is fundamentally justified by clear architectural principles, boundaries, and dependencies—not to arbitrarily create refactoring work.

## 2. Scope
- Analysis of `agent_pipeline.py` and its state-machine dependencies.
- Evaluation of `sdd_contract/` integration.
- Assessment of runtime complexity (essential vs. accidental).
- Dependency direction analysis (specifically avoiding reverse dependencies from `cognitive_directives.py`).

## 3. E0.8 Baseline
Confirmed prior to audit:
- 223 collected, 223 passed, 0 failures.
- Reproducibility VERIFIED.
- SDD PASS.
- No circular dependencies detected.
- Canonical authorities (SQLite, PyWebView UI, graph_context) intact.

## 4. Architectural Inventory
| Module | Primary Responsibility | Consumers | Dependencies | State Ownership | Risk Level |
|--------|------------------------|-----------|--------------|-----------------|------------|
| `agent_pipeline.py` | Core state machine and lifecycle orchestration | `desktop_app.py`, CLI | `sdd_contract`, DB, tools | YES (Agent State) | PROTECTED |
| `sdd_contract/` | Task models, types, and architectural invariants | `agent_pipeline.py`, Tests | None | NO | PROTECTED |
| `cognitive_directives.py` | LLM directive generation per phase | `agent_pipeline.py` | None | NO | PROTECTED |
| `storage/database.py` | SQLite Persistence Source of Truth | `agent_pipeline.py` | None | YES (Storage) | PROTECTED |
| `session_manager.py` | JSON legacy export/compatibility | `agent_pipeline.py` | None | YES (Legacy) | LOW |

## 5. Candidate Discovery
### Candidate 1: `_stage_verifier` Execution Logic (AST/Ruff/Pytest)
| Candidate | Independent Responsibility | Boundary Clear | Coupling | State Risk | Benefit | Risk |
|-----------|---------------------------|----------------|----------|------------|---------|------|
| Verifier Subprocess Logic | Partial (Test running) | NO (Tightly coupled to pipeline dicts) | High (Reads pipeline state) | NO | Minor loc reduction | HIGH |

### Candidate 2: `ComplexityRiskEvaluator`
| Candidate | Independent Responsibility | Boundary Clear | Coupling | State Risk | Benefit | Risk |
|-----------|---------------------------|----------------|----------|------------|---------|------|
| Risk Evaluator | NO (Wraps TaskRouter) | YES | Low | NO | None (Already delegates) | CONTROLLED |

## 6. Responsibility Analysis
`agent_pipeline.py` is large (~1033 lines), but its responsibilities are highly cohesive: managing the transitions between `PLANNER`, `EXECUTE`, `VERIFIER`, `CRITIC`, and `REPLAN`. Extracting these methods to separate files would fragment the state machine authority and spread the lifecycle coordination across multiple files, violating the "ONE RESPONSIBILITY → ONE CANONICAL IMPLEMENTATION" rule.

## 7. Boundary Analysis
The boundaries between the pipeline (orchestration), `sdd_contract` (definitions), and `cognitive_directives` (prompts) are clean. The pipeline orchestrates, relying on definitions from the contract, and injecting prompts from the directives. Moving logic out of the pipeline would require passing a massive context dictionary (workspace, goal, task type, levels, diffs) to external modules, creating artificial high-coupling interfaces.

## 8. Duplication Audit
- **Persistence**: `AgentStateMachineController._save_checkpoint` writes to SQLite (Primary) and JSON (Secondary). This was explicitly classified in Phase C3.1 as an intentional legacy compatibility layer, NOT an architectural drift.
- **Task Classification**: `ComplexityRiskEvaluator.classify_with_router` delegates directly to `TaskRouter.classify()`. It acts as an adapter, not a duplicate implementation.

## 9. Dependency Direction Audit
| Dependency | Direction Correct? | Architectural Concern | Evidence |
|------------|-------------------|-----------------------|----------|
| `agent_pipeline` → `cognitive_directives` | YES | None | Verified via imports |
| `agent_pipeline` → `sdd_contract` | YES | None | Verified via imports |
| `sdd_contract` → `agent_pipeline` | NO IMPORTS | None | No reverse dependency found |

## 10. Complexity Triage
**Essential Complexity:**
- State transitions, checkpointing, prompt assembly, loop management (replans).
**Accidental Complexity:**
- Subprocess calls for `pytest`, `ruff`, and `git` inside the pipeline.
**Decision:** Extracting subprocess calls into `tools.py` would save space, but it does not represent a structural architectural shift. It is a minor refactoring that does not warrant a dedicated phase.

## 11. Extraction Gate Evaluation
No candidate passes the extraction gate. Extracting the pipeline steps would violate essential state-machine coherence. Extracting the subprocess calls provides no architectural benefit, only cosmetic line-count reduction.

## 12. Candidate Prioritization
No candidates classified as A (HIGH VALUE / LOW RISK) or B. All evaluated elements are either C (LOW VALUE) or D (PROTECTED).

## 13. Rejected Candidates
- `_stage_verifier` subprocess logic (Rejected: Fragmented pipeline coherence, low architectural value).
- `ComplexityRiskEvaluator` (Rejected: Already delegates properly, extraction adds boilerplate).

## 14. Protected Components
- `agent_pipeline.py` (State Machine)
- `sdd_contract/` (Task Contracts)
- `storage/database.py` (Source of Truth)
- `desktop_app.py` (Canonical UI)

## 15. No-Go Evaluation
NO STRUCTURAL CHANGE IS CURRENTLY JUSTIFIED. The architecture is cohesive, responsibilities are clearly bounded, and the pipeline, while large, correctly centralizes state transitions. Creating artificial extraction work would violate the principle of MINIMUM NECESSARY COMPLEXITY.

## 16. Test Validation
Execution of test suite post-audit:
`python -m pytest -q` -> 223 passed
Baseline remains fully intact.

## 17. SDD Validation
Execution of `scripts/sdd_check.py`:
**PASS**
Invariants and feature specs remain 100% traceable and verified.

## 18. Architectural Risks
- Leaving subprocess execution inside the pipeline makes unit testing slightly harder (requires mocking `subprocess.run`), but this is already handled successfully by the current 223 tests.

## 19. Recommended Next Step
Advance directly to Phase D3 (Performance Optimization / Pipeline Refinement) or feature development, as the structural architecture requires no hardening at this time.

## 20. Explicit Non-Goals
This phase strictly avoided manufacturing refactoring work for the sake of arbitrary file-size reduction.

## 21. Final Decision
**C. NO STRUCTURAL CHANGE JUSTIFIED**

---

# REQUIRED FINAL SUMMARY

## BASELINE
- pytest: 223 passed
- SDD: PASS

## CANDIDATES ANALYZED
- total: 2
- rejected: 2
- protected: 5
- viable: 0

## BEST CANDIDATE
NO CANDIDATE JUSTIFIED

## ARCHITECTURAL FINDINGS
- duplication: NONE (Intentional fallbacks only)
- dependency direction: STRICTLY OBSERVED
- circular imports: NONE
- accidental complexity: MINIMAL (subprocess wrappers)
- essential complexity preserved: YES (agent_pipeline.py intact)

## FINAL DECISION
C

## RECOMMENDED NEXT PHASE
Phase D3: Performance Optimization

## FILES MODIFIED
NONE

## TESTS MODIFIED
NONE

## SDD MODIFIED
NONE
