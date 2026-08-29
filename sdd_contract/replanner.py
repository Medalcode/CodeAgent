"""
Replanner with evidence-based triggers.
"""
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class PlanStatus(Enum):
    """Status of a plan."""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


@dataclass
class PlanStep:
    """A single step in a plan."""
    id: str
    description: str
    tools_needed: List[str]
    expected_outcome: str
    condition: str = "always"  # always, if_success, if_failure


@dataclass
class Plan:
    """A plan for task execution."""
    id: str
    task_id: str
    steps: List[PlanStep]
    tools_needed: List[str]
    expected_outcome: str
    status: PlanStatus = PlanStatus.DRAFT
    version: int = 1
    parent_plan_id: Optional[str] = None  # For replanning history
    
    def add_step(self, step: PlanStep) -> None:
        """Add a step to the plan."""
        self.steps.append(step)
        if step.tools_needed:
            for tool in step.tools_needed:
                if tool not in self.tools_needed:
                    self.tools_needed.append(tool)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "steps": [s.__dict__ for s in self.steps],
            "tools_needed": self.tools_needed,
            "expected_outcome": self.expected_outcome,
            "status": self.status.value,
            "version": self.version,
            "parent_plan_id": self.parent_plan_id
        }


@dataclass
class Diagnosis:
    """Diagnosis of a failure."""
    id: str
    task_id: str
    problem: str
    evidence: str
    root_cause: str
    suggested_changes: List[str]
    verified: bool = False  # Has evidence been verified?
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "problem": self.problem,
            "evidence": self.evidence,
            "root_cause": self.root_cause,
            "suggested_changes": self.suggested_changes,
            "verified": self.verified
        }


class Replanner:
    """Plans alternative approaches based on evidence."""
    
    def __init__(self, max_replans: int = 2):
        self.max_replans = max_replans
    
    def should_replan(
        self,
        task_type: str,
        diagnosis: Optional[Diagnosis],
        replan_count: int
    ) -> bool:
        """
        Determine if replanning should occur.
        
        Args:
            task_type: Type of task being executed
            diagnosis: Evidence-based diagnosis (if available)
            replan_count: Number of replans so far
            
        Returns:
            True if replanning should proceed
        """
        # Must have diagnosis with evidence
        if diagnosis is None:
            return False
        
        # Must have evidence in diagnosis
        if not diagnosis.evidence or diagnosis.evidence.strip() == "":
            return False
        
        # Check replan limit
        if replan_count >= self.max_replans:
            return False
        
        # ACTION tasks: replan only after evidence gathered
        if task_type == "ACTION":
            return True
        
        # FEATURE tasks: replan only after DIAGNOSE phase with evidence
        if task_type == "FEATURE":
            return True
        
        # RECOVERY tasks: replan based on diagnosis
        if task_type == "RECOVERY":
            return True
        
        # Other task types: replan only with strong evidence
        return True
    
    def generate_plan(
        self,
        diagnosis: Diagnosis,
        previous_plan: Plan
    ) -> Plan:
        """
        Generate new plan based on diagnosis.
        
        Args:
            diagnosis: Evidence-based diagnosis of failure
            previous_plan: The plan that failed
            
        Returns:
            New revised plan
        """
        new_steps = []
        for i, step in enumerate(previous_plan.steps):
            # Modify steps based on diagnosis
            new_description = step.description
            
            # If diagnosis suggests specific changes, incorporate them
            for change in diagnosis.suggested_changes:
                if change.lower() in step.description.lower():
                    new_description = f"[REVISED] {step.description}"
            
            new_steps.append(PlanStep(
                id=f"step-{i}",
                description=new_description,
                tools_needed=step.tools_needed,
                expected_outcome=step.expected_outcome,
                condition=step.condition
            ))
        
        new_plan = Plan(
            id=f"plan-{previous_plan.version + 1}",
            task_id=previous_plan.task_id,
            steps=new_steps,
            tools_needed=previous_plan.tools_needed.copy(),
            expected_outcome=previous_plan.expected_outcome,
            status=PlanStatus.DRAFT,
            version=previous_plan.version + 1,
            parent_plan_id=previous_plan.id
        )
        
        return new_plan
    
    def document_change(
        self,
        previous: Plan,
        new: Plan,
        diagnosis: Diagnosis
    ) -> str:
        """
        Document what changed and why.
        
        Args:
            previous: Previous plan
            new: New plan
            diagnosis: Diagnosis that triggered the change
            
        Returns:
            Detailed change documentation
        """
        return f"""Replanned from {previous.id} to {new.id}:
Problem: {diagnosis.problem}
Root Cause: {diagnosis.root_cause}
Evidence: {diagnosis.evidence}
Changes: {", ".join(diagnosis.suggested_changes) if diagnosis.suggested_changes else "N/A"}
Previous expected outcome: {previous.expected_outcome}
New expected outcome: {new.expected_outcome}"""
