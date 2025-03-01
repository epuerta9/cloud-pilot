"""Node for executing Terraform commands."""

import os
import subprocess
from typing import Dict

# Import the CloudPilotState type
from src.state import CloudPilotState
from src.constants import ACTION_USER_INTERACTION


def execute_terraform(state: CloudPilotState) -> CloudPilotState:
    """
    Execute Terraform commands on the generated code.

    Args:
        state: The current state of the graph

    Returns:
        Updated state with execution results
    """
    # Create a copy of the state to modify
    new_state = state.copy()

    try:
        # Check if we have a terraform file path
        if not state["terraform_file_path"]:
            new_state["error"] = "No Terraform file path specified"
            new_state["next_action"] = ACTION_USER_INTERACTION
            return new_state

        # Check if the file exists
        # if not os.path.exists(state["terraform_file_path"]):
        #     new_state["error"] = f"Terraform file not found: {state['terraform_file_path']}"
        #     new_state["next_action"] = ACTION_USER_INTERACTION
        #     return new_state

        # Get the directory containing the Terraform file
        terraform_dir = os.path.dirname(state["terraform_file_path"])
        print(f"Terraform directory: {terraform_dir}")
        try:
            # # Initialize Terraform
            # init_result = subprocess.run(
            #     ["terraform", "init"],
            #     capture_output=True,
            #     text=True,
            #     check=True
            # )

            # Run Terraform apply
            print("Running Terraform apply")
            apply_result = subprocess.run(
                ["terraform", "apply", "-auto-approve",],
                capture_output=True,
                text=True,
                check=True
            )
            print("Terraform apply completed")
            # Update the state with the execution results
            new_state["result"] = apply_result.stdout
            new_state["error"] = ""

        except subprocess.CalledProcessError as e:
            if "init" in str(e.cmd):
                new_state["error"] = f"Terraform initialization failed: {e.stderr}"
            else:
                new_state["error"] = f"Terraform apply failed: {e.stderr}"
        #finally:
            # Change back to the original directory
            # os.chdir(original_dir)

    except Exception as e:
        new_state["error"] = f"Error executing Terraform: {str(e)}"

    # Always set next_action to user_interaction when done
    new_state["next_action"] = ACTION_USER_INTERACTION
    return new_state