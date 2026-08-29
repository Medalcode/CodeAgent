# Implementation Plan: CodeAgent SDD Contract

## Overview

This task plan implements the SDD (Software Development Design) contract system for CodeAgent. The system enforces behavioral boundaries per task type to prevent four recurring bugs: unexpected UI windows, unnecessary verification, replanning without evidence, and tests running when not requested.

The implementation focuses on adding behavioral guards to existing code through:
- Behavioral contracts with tool access control
- Evidence-based verification
- UI instance lifecycle management
- Evidence logging and diagnosis

## Tasks

- [ ] 1. Create core domain types and contracts
  - [ ] 1.1 Define TaskType enum (CHAT, ACTION, FEATURE, RECOVERY)
    - Create TaskType enum with four values
    - _Requirements: 1, 2, 3, 4, 5_
  
  - [ ] 1.2 Define VerificationState enum (PASS, NOT_REQUIRED, FAIL, ERROR)
    - Create VerificationState enum with four states
    - _Requirements: 6_

  - [ ] 1.3 Define ToolType enum for tool categorization
    - Create ToolType enum (FILESYSTEM, TERMINAL, VERIFICATION, REPLANNING, CONVERSATION, UI, TEST_RUNNER, DEBUGGER)
    - _Requirements: 8, 11_

  - [ ] 1.4 Create TaskContract base interface
    - Define abstract methods: get_allowed_tools(), can_verify(), can_replan(), get_max_iterations()
    - _Requirements: 2, 3, 4, 5, 9_

  - [ ] * 1.5 Write property test for TaskClassificationUniqueness
    - **Property 1: Task Classification Uniqueness**
    - **Validates: Requirements 1**

- [ ] 2. Implement Task Contracts (CHAT, ACTION, FEATURE, RECOVERY)
  - [ ] 2.1 Implement ChatTaskContract class
    - Allowed tools: only CONVERSATION
    - can_verify() returns False
    - can_replan() returns False
    - max_iterations = 1
    - _Requirements: 2_

  - [ ] 2.2 Implement ActionTaskContract class
    - Allowed tools: CONVERSATION, TERMINAL, FILESYSTEM
    - can_verify() returns True (only if requested)
    - can_replan() returns True (only with evidence)
    - max_iterations = 3
    - _Requirements: 3_

  - [ ] 2.3 Implement FeatureTaskContract class
    - Allowed tools: all tools including VERIFICATION, REPLANNING, UI, TEST_RUNNER, DEBUGGER
    - can_verify() returns True
    - can_replan() returns True (with evidence)
    - max_iterations = 5
    - _Requirements: 4_

  - [ ] 2.4 Implement RecoveryTaskContract class
    - Allowed tools: CONVERSATION, TERMINAL, FILESYSTEM, UI
    - can_verify() returns True
    - can_replan() returns True
    - max_iterations = 4
    - _Requirements: 5_

  - [ ] * 2.5 Write unit tests for all task contracts
    - Test each contract's allowed tools set
    - Test can_verify() and can_replan() behavior
    - _Requirements: 2, 3, 4, 5_

- [ ] 3. Implement Task Router with classification logic
  - [ ] 3.1 Create TaskClassification data class
    - Fields: task_type, confidence, classification_reason, metadata
    - _Requirements: 1_

  - [ ] 3.2 Implement classify() method
    - Extract indicators from prompt
    - Apply decision rules
    - Calculate confidence
    - Return TaskClassification
    - _Requirements: 1_

  - [ ] 3.3 Implement indicator extraction method
    - Extract conversation keywords (hola, explica, dime, etc.)
    - Extract action keywords (crea, modifica, escribe, etc.)
    - Extract feature keywords (implementa, construye, agrega, etc.)
    - Extract recovery keywords (recupera, arregla, restaura, etc.)
    - _Requirements: 1_

  - [ ] 3.4 Implement decision rules for task type determination
    - Priority: RECOVERY > FEATURE > ACTION > CHAT
    - Return FEATURE for ambiguous cases
    - _Requirements: 1_

  - [ ] * 3.5 Write property test for classification uniqueness
    - **Property 1: Task Classification Uniqueness**
    - **Validates: Requirements 1**

  - [ ] * 3.6 Write integration tests for router with various prompts
    - Test CHAT prompts
    - Test ACTION prompts
    - Test FEATURE prompts
    - Test RECOVERY prompts
    - _Requirements: 1_

- [ ] 4. Implement Evidence Logger
  - [ ] 4.1 Create Evidence data class
    - Fields: evidence_type, timestamp, task_id, description, expected, actual, difference, additional_context
    - _Requirements: 7, 11_

  - [ ] 4.2 Implement log_verification_fail() method
    - Record verification failure with expected vs actual values
    - Store evidence in in-memory log
    - Return Evidence object
    - _Requirements: 7, 11_

  - [ ] 4.3 Implement log_verification_error() method
    - Record verification error with stack trace
    - Store evidence in in-memory log
    - Return Evidence object
    - _Requirements: 7_

  - [ ] 4.4 Implement log_diagnosis() method
    - Record diagnosis with problem, root cause, and evidence
    - Link to task ID
    - Return Evidence object
    - _Requirements: 11_

  - [ ] 4.5 Implement get_evidence_for_task() method
    - Filter evidence by task_id
    - Return list of evidence entries
    - _Requirements: 7, 11_

  - [ ] * 4.6 Write property test for evidence completeness
    - **Property 6: Evidence-Based Diagnosis**
    - **Validates: Requirements 7, 11**

