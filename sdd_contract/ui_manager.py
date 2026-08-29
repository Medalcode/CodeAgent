"""
UI Manager for enforcing single-instance policy.
"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class UIState(Enum):
    """State of a UI instance."""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    TERMINATED = "TERMINATED"


@dataclass
class UIInstance:
    """Represents a UI instance."""
    id: str
    state: UIState
    type: str
    session_id: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "state": self.state.value,
            "type": self.type,
            "session_id": self.session_id
        }


class UIManager:
    """Manages UI lifecycle with single-instance policy."""
    
    def __init__(self):
        self.instance: Optional[UIInstance] = None
        self.max_instances = 1
    
    def create_instance(self, session_id: str, ui_type: str) -> UIInstance:
        """
        Create a new UI instance.
        
        Args:
            session_id: The current session ID
            ui_type: Type of UI to create
            
        Returns:
            The created UI instance
            
        Raises:
            ValueError: If max instances would be exceeded
        """
        if self.instance is not None:
            if self.instance.state == UIState.CLOSED:
                # Close old instance, create new
                self.instance.state = UIState.TERMINATED
                self.instance = self._create_internal(session_id, ui_type)
            else:
                raise ValueError("UI instance already exists for this session")
        else:
            self.instance = self._create_internal(session_id, ui_type)
        
        return self.instance
    
    def update_instance(self, ui_instance: UIInstance) -> None:
        """
        Update an existing UI instance.
        Does NOT create new instances.
        
        Args:
            ui_instance: Updated UI instance data
            
        Raises:
            ValueError: If no UI instance exists
        """
        if self.instance is None:
            raise ValueError("No UI instance exists for session")
        
        self.instance.state = ui_instance.state
        self.instance.type = ui_instance.type
    
    def close_instance(self) -> None:
        """Mark the UI instance as closed."""
        if self.instance:
            self.instance.state = UIState.CLOSED
    
    def terminate_session(self) -> None:
        """Mark the session as terminated."""
        if self.instance:
            self.instance.state = UIState.TERMINATED
            self.instance = None
    
    def get_instance(self) -> Optional[UIInstance]:
        """Get the current UI instance."""
        return self.instance
    
    def _create_internal(self, session_id: str, ui_type: str) -> UIInstance:
        """Internal method to create UI instance."""
        # In a real implementation, this would create the actual UI
        # For now, just return a placeholder
        return UIInstance(
            id=f"ui-{session_id[:8]}",
            state=UIState.OPEN,
            type=ui_type,
            session_id=session_id
        )
