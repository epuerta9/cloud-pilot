from typing import Any, Dict, Optional, TypedDict
from dataclasses import dataclass, field

@dataclass
class CloudPilotState:
    """State object for the Cloud Pilot application."""
    # Add whatever fields were in the original CloudPilotState
    messages: list[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    # Add other fields as needed 

class CloudPilotState(TypedDict):
    """State for the Cloud Pilot graph."""
    # The current task description
    task: str
    # The current terraform code
    terraform_code: str
    # The path to the terraform file
    terraform_file_path: str
    # The result of the last operation
    result: str
    # Any error messages
    error: str
    # User input/feedback
    user_input: str
    # Next action to take
    next_action: str 