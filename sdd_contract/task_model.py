"""
Task data model for execution tracking.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class TaskStatus(Enum):
    """Status of task execution."""
    INITIALIZED = "INITIALIZED"
    RUNNING = "RUNNING"
    EXECUTING = "EXECUTING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    RECOVERED = "RECOVERED"
    TERMINATED = "TERMINATED"


class WorkflowPhase(Enum):
    """Workflow phases for tasks."""
    INIT = "INIT"
    PLAN = "PLAN"
    EXPLORE = "EXPLORE"
    EXECUTE = "EXECUTE"
    VERIFY = "VERIFY"
    DIAGNOSE = "DIAGNOSE"
    REPLAN = "REPLAN"
    CRITIC = "CRITIC"
    DONE = "DONE"


@dataclass
class Task:
    """Represents a task being executed."""
    id: str
    prompt: str
    task_type: str  # CHAT, ACTION, FEATURE, RECOVERY
    status: TaskStatus
    workflow_phase: WorkflowPhase
    tools_used: list[str]
    verification_results: dict[str, str]  # criterion_name -> PASS/FAIL/ERROR/NOT_REQUIRED
    evidence_ids: list[str]  # References to evidence logger entries
    iterations: int
    max_iterations: int
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any]

    def can_replan(self) -> bool:
        """Check if task can still replan."""
        return (
            self.iterations < self.max_iterations
            and self.task_type in ("ACTION", "FEATURE", "RECOVERY")
        )

    def mark_verified(self, results: dict[str, str]) -> None:
        """Mark task as verified with results."""
        self.verification_results = results
        self.status = TaskStatus.VERIFIED
        self.updated_at = datetime.now()

    def mark_failed(self, evidence_id: str) -> None:
        """Mark task as failed with evidence reference."""
        self.evidence_ids.append(evidence_id)
        self.status = TaskStatus.FAILED
        self.updated_at = datetime.now()

    def increment_iterations(self) -> None:
        """Increment iteration count."""
        self.iterations += 1
        self.updated_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "prompt": self.prompt,
            "task_type": self.task_type,
            "status": self.status.value,
            "workflow_phase": self.workflow_phase.value,
            "tools_used": self.tools_used,
            "verification_results": self.verification_results,
            "evidence_ids": self.evidence_ids,
            "iterations": self.iterations,
            "max_iterations": self.max_iterations,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class TaskResult:
    """Result of task execution."""
    success: bool
    task_id: str
    response: str | None = None
    execution_result: dict[str, Any] | None = None
    verification_result: dict[str, Any] | None = None
    replan_count: int = 0
    error: str | None = None
    evidence_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "task_id": self.task_id,
            "response": self.response,
            "execution_result": self.execution_result,
            "verification_result": self.verification_result,
            "replan_count": self.replan_count,
            "error": self.error,
            "evidence_ids": self.evidence_ids
        }
