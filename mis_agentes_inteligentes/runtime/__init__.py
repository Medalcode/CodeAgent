"""
Módulo de runtime autónomo y event bus para CodeAgent v6.0 Enterprise.
"""
from runtime.event_bus import EventBus, get_event_bus
from runtime.runtime import CodeAgentRuntime, get_runtime

__all__ = ["EventBus", "get_event_bus", "CodeAgentRuntime", "get_runtime"]
