"""
Integrator for SDD contract enforcement into existing agent_pipeline.py.
"""
from typing import Dict, Any, Optional

from .task_router import TaskRouter
from .task_contract import TaskContract, ChatTaskContract, ActionTaskContract, FeatureTaskContract, RecoveryTaskContract
from .verification_engine import VerificationEngine, VerificationCriterion, VerificationResult
from .replanner import Replanner, Plan, Diagnosis
from .ui_manager import UIManager
from .tool_policy import ToolPolicyEnforcer
from .evidence_logger import EvidenceLogger
from .task_types import TaskType, TaskClassification
from .task_model import Task, TaskStatus, WorkflowPhase, TaskResult


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
    
    def classify_prompt(self, prompt: str, context: Dict[str, Any] = None) -> TaskClassification:
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
        metadata: Dict[str, Any] = None
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
        task: Task,
        criteria: List[VerificationCriterion],
        results: Dict[str, Any]
    ) -> VerificationResult:
        """Verify results against criteria."""
        return self.verification_engine.verify(criteria, results, self.evidence_logger)
    
    def should_replan(self, task: Task, diagnosis: Optional[Diagnosis] = None) -> bool:
        """Determine if replanning should occur."""
        return self.replanner.should_replan(
            task_type=task.task_type,
            diagnosis=diagnosis,
            replan_count=task.iterations
        )
    
    def generate_plan(self, diagnosis: Diagnosis, previous_plan: Plan) -> Plan:
        """Generate a new plan based on diagnosis."""
        return self.replanner.generate_plan(diagnosis, previous_plan)
    
    def ensure_single_ui_instance(self, session_id: str, ui_type: str) -> Optional[Any]:
        """Ensure only one UI instance exists."""
        try:
            return self.ui_manager.create_instance(session_id, ui_type)
        except ValueError:
            # Instance already exists, get it
            return self.ui_manager.get_instance()
    
    def update_ui_instance(self, ui_instance: Any) -> None:
        """Update existing UI instance."""
        self.ui_manager.update_instance(ui_instance)
    
    def get_evidence_for_task(self, task_id: str) -> List[Any]:
        """Get all evidence for a task."""
        return self.evidence_logger.get_evidence_for_task(task_id)
