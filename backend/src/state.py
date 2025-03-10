from typing import TypedDict, List
from typing_extensions import NotRequired
from langgraph.graph.message import add_messages


class CloudPilotState(TypedDict):
    """State for the Cloud Pilot graph."""

    # Messages list with add_messages reducer
    messages: List[str]

    # The current task description
    task: str

    # The current Terraform code
    terraform_code: str

    # The current Terraform json
    terraform_json: str

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