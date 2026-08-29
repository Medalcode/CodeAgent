"""
Tool Policy Enforcer for controlling tool access by task type.
"""
from dataclasses import dataclass
from typing import Set, Dict
from enum import Enum

from .task_types import ToolType


@dataclass
class ToolPolicy:
    """Policy defining allowed tools for a task type."""
    task_type: str
    allowed_tools: Set[ToolType]
    blocked_tools: Set[ToolType]


class ToolPolicyEnforcer:
    """Controls tool access by task type."""
    
    def __init__(self):
        self.policies = self._initialize_policies()
    
    def _initialize_policies(self) -> Dict[str, ToolPolicy]:
        """Initialize tool policies for each task type."""
        return {
            "CHAT": ToolPolicy(
                task_type="CHAT",
                allowed_tools={ToolType.CONVERSATION},
                blocked_tools={
                    ToolType.FILESYSTEM,
                    ToolType.TERMINAL,
                    ToolType.VERIFICATION,
                    ToolType.REPLANNING,
                    ToolType.UI,
                    ToolType.TEST_RUNNER,
                    ToolType.DEBUGGER
                }
            ),
            "ACTION": ToolPolicy(
                task_type="ACTION",
                allowed_tools={ToolType.CONVERSATION, ToolType.TERMINAL, ToolType.FILESYSTEM},
                blocked_tools={
                    ToolType.VERIFICATION,  # Only if explicitly requested
                    ToolType.REPLANNING,
                    ToolType.UI,
                    ToolType.TEST_RUNNER,
                    ToolType.DEBUGGER
                }
            ),
            "FEATURE": ToolPolicy(
                task_type="FEATURE",
                allowed_tools={
                    ToolType.CONVERSATION,
                    ToolType.TERMINAL,
                    ToolType.FILESYSTEM,
                    ToolType.VERIFICATION,
                    ToolType.REPLANNING,
                    ToolType.UI,
                    ToolType.TEST_RUNNER,
                    ToolType.DEBUGGER
                },
                blocked_tools=set()
            ),
            "RECOVERY": ToolPolicy(
                task_type="RECOVERY",
                allowed_tools={
                    ToolType.CONVERSATION,
                    ToolType.TERMINAL,
                    ToolType.FILESYSTEM,
                    ToolType.UI
                },
                blocked_tools={
                    ToolType.VERIFICATION,
                    ToolType.REPLANNING,
                    ToolType.TEST_RUNNER,
                    ToolType.DEBUGGER
                }
            )
        }
    
    def is_tool_allowed(self, task_type: str, tool_type: ToolType) -> bool:
        """
        Check if a tool is allowed for a task type.
        
        Args:
            task_type: The task type being executed
            tool_type: The tool being requested
            
        Returns:
            True if tool is allowed
        """
        policy = self.policies.get(task_type)
        if not policy:
            return False
        
        return tool_type in policy.allowed_tools
    
    def get_allowed_tools(self, task_type: str) -> Set[ToolType]:
        """Get all allowed tools for a task type."""
        policy = self.policies.get(task_type)
        return policy.allowed_tools if policy else set()
    
    def get_blocked_tools(self, task_type: str) -> Set[ToolType]:
        """Get all blocked tools for a task type."""
        policy = self.policies.get(task_type)
        return policy.blocked_tools if policy else set()
    
    def enforce_tool_policy(
        self,
        task_type: str,
        requested_tools: Set[ToolType],
        evidence_logger = None,
        task_id: str = "unknown"
    ) -> Set[ToolType]:
        """
        Enforce tool policy by filtering requested tools.
        
        Args:
            task_type: The task type being executed
            requested_tools: Set of tools being requested
            evidence_logger: Optional evidence logger for logging violations
            task_id: ID of the task
            
        Returns:
            Set of allowed tools only
        """
        policy = self.policies.get(task_type)
        if not policy:
            return requested_tools
        
        allowed_tools = set()
        blocked_tools = []
        
        for tool in requested_tools:
            if tool in policy.allowed_tools:
                allowed_tools.add(tool)
            else:
                blocked_tools.append(tool)
                
                # Log violation if logger available
                if evidence_logger:
                    evidence_logger.log_tool_policy_violation(
                        task_id=task_id,
                        task_type=task_type,
                        tool=tool.value,
                        reason=f"Tool not allowed for {task_type} task"
                    )
        
        return allowed_tools
