"""
Task Contract implementations for SDD.
Enforces behavioral boundaries per task type.
"""
from abc import ABC, abstractmethod

from .task_types import ToolType


class TaskContract(ABC):
    """Base interface for all task contracts."""

    @abstractmethod
    def get_allowed_tools(self) -> set[ToolType]:
        """Return set of tools allowed for this task type."""
        raise NotImplementedError

    @abstractmethod
    def can_verify(self) -> bool:
        """Return True if verification is allowed for this task."""
        raise NotImplementedError

    @abstractmethod
    def can_replan(self) -> bool:
        """Return True if replanning is allowed for this task."""
        raise NotImplementedError

    @abstractmethod
    def get_max_iterations(self) -> int:
        """Return maximum iterations for this task type."""
        raise NotImplementedError

    @property
    def requires_code_verification(self) -> bool:
        """Compatibility property for pipeline verification check."""
        return self.can_verify()

    @property
    def requires_tests(self) -> bool:
        """Compatibility property for pipeline test requirement check."""
        return self.can_verify() and ToolType.TEST_RUNNER in self.get_allowed_tools()

    @property
    def requires_execution(self) -> bool:
        """Compatibility property for execution phase requirement."""
        return self.get_max_iterations() > 1

    @property
    def tools_allowed(self) -> bool:
        """Compatibility property for tool usage allowance."""
        return len(self.get_allowed_tools()) > 1

    @property
    def files_allowed(self) -> bool:
        """Compatibility property for filesystem modification allowance."""
        return ToolType.FILESYSTEM in self.get_allowed_tools()


class ChatTaskContract(TaskContract):
    """Contract for CHAT tasks - conversational only."""

    def get_allowed_tools(self) -> set[ToolType]:
        return {ToolType.CONVERSATION}

    def can_verify(self) -> bool:
        return False

    def can_replan(self) -> bool:
        return False

    def get_max_iterations(self) -> int:
        return 1


class ActionTaskContract(TaskContract):
    """Contract for ACTION tasks - minimal tools, single operation."""

    def get_allowed_tools(self) -> set[ToolType]:
        return {ToolType.CONVERSATION, ToolType.TERMINAL, ToolType.FILESYSTEM}

    def can_verify(self) -> bool:
        return True  # Only if explicitly requested

    def can_replan(self) -> bool:
        return True  # Only after evidence gathered

    def get_max_iterations(self) -> int:
        return 3


class FeatureTaskContract(TaskContract):
    """Contract for FEATURE tasks - full workflow."""

    def get_allowed_tools(self) -> set[ToolType]:
        return {
            ToolType.CONVERSATION,
            ToolType.TERMINAL,
            ToolType.FILESYSTEM,
            ToolType.VERIFICATION,
            ToolType.REPLANNING,
            ToolType.UI,
            ToolType.TEST_RUNNER,
            ToolType.DEBUGGER
        }

    def can_verify(self) -> bool:
        return True

    def can_replan(self) -> bool:
        return True  # With evidence

    def get_max_iterations(self) -> int:
        return 5


class RecoveryTaskContract(TaskContract):
    """Contract for RECOVERY tasks - state restoration."""

    def get_allowed_tools(self) -> set[ToolType]:
        return {
            ToolType.CONVERSATION,
            ToolType.TERMINAL,
            ToolType.FILESYSTEM,
            ToolType.UI
        }

    def can_verify(self) -> bool:
        return True

    def can_replan(self) -> bool:
        return True

    def get_max_iterations(self) -> int:
        return 4