- [ ] 5. Implement Verification Engine
  - [ ] 5.1 Create VerificationCriterion data class
    - Fields: id, name, description, required, expected, actual, state, evidence_id, details
    - _Requirements: 6, 7_

  - [ ] 5.2 Create VerificationResult data class
    - Fields: state, criteria, success, evidence
    - _Requirements: 6_

  - [ ] 5.3 Implement verify() method
    - Evaluate each criterion against results
    - Assign PASS/FAIL/ERROR/NOT_REQUIRED state
    - Compute overall success
    - Gather evidence for failures
    - _Requirements: 6, 7_

  - [ ] 5.4 Implement compute_success() method
    - Check all required criteria are PASS
    - Exclude NOT_REQUIRED from success calculation
    - _Requirements: 6_

  - [ ] 5.5 Implement gather_evidence() method
    - Analyze expected vs actual difference
    - Format evidence string
    - _Requirements: 7_

  - [ ] * 5.6 Write property test for verification state exhaustiveness
    - **Property 7: Verification State Exhaustiveness**
    - **Validates: Requirements 6**

- [ ] 6. Implement Replanner with evidence-based triggers
  - [ ] 6.1 Create Diagnosis data class
    - Fields: problem, evidence, root_cause, suggested_changes
    - _Requirements: 9, 11_

  - [ ] 6.2 Create Plan data class
    - Fields: steps, tools_needed, expected_outcome
    - _Requirements: 9_

  - [ ] 6.3 Implement should_replan() method
    - Check task type allows replanning
    - Verify evidence exists for ACTION/FEATURE
    - Enforce max_replans limit
    - _Requirements: 9_

  - [ ] 6.4 Implement generate_plan() method
    - Generate revised plan based on diagnosis
    - Document what changed
    - Return new Plan object
    - _Requirements: 9_

  - [ ] 6.5 Implement document_change() method
    - Document what changed and why
    - Link to diagnosis
    - Return documentation string
    - _Requirements: 9_

  - [ ] * 6.6 Write property test for bounded replanning
    - **Property 3: ACTION Task Bounded Execution**
    - **Validates: Requirements 3, 9**

- [ ] 7. Implement UI Manager with single-instance enforcement
  - [ ] 7.1 Create UIInstance data class
    - Fields: id, state, type, session_id
    - _Requirements: 10_

  - [ ] 7.2 Implement create_instance() method
    - Check if instance already exists
    - Raise ValueError if max instances exceeded
    - Create new instance or update existing
    - _Requirements: 10_

  - [ ] 7.3 Implement update_instance() method
    - Update existing instance (no new creation)
    - Raise ValueError if no instance exists
    - _Requirements: 10_

  - [ ] 7.4 Implement close_instance() method
    - Mark instance state as CLOSED
    - _Requirements: 10_

  - [ ] 7.5 Implement terminate_session() method
    - Mark instance state as TERMINATED
    - Clear instance reference
    - _Requirements: 10_

  - [ ] * 7.6 Write property test for UI instance uniqueness
    - **Property 5: UI Instance Uniqueness**
    - **Validates: Requirements 10**

- [ ] 8. Implement Tool Policy Enforcer
  - [ ] 8.1 Create ToolPolicy data class
    - Fields: task_type, allowed_tools, blocked_tools
    - _Requirements: 8_

  - [ ] 8.2 Implement _initialize_policies() method
    - CHAT: only CONVERSATION tool allowed
    - ACTION: CONVERSATION, TERMINAL, FILESYSTEM (no VERIFICATION by default)
    - FEATURE: all tools allowed
    - RECOVERY: CONVERSATION, TERMINAL, FILESYSTEM, UI
    - _Requirements: 8_

  - [ ] 8.3 Implement is_tool_allowed() method
    - Check tool against task type policy
    - Return True/False
    - _Requirements: 8_

  - [ ] 8.4 Implement get_allowed_tools() method
    - Return set of allowed tools for task type
    - _Requirements: 8_

  - [ ] 8.5 Implement enforce_tool_policy() method
    - Filter requested tools to allowed set
    - Log violations for blocked tools
    - _Requirements: 8_

  - [ ] * 8.6 Write unit tests for tool policy enforcement
    - Test allowed tools per task type
    - Test blocked tools rejected
    - _Requirements: 8_

