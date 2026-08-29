"""
Evidence Logger for recording verification failures and diagnoses.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class EvidenceType(Enum):
    """Types of evidence that can be logged."""
    VERIFICATION_FAIL = "VERIFICATION_FAIL"
    VERIFICATION_ERROR = "VERIFICATION_ERROR"
    DIAGNOSIS = "DIAGNOSIS"
    REPLAN = "REPLAN"
    TOOL_POLICY_VIOLATION = "TOOL_POLICY_VIOLATION"
    EXECUTION = "EXECUTION"


@dataclass
class Evidence:
    """Evidence entry for verification results and diagnoses."""
    evidence_type: EvidenceType
    timestamp: datetime
    task_id: str
    description: str
    expected: str
    actual: str
    difference: str
    additional_context: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "evidence_type": self.evidence_type.value,
            "timestamp": self.timestamp.isoformat(),
            "task_id": self.task_id,
            "description": self.description,
            "expected": self.expected,
            "actual": self.actual,
            "difference": self.difference,
            "additional_context": self.additional_context
        }


class EvidenceLogger:
    """Records concrete proof of verification results."""

    def __init__(self):
        self.evidence_log: list[Evidence] = []

    def log_verification_fail(
        self,
        task_id: str,
        criterion_name: str,
        expected: str,
        actual: str,
        difference: str
    ) -> Evidence:
        """
        Log a verification failure with evidence.

        Args:
            task_id: ID of the task
            criterion_name: Name of the failed criterion
            expected: Expected outcome
            actual: Actual outcome
            difference: Analysis of difference

        Returns:
            The logged Evidence object
        """
        evidence = Evidence(
            evidence_type=EvidenceType.VERIFICATION_FAIL,
            timestamp=datetime.now(),
            task_id=task_id,
            description=f"Verification failed for criterion: {criterion_name}",
            expected=expected,
            actual=actual,
            difference=difference
        )
        self.evidence_log.append(evidence)
        return evidence

    def log_verification_error(
        self,
        task_id: str,
        error_message: str,
        stack_trace: str | None = None
    ) -> Evidence:
        """
        Log a verification error.

        Args:
            task_id: ID of the task
            error_message: Error message from verification
            stack_trace: Optional stack trace

        Returns:
            The logged Evidence object
        """
        evidence = Evidence(
            evidence_type=EvidenceType.VERIFICATION_ERROR,
            timestamp=datetime.now(),
            task_id=task_id,
            description="Verification encountered an error",
            expected="Verification to complete successfully",
            actual=error_message,
            difference="Exception occurred during verification",
            additional_context=stack_trace
        )
        self.evidence_log.append(evidence)
        return evidence

    def log_diagnosis(
        self,
        task_id: str,
        problem: str,
        root_cause: str,
        evidence: str
    ) -> Evidence:
        """
        Log a diagnosis with evidence.

        Args:
            task_id: ID of the task
            problem: The problem identified
            root_cause: Root cause analysis
            evidence: Supporting evidence

        Returns:
            The logged Evidence object
        """
        evidence_obj = Evidence(
            evidence_type=EvidenceType.DIAGNOSIS,
            timestamp=datetime.now(),
            task_id=task_id,
            description=f"Diagnosis: {problem}",
            expected="Task to succeed",
            actual=f"Root cause: {root_cause}",
            difference=evidence
        )
        self.evidence_log.append(evidence_obj)
        return evidence_obj

    def log_replan(
        self,
        task_id: str,
        previous_plan_id: str,
        new_plan_id: str,
        diagnosis: str
    ) -> Evidence:
        """
        Log a replanning event with diagnosis.

        Args:
            task_id: ID of the task
            previous_plan_id: ID of the previous plan
            new_plan_id: ID of the new plan
            diagnosis: Diagnosis that triggered replanning

        Returns:
            The logged Evidence object
        """
        evidence = Evidence(
            evidence_type=EvidenceType.REPLAN,
            timestamp=datetime.now(),
            task_id=task_id,
            description=f"Replanning: {previous_plan_id} -> {new_plan_id}",
            expected="Task to succeed with previous plan",
            actual=f"Replanning with new plan due to: {diagnosis}",
            difference="New plan created based on diagnosis"
        )
        self.evidence_log.append(evidence)
        return evidence

    def log_tool_policy_violation(
        self,
        task_id: str,
        task_type: str,
        tool: str,
        reason: str
    ) -> Evidence:
        """
        Log a tool policy violation.

        Args:
            task_id: ID of the task
            task_type: Type of task attempting to use tool
            tool: Tool that was blocked
            reason: Reason for blocking

        Returns:
            The logged Evidence object
        """
        evidence = Evidence(
            evidence_type=EvidenceType.TOOL_POLICY_VIOLATION,
            timestamp=datetime.now(),
            task_id=task_id,
            description=f"Tool policy violation: {tool} blocked for {task_type}",
            expected=f"{tool} to be allowed for {task_type}",
            actual=f"{tool} blocked: {reason}",
            difference="Tool access denied by policy"
        )
        self.evidence_log.append(evidence)
        return evidence

    def get_evidence_for_task(self, task_id: str) -> list[Evidence]:
        """Get all evidence for a specific task."""
        return [e for e in self.evidence_log if e.task_id == task_id]

    def get_recent_evidence(self, limit: int = 10) -> list[Evidence]:
        """Get most recent evidence entries."""
        return sorted(
            self.evidence_log,
            key=lambda e: e.timestamp,
            reverse=True
        )[:limit]
