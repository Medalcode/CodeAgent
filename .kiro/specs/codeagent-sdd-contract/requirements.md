# Requirements Document

## Introduction

This document defines the contract of behavior for the CodeAgent platform. CodeAgent is a local AI-powered code agent system that executes tasks through a supervisor orchestration layer. This specification establishes formal boundaries and guarantees about agent behavior to prevent known bugs from recurring.

The bugs this contract addresses include:
- Unexpected UI windows being created during agent execution
- Unnecessary verification steps being triggered
- Replanning without evidence of failure
- Tests running when not explicitly requested

This is a living contract that will evolve as new behavioral patterns are discovered and formalized.

## Glossary

- **CodeAgent**: The local AI-powered code agent platform (v6.11 Enterprise)
- **Orquestador**: The supervisor agent that runs benchmarks at three levels (baja, media, alta)
- **Task**: A unit of work assigned to the agent, classified into specific types
- **Tool**: An executable capability available to the agent (e.g., file reading, command execution)
- **Verification**: The process of validating task results against acceptance criteria
- **Replanning**: The agent's ability to revise its approach after encountering obstacles
- **UI Instance**: A visible interface window or panel presented to the user
- **Evidence**: Concrete proof of failure or deviation from expected behavior

## Requirements

### Requirement 1: Task Classification

**User Story:** As a user, I want tasks to be clearly classified so that I can understand what behavior to expect from the agent.

#### Acceptance Criteria

1. THE CodeAgent SHALL classify every task as exactly one of: CHAT, ACTION, FEATURE, or RECOVERY
2. WHEN a task is received, THE CodeAgent SHALL determine its classification before executing any tools
3. WHERE a task classification is ambiguous, THE CodeAgent SHALL ask for clarification before proceeding

### Requirement 2: CHAT Task Contract

**User Story:** As a user, I want CHAT tasks to be conversational so that I can have natural discussions without unintended side effects.

#### Acceptance Criteria

1. FOR A CHAT task, THE CodeAgent SHALL NOT access the filesystem
2. FOR A CHAT task, THE CodeAgent SHALL NOT execute terminal commands
3. FOR A CHAT task, THE CodeAgent SHALL NOT trigger verification steps
4. FOR A CHAT task, THE CodeAgent SHALL NOT perform replanning
5. WHEN a CHAT task is completed, THE CodeAgent SHALL return exactly one response and mark the task as DONE

### Requirement 3: ACTION Task Contract

**User Story:** As a user, I want ACTION tasks to execute efficiently so that I can complete specific operations without unnecessary steps.

#### Acceptance Criteria

1. FOR AN ACTION task, THE CodeAgent SHALL use only the tools necessary to complete the task
2. FOR AN ACTION task, THE CodeAgent SHALL verify only what was explicitly requested
3. IF an ACTION task succeeds on first attempt, THE CodeAgent SHALL perform zero replans
4. IF an ACTION task fails, THE CodeAgent SHALL diagnose the failure before replanning
5. FOR AN ACTION task, THE CodeAgent SHALL NOT access tools outside the task scope

### Requirement 4: FEATURE Task Contract

**User Story:** As a user, I want FEATURE tasks to follow a structured workflow so that new functionality is implemented correctly.

#### Acceptance Criteria

1. FOR A FEATURE task, THE CodeAgent SHALL follow the workflow: PLAN → EXPLORE → EXECUTE → VERIFY → DIAGNOSE/REPLAN
2. WHEN a FEATURE task enters the VERIFY phase and fails, THE CodeAgent SHALL enter the DIAGNOSE phase
3. FOR THE DIAGNOSE phase, THE CodeAgent SHALL require evidence of failure before replanning
4. WHEN evidence of failure is found, THE CodeAgent SHALL replan based on the diagnosis
5. FOR A FEATURE task, THE CodeAgent SHALL NOT skip the VERIFY phase
6. FOR A FEATURE task, THE CodeAgent SHALL invoke the CRITIC after successful verification

### Requirement 5: RECOVERY Task Contract

**User Story:** As a user, I want RECOVERY tasks to restore system state so that failures can be properly handled.

#### Acceptance Criteria

1. FOR A RECOVERY task, THE CodeAgent SHALL restore system state to a known-good condition
2. FOR A RECOVERY task, THE CodeAgent SHALL document what was recovered and how
3. WHEN recovery is complete, THE CodeAgent SHALL return to normal task execution
4. FOR A RECOVERY task, THE CodeAgent SHALL not modify requirements beyond what is necessary for recovery

