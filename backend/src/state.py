from typing import Any, Dict, Optional, TypedDict, List
from dataclasses import dataclass, field
from typing import Annotated
from langgraph.graph.message import add_messages



class CloudPilotState(TypedDict):
    """State for the Cloud Pilot graph."""

    messages: Annotated[list, add_messages]

    # The current task description
    task: str
    # The current CDK code
    cdk_code: str
    # The path to the CDK file
    cdk_file_path: str
    # The result of the last operation
    result: str
    # Any error messages
    error: str
    # User input/feedback
    user_input: str
    # Next action to take
    next_action: str 