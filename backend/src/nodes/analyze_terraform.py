"""Node for analyzing Terraform code."""

import os
from typing import Dict

from llama_index.llms.anthropic import Anthropic
from llama_index.core import Settings

# Import the CloudPilotState type
from src.state import CloudPilotState
from src.constants import ANTHROPIC_MODEL

def analyze_terraform(state: CloudPilotState) -> CloudPilotState:
    """
    Analyze Terraform code to understand its purpose and structure.

    Args:
        state: The current state of the graph

    Returns:
        Updated state with analysis results
    """
    # Create a copy of the state to modify
    new_state = state.copy()

    try:
        # If there's no terraform code but there's a file path, read the file
        if not state["terraform_code"] and state["terraform_file_path"]:
            if os.path.exists(state["terraform_file_path"]):
                with open(state["terraform_file_path"], "r") as f:
                    new_state["terraform_code"] = f.read()
            else:
                new_state["error"] = f"File not found: {state['terraform_file_path']}"
                return new_state

        # If there's still no terraform code, return an error
        if not new_state["terraform_code"]:
            new_state["error"] = "No Terraform code to analyze"
            return new_state

        # Initialize the LLM
        llm = Anthropic(model=ANTHROPIC_MODEL)

        # Analyze the Terraform code
        prompt = f"""
        Analyze the following Terraform code and provide a summary of:
        1. Resources being created
        2. Configuration details
        3. Potential issues or improvements

        Terraform code:
        ```
        {new_state["terraform_code"]}
        ```
        """

        response = llm.complete(prompt)

        # Update the state with the analysis result
        new_state["result"] = response.text
        new_state["error"] = ""

    except Exception as e:
        new_state["error"] = f"Error analyzing Terraform code: {str(e)}"

    return new_state