### Requirement 6: Verification States

**User Story:** As a user, I want verification results to be clearly defined so that I understand whether a task passed or failed.

#### Acceptance Criteria

1. EACH verification criterion SHALL have exactly one of these states: PASS, NOT_REQUIRED, FAIL, ERROR
2. FOR a task with all required criteria, THE CodeAgent SHALL compute SUCCESS = all required criteria == PASS
3. IF a criterion is marked NOT_REQUIRED, THE CodeAgent SHALL exclude it from the success calculation
4. FOR a task with verification results PASS + PASS + NOT_REQUIRED, THE CodeAgent SHALL mark it as SUCCESS
5. FOR a task with verification results PASS + FAIL, THE CodeAgent SHALL mark it as FAILURE

### Requirement 7: Verification Evidence

**User Story:** As a user, I want verification to be based on evidence so that results are trustworthy.

#### Acceptance Criteria

1. FOR ANY verification that produces FAIL or ERROR, THE CodeAgent SHALL provide evidence
2. THE evidence SHALL include the expected outcome, actual outcome, and the difference
3. FOR a FAIL verification, THE CodeAgent SHALL identify which specific criterion failed
4. FOR an ERROR verification, THE CodeAgent SHALL include error details and stack trace if applicable

### Requirement 8: Tool Policy by Task Type

**User Story:** As a user, I want tool access to be controlled by task type so that dangerous operations are prevented.

#### Acceptance Criteria

1. FOR A CHAT task, THE CodeAgent SHALL have access to conversation tools only
2. FOR AN ACTION task, THE CodeAgent SHALL have access only to tools required for the specific task
3. FOR A FEATURE task, THE CodeAgent SHALL have access to all tools but with guided workflow
4. FOR A RECOVERY task, THE CodeAgent SHALL have access to tools needed for restoration
5. WHEN a task attempts to use a tool outside its allowed set, THE CodeAgent SHALL reject the tool usage

### Requirement 9: Replanning Constraints

**User Story:** As a user, I want replanning to be evidence-based so that the agent doesn't change course unnecessarily.

#### Acceptance Criteria

1. FOR AN ACTION task that succeeds, THE CodeAgent SHALL perform zero replans
2. FOR A FEATURE task, THE CodeAgent SHALL NOT replan without first entering the DIAGNOSE phase
3. FOR THE DIAGNOSE phase, THE CodeAgent SHALL require concrete evidence of failure before replanning
4. WHEN replanning occurs, THE CodeAgent SHALL document what changed and why
5. THE total number of replans for any single task SHALL be bounded by a system-defined maximum

### Requirement 10: UI Lifecycle Policy

**User Story:** As a user, I want exactly one UI instance per session so that no unexpected windows appear.

#### Acceptance Criteria

1. THE CodeAgent SHALL NEVER create additional UI windows during any task execution
2. FOR A single user session, THE CodeAgent SHALL maintain exactly one UI instance
3. NO inference, tool execution, verification, or replanning SHALL create new UI instances
4. WHEN a UI instance is closed, THE CodeAgent SHALL mark the session as terminated
5. FOR A FEATURE task, THE CodeAgent SHALL update the existing UI instance, not create new ones

### Requirement 11: Evidence Requirement for Diagnosis

**User Story:** As a user, I want diagnosis to require evidence so that corrective actions are justified.

#### Acceptance Criteria

1. WHEN a FEATURE task fails verification, THE CodeAgent SHALL NOT replan until evidence is gathered
2. THE evidence SHALL be concrete and verifiable (e.g., test failure output, error message)
3. FOR A diagnostic phase, THE CodeAgent SHALL not rely on assumptions or guesses
4. IF no evidence of failure can be found, THE CodeAgent SHALL report uncertainty rather than replan
5. WHEN evidence is gathered, THE CodeAgent SHALL document it before replanning

### Requirement 12: Bounded Execution

**User Story:** As a user, I want execution to be bounded so that tasks don't run indefinitely.

#### Acceptance Criteria

1. EACH task SHALL have a maximum iteration count defined by the system
2. WHEN maximum iterations are reached, THE CodeAgent SHALL terminate and report failure
3. FOR FEATURE tasks, THE CodeAgent SHALL report progress through phases (PLAN, EXPLORE, EXECUTE, VERIFY, DIAGNOSE)
4. FOR tasks that exceed time limits, THE CodeAgent SHALL terminate gracefully
5. WHEN termination occurs, THE CodeAgent SHALL provide a summary of what was accomplished
