"""Node for capturing Terraform state after execution."""

import os
import json
import subprocess
from typing import Dict

from src.state import CloudPilotState

def terraform_show(state: CloudPilotState) -> CloudPilotState:
    """
    Capture the current state of Terraform resources after execution.

    Args:
        state: The current state of the application

    Returns:
        Updated state with the show result
    """
    # Create a copy of the state to modify
    new_state = state.copy()

    try:
        # Get absolute paths
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_dir = os.path.join(project_root, "terraform_prod")

        # Run terraform show with -json flag
        show_result = subprocess.run(
            ["terraform", "-chdir=" + output_dir, "show", "-json"],
            capture_output=True,
            text=True
        )

        if show_result.returncode != 0:
            new_state["error"] = f"Terraform show failed: {show_result.stderr}"
            return new_state

        # Save the show output to file
        show_json_path = os.path.join(output_dir, "show.json")
        try:
            with open(show_json_path, "w") as f:
                f.write(show_result.stdout)
        except Exception as e:
            new_state["error"] = f"Error saving show JSON: {str(e)}"
            return new_state

        # Parse and store the show result in state
        try:
            show_data = json.loads(show_result.stdout)
            new_state["terraform_json"] = show_data
            new_state["result"] = "Terraform show completed and saved to show.json"
        except json.JSONDecodeError as e:
            new_state["error"] = f"Error parsing show output: {str(e)}"

    except Exception as e:
        new_state["error"] = f"Error in terraform_show: {str(e)}"

    return new_state