- [ ] 9. Integrate SDD contract enforcement into existing agent_pipeline.py
  - [ ] 9.1 Add TaskRouter import and integration
    - Import TaskRouter from new contract module
    - Add classify_prompt() wrapper method
    - _Requirements: 1_

  - [ ] 9.2 Add contract lookup in run() method
    - Look up TaskContract based on classified task type
    - Pass contract to execution stages
    - _Requirements: 2, 3, 4, 5_

  - [ ] 9.3 Add tool policy enforcement before tool execution
    - Call enforcer.is_tool_allowed() for each tool request
    - Block unauthorized tools
    - Log policy violations
    - _Requirements: 8_

  - [ ] 9.4 Add verification state tracking
    - Track verification results per criterion
    - Use VerificationEngine for final verification
    - _Requirements: 6, 7_

  - [ ] 9.5 Add evidence logging before replanning
    - Call evidence_logger.log_diagnosis() before replanning
    - Require evidence for FEATURE task replanning
    - _Requirements: 9, 11_

  - [ ] 9.6 Add UI manager enforcement
    - Check UIManager before creating UI instances
    - Update existing instance instead of creating new
    - _Requirements: 10_

  - [ ] * 9.7 Write integration tests for pipeline integration
    - Test CHAT task with no verification
    - Test ACTION task with limited tools
    - Test FEATURE task with full workflow
    - Test RECOVERY task restoration
    - _Requirements: 2, 3, 4, 5, 8, 10_

- [ ] 10. Create data models for task execution tracking
  - [ ] 10.1 Create Task data class
    - Fields: id, prompt, task_type, status, workflow_phase, tools_used, verification_results, evidence_ids, iterations, max_iterations, created_at, updated_at, metadata
    - _Requirements: 1, 2, 3, 4, 5_

  - [ ] 10.2 Implement mark_verified() method
    - Update verification_results
    - Set status to VERIFIED
    - Update timestamp
    - _Requirements: 6_

  - [ ] 10.3 Implement mark_failed() method
    - Add evidence_id to evidence_ids list
    - Set status to FAILED
    - Update timestamp
    - _Requirements: 7_

  - [ ] * 10.4 Write unit tests for Task model
    - Test state transitions
    - Test verification result updates
    - _Requirements: 1, 6, 7_

- [ ] 11. Add bounded execution enforcement
  - [ ] 11.1 Add max_iterations check in Task contract
    - Return contract's max_iterations for each task type
    - _Requirements: 12_

  - [ ] 11.2 Implement iteration tracking in Task class
    - Increment iterations on each replan
    - Check against max_iterations
    - _Requirements: 12_

  - [ ] 11.3 Add termination logic when iterations exceeded
    - Set status to TERMINATED
    - Return failure with summary
    - _Requirements: 12_

  - [ ] * 11.4 Write property test for bounded execution
    - **Property: Bounded Execution**
    - **Validates: Requirements 12**

- [ ] 12. Create migration scripts for existing code
  - [ ] 12.1 Create compatibility wrapper for existing code
    - Map old TaskType (CHAT, ACTION, FEATURE) to new TaskType
    - Handle RECOVERY as new type
    - _Requirements: 1_

  - [ ] 12.2 Add backward compatibility mode
    - If contract module unavailable, use existing behavior
    - Log warning for backward compatibility usage
    - _Requirements: 1, 2, 3, 4_

  - [ ] 12.3 Add migration guide documentation
    - Document behavioral changes per task type
    - List breaking changes
    - Provide upgrade steps
    - _Requirements: 1, 2, 3, 4, 5, 8_

  - [ ] * 12.4 Write migration tests
    - Test old prompts classified correctly
    - Test new prompts with RECOVERY type
    - _Requirements: 1, 5_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties defined in the design document
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end behavior
- The implementation focuses on adding behavioral guards to existing code, not rewriting from scratch

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "1.3"] },
    { "id": 1, "tasks": ["1.4", "2.1", "2.2", "2.3", "2.4"] },
    { "id": 2, "tasks": ["1.5", "2.5", "3.1", "3.2", "4.1"] },
    { "id": 3, "tasks": ["3.3", "3.4", "4.2", "4.3", "4.4", "4.5"] },
    { "id": 4, "tasks": ["3.5", "3.6", "4.6", "5.1", "5.2", "5.3"] },
    { "id": 5, "tasks": ["5.4", "5.5", "5.6", "6.1", "6.2", "6.3"] },
    { "id": 6, "tasks": ["6.4", "6.5", "6.6", "7.1", "7.2", "7.3"] },
    { "id": 7, "tasks": ["7.4", "7.5", "7.6", "8.1", "8.2", "8.3"] },
    { "id": 8, "tasks": ["8.4", "8.5", "8.6", "9.1", "9.2", "9.3"] },
    { "id": 9, "tasks": ["9.4", "9.5", "9.6", "9.7", "10.1", "10.2"] },
    { "id": 10, "tasks": ["10.3", "10.4", "11.1", "11.2", "11.3", "11.4"] },
    { "id": 11, "tasks": ["12.1", "12.2", "12.3", "12.4"] }
  ]
}
```