"""
Integrator for SDD contract enforcement into existing agent_pipeline.py.
"""
from datetime import datetime
from typing import Any

from .evidence_logger import EvidenceLogger
from .replanner import Diagnosis, Plan, Replanner
from .task_contract import (
    ActionTaskContract,
    ChatTaskContract,
    FeatureTaskContract,
    RecoveryTaskContract,
    TaskContract,
)
from .task_model import Task, TaskStatus, WorkflowPhase
from .task_router import TaskRouter
from .task_types import TaskClassification
from .tool_policy import ToolPolicyEnforcer
from .ui_manager import UIManager
from .verification_engine import VerificationCriterion, VerificationEngine, VerificationResult


class SDDIntegrator:
    """Integrates SDD contract enforcement into existing pipeline."""

    def __init__(self):
        self.router = TaskRouter()
        self.verification_engine = VerificationEngine()
        self.replanner = Replanner(max_replans=2)
        self.ui_manager = UIManager()
        self.tool_policy_enforcer = ToolPolicyEnforcer()
        self.evidence_logger = EvidenceLogger()

    def get_contract(self, task_type: str) -> TaskContract:
        """Get the appropriate contract for a task type."""
        contracts = {
            "CHAT": ChatTaskContract(),
            "ACTION": ActionTaskContract(),
            "FEATURE": FeatureTaskContract(),
            "RECOVERY": RecoveryTaskContract()
        }
        return contracts.get(task_type, ChatTaskContract())

    def classify_prompt(self, prompt: str, context: dict[str, Any] = None) -> TaskClassification:
        """Classify a prompt using the task router."""
        return self.router.classify(prompt, context or {})

    def enforce_tool_policy(
        self,
        task_type: str,
        requested_tools: set,
        task_id: str = "unknown"
    ) -> set:
        """Enforce tool policy for a task type."""
        return self.tool_policy_enforcer.enforce_tool_policy(
            task_type=task_type,
            requested_tools=requested_tools,
            evidence_logger=self.evidence_logger,
            task_id=task_id
        )

    def create_task(
        self,
        task_id: str,
        prompt: str,
        task_type: str,
        metadata: dict[str, Any] = None
    ) -> Task:
        """Create a new task with the appropriate contract."""
        contract = self.get_contract(task_type)
        return Task(
            id=task_id,
            prompt=prompt,
            task_type=task_type,
            status=TaskStatus.INITIALIZED,
            workflow_phase=WorkflowPhase.INIT,
            tools_used=[],
            verification_results={},
            evidence_ids=[],
            iterations=0,
            max_iterations=contract.get_max_iterations(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata=metadata or {}
        )

    def verify_results(
        self,
        _task: Task,
        criteria: list[VerificationCriterion],
        results: dict[str, Any]
    ) -> VerificationResult:
        """Verify results against criteria."""
        return self.verification_engine.verify(criteria, results, self.evidence_logger)

    def should_replan(self, task: Task, diagnosis: Diagnosis | None = None) -> bool:
        """Determine if replanning should occur."""
        return self.replanner.should_replan(
            task_type=task.task_type,
            diagnosis=diagnosis,
            replan_count=task.iterations
        )

    def generate_plan(self, diagnosis: Diagnosis, previous_plan: Plan) -> Plan:
        """Generate a new plan based on diagnosis."""
        return self.replanner.generate_plan(diagnosis, previous_plan)

    def ensure_single_ui_instance(self, session_id: str, ui_type: str) -> Any | None:
        """Ensure only one UI instance exists."""
        try:
            return self.ui_manager.create_instance(session_id, ui_type)
        except ValueError:
            # Instance already exists, get it
            return self.ui_manager.get_instance()

    def update_ui_instance(self, ui_instance: Any) -> None:
        """Update existing UI instance."""
        self.ui_manager.update_instance(ui_instance)

    def get_evidence_for_task(self, task_id: str) -> list[Any]:
        """Get all evidence for a task."""
        return self.evidence_logger.get_evidence_for_task(task_id)
