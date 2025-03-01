"""Node for handling Terraform plan operations."""

import os
from typing import Dict
from pathlib import Path

from src.state import CloudPilotState
from src.agents.terraform_agent import TerraformAgent


def terraform_plan(state: CloudPilotState) -> CloudPilotState:
    """
    Create and save a Terraform plan for review.

    Args:
        state: The current state of the graph

    Returns:
        Updated state with plan results and next action
    """
    # Create a copy of the state to modify
    new_state = state.copy()

    try:
        # Initialize the Terraform agent
        tf_agent = TerraformAgent()

        # Check if we have a terraform file path
        if not state["terraform_file_path"]:
            new_state["error"] = "No Terraform file path specified"
            new_state["next_action"] = "user_interaction"
            return new_state

        # Verify the file exists
        if not os.path.exists(state["terraform_file_path"]):
            new_state["error"] = f"Terraform file not found: {state['terraform_file_path']}"
            new_state["next_action"] = "user_interaction"
            return new_state

        # Get the directory containing the Terraform file
        terraform_dir = os.path.dirname(state["terraform_file_path"])

        # Generate the plan file path with .plan.out.tf suffix
        plan_file = os.path.join(terraform_dir, "terraform.plan.out.tf")

        # Run terraform plan and save to file
        plan_result = tf_agent.terraform_plan(terraform_dir)

        if "Error:" in plan_result:
            new_state["error"] = plan_result
            new_state["next_action"] = "user_interaction"
            return new_state

        # Save the plan to file
        try:
            with open(plan_file, "w") as f:
                f.write(plan_result)
            new_state["result"] = f"Terraform plan created and saved to {plan_file}\n\nPlan Output:\n{plan_result}"
        except Exception as e:
            new_state["error"] = f"Error saving plan file: {str(e)}"
            new_state["next_action"] = "user_interaction"
            return new_state

        # Set next action to wait for plan approval
        new_state["next_action"] = "plan_approval"

    except Exception as e:
        new_state["error"] = f"Error in terraform plan: {str(e)}"
        new_state["next_action"] = "user_interaction"

    return new_state