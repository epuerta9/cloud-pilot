"""Node for handling Terraform plan operations."""

import os
import subprocess
from typing import Dict

from src.state import CloudPilotState
from src.constants import ACTION_USER_INTERACTION, ACTION_APPROVE_PLAN

def terraform_plan(state: CloudPilotState) -> CloudPilotState:
    """
    Create a Terraform plan.

    Args:
        state: The current state of the application

    Returns:
        Updated state with the plan result
    """
    # Create a copy of the state to modify
    new_state = state.copy()

    try:
        # Check if we have a terraform file path
        if not new_state.get("terraform_file_path"):
            new_state["error"] = "No Terraform file path provided"
            new_state["next_action"] = ACTION_USER_INTERACTION
            return new_state

        # Change to the directory containing the Terraform file
        terraform_dir = os.path.dirname(new_state["terraform_file_path"])
        if not terraform_dir:
            terraform_dir = "."

        try:
            os.chdir(terraform_dir)
        except Exception as e:
            new_state["error"] = f"Failed to change to directory {terraform_dir}: {str(e)}"
            new_state["next_action"] = ACTION_USER_INTERACTION
            return new_state

        # Initialize Terraform if needed
        try:
            subprocess.run(["terraform", "init"], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            new_state["error"] = f"Terraform init failed: {e.stderr.decode()}"
            new_state["next_action"] = ACTION_USER_INTERACTION
            return new_state

        # Create the plan
        try:
            result = subprocess.run(
                ["terraform", "plan", "-no-color"],
                check=True,
                capture_output=True,
                text=True
            )
            new_state["result"] = result.stdout
            new_state["next_action"] = ACTION_APPROVE_PLAN

        except subprocess.CalledProcessError as e:
            new_state["error"] = f"Terraform plan failed: {e.stderr}"
            new_state["next_action"] = ACTION_USER_INTERACTION
            return new_state

    except Exception as e:
        new_state["error"] = f"Error in terraform_plan: {str(e)}"
        new_state["next_action"] = ACTION_USER_INTERACTION

    return new_state