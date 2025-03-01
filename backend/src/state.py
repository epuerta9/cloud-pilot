from typing import TypedDict, Annotated
from typing_extensions import NotRequired

def add_messages(messages: list) -> list:
    """Add messages to the state."""
    return messages

class CloudPilotState(TypedDict):
    """State for the Cloud Pilot graph."""

    messages: Annotated[list, add_messages]

    # The current task description
    task: str
    
    # The current Terraform code
    terraform_code: str
    
    # The path to the Terraform file
    terraform_file_path: str
    
    # Sentinel to track if Terraform was built successfully
    terraform_built: NotRequired[bool]
    
    # The result of the last operation
    result: str
    
    # Any error messages
    error: str
    
    # User input/feedback
    user_input: str
    
    # Next action to take
    next_action: str 