"""
Verification Engine for validating task results against criteria.
"""
from dataclasses import dataclass
from typing import Any

from .task_types import VerificationState


@dataclass
class VerificationCriterion:
    """A single verification criterion."""
    id: str
    name: str
    description: str
    required: bool
    expected: str
    actual: str | None = None
    state: VerificationState = VerificationState.NOT_REQUIRED
    evidence_id: str | None = None
    details: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "required": self.required,
            "expected": self.expected,
            "actual": self.actual,
            "state": self.state.value,
            "evidence_id": self.evidence_id,
            "details": self.details
        }


@dataclass
class VerificationResult:
    """Result of verification process."""
    state: VerificationState
    criteria: list[VerificationCriterion]
    success: bool
    evidence: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "state": self.state.value,
            "criteria": [c.to_dict() for c in self.criteria],
            "success": self.success,
            "evidence": self.evidence
        }


class VerificationEngine:
    """Validates task results against acceptance criteria."""

    def verify(
        self,
        criteria: list[VerificationCriterion],
        results: dict[str, Any],
        evidence_logger = None
    ) -> VerificationResult:
        """
        Verify results against criteria.

        Args:
            criteria: List of verification criteria
            results: Actual results from task execution
            evidence_logger: Optional evidence logger for recording failures

        Returns:
            VerificationResult with overall state and evidence
        """
        verification_results: list[VerificationCriterion] = []
        pass_count = 0
        fail_count = 0
        error_count = 0

        for criterion in criteria:
            result = self._evaluate_criterion(criterion, results, evidence_logger)
            verification_results.append(result)

            if result.state == VerificationState.PASS:
                pass_count += 1
            elif result.state == VerificationState.FAIL:
                fail_count += 1
            elif result.state == VerificationState.ERROR:
                error_count += 1

        # Compute success: all required criteria must be PASS
        [c for c in criteria if c.required]
        success = (fail_count == 0 and error_count == 0)

        # Gather evidence if any failures
        if fail_count > 0 or error_count > 0:
            evidence = self._gather_verification_evidence(verification_results)
        else:
            evidence = "All verification criteria passed"

        state = VerificationState.PASS if success else VerificationState.FAIL

        return VerificationResult(
            state=state,
            criteria=verification_results,
            success=success,
            evidence=evidence
        )

    def _evaluate_criterion(
        self,
        criterion: VerificationCriterion,
        results: dict[str, Any],
        evidence_logger = None
    ) -> VerificationCriterion:
        """
        Evaluate a single criterion against results.

        Args:
            criterion: The criterion to evaluate
            results: Actual results from task execution
            evidence_logger: Optional evidence logger

        Returns:
            Criterion with updated state and results
        """
        # If not required, mark as NOT_REQUIRED
        if not criterion.required:
            return criterion

        # Get expected and actual values
        expected = criterion.expected
        actual = results.get(criterion.id) if criterion.id in results else results.get(criterion.name)

        # If actual not found, mark as ERROR
        if actual is None:
            if evidence_logger:
                evidence_id = evidence_logger.log_verification_error(
                    task_id="unknown",
                    error_message=f"Actual value not found for criterion: {criterion.name}"
                ).task_id
            else:
                evidence_id = None

            return VerificationCriterion(
                id=criterion.id,
                name=criterion.name,
                description=criterion.description,
                required=criterion.required,
                expected=criterion.expected,
                actual="NOT_FOUND",
                state=VerificationState.ERROR,
                evidence_id=evidence_id,
                details="Actual value not found"
            )

        # Compare expected vs actual
        if actual == expected:
            return VerificationCriterion(
                id=criterion.id,
                name=criterion.name,
                description=criterion.description,
                required=criterion.required,
                expected=expected,
                actual=actual,
                state=VerificationState.PASS
            )
        else:
            difference = self._analyze_difference(expected, actual)
            if evidence_logger:
                evidence_id = evidence_logger.log_verification_fail(
                    task_id="unknown",
                    criterion_name=criterion.name,
                    expected=expected,
                    actual=actual,
                    difference=difference
                ).task_id
            else:
                evidence_id = None

            return VerificationCriterion(
                id=criterion.id,
                name=criterion.name,
                description=criterion.description,
                required=criterion.required,
                expected=expected,
                actual=actual,
                state=VerificationState.FAIL,
                evidence_id=evidence_id,
                details=difference
            )

    def _get_actual_value(self, results: dict[str, Any], criterion_name: str) -> Any | None:
        """Get actual value from results for a criterion name."""
        return results.get(criterion_name)

    def _analyze_difference(self, expected: str, actual: str) -> str:
        """Analyze the difference between expected and actual."""
        if len(expected) < 100 and len(actual) < 100:
            return f"Expected: '{expected}', Actual: '{actual}'"
        else:
            return "Value mismatch: expected and actual differ"

    def _gather_verification_evidence(self, criteria: list[VerificationCriterion]) -> str:
        """
        Gather evidence from all verification results.

        Args:
            criteria: List of verification criteria with results

        Returns:
            Evidence string summarizing failures
        """
        failures = [
            c for c in criteria
            if c.state in (VerificationState.FAIL, VerificationState.ERROR)
        ]

        if not failures:
            return "All criteria passed"

        failure_details = "\n".join([
            f"- {c.name}: {c.details}" for c in failures
        ])

        return f"Verification failed for {len(failures)} criteria:\n{failure_details}"

    def compute_success(self, criteria: list[VerificationCriterion]) -> bool:
        """
        Compute overall success based on criteria states.

        Args:
            criteria: List of verification criteria

        Returns:
            True if all required criteria are PASS
        """
        required_criteria = [c for c in criteria if c.required]
        if not required_criteria:
            return True

        return all(c.state == VerificationState.PASS for c in required_criteria)
