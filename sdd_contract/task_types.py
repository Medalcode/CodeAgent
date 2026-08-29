"""
Core domain types for SDD Contract system.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any


class TaskType(Enum):
    """Task classification types."""
    CHAT = "CHAT"
    ACTION = "ACTION"
    FEATURE = "FEATURE"
    RECOVERY = "RECOVERY"


class VerificationState(Enum):
    """Verification result states."""
    PASS = "PASS"
    NOT_REQUIRED = "NOT_REQUIRED"
    FAIL = "FAIL"
    ERROR = "ERROR"


class ToolType(Enum):
    """Tool categorization for policy enforcement."""
    FILESYSTEM = "filesystem"
    TERMINAL = "terminal"
    VERIFICATION = "verification"
    REPLANNING = "replanning"
    CONVERSATION = "conversation"
    UI = "ui"
    TEST_RUNNER = "test_runner"
    DEBUGGER = "debugger"


@dataclass
class TaskClassification:
    """Result of task classification."""
    task_type: TaskType
    confidence: float
    classification_reason: str
    metadata: dict[str, Any]
