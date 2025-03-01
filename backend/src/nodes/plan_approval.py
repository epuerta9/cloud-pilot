"""Node for handling Terraform plan approval."""

import os
from typing import Dict, Literal
from langgraph.types import Command, interrupt

from src.state import CloudPilotState
from src.constants import (
    ACTION_USER_INTERACTION, ACTION_EXECUTE, ACTION_GENERATE,
    NODE_EXECUTE_TERRAFORM, NODE_GENERATE_TERRAFORM, NODE_USER_INTERACTION
)


def plan_approval(state: CloudPilotState) -> CloudPilotState:
    """
    Handle the approval or rejection of a Terraform plan.

    Args:
        state: The current state of the application

    Returns:
        Updated state with the next action based on user's decision
    """
    # Create a copy of the state to modify
    new_state = state.copy()

    try:
        print("\n" + "="*50)
        print("Terraform Plan Review")
        print("="*50)

        # Display the current plan result
        if state["result"]:
            print("\nPlan Summary:")
            print(state["result"])

        # Display any errors
        if state["error"]:
            print("\nErrors:")
            print(state["error"])
            new_state["next_action"] = ACTION_USER_INTERACTION
            return new_state

        # Interrupt the graph to get user feedback
        return interrupt(
            "plan_approval",
            "What would you like to do?\n1. Apply the plan\n2. Modify the code\n3. Cancel",
            new_state
        )

    except Exception as e:
        new_state["error"] = f"Error in plan approval: {str(e)}"
        new_state["next_action"] = ACTION_USER_INTERACTION
        return new_state


def handle_plan_feedback(state: CloudPilotState) -> Literal["execute", "generate", "user_interaction"]:
    """
    Handle the user's feedback on the plan and determine the next node.

    Args:
        state: The current state of the application

    Returns:
        The name of the next node to execute
    """
    # Get the user's choice from the feedback
    choice = state.get("user_input", "")

    if choice == "1":
        # Proceed with terraform apply
        state["next_action"] = ACTION_EXECUTE
        return NODE_EXECUTE_TERRAFORM
    elif choice == "2":
        # Return to generate terraform for modifications
        state["next_action"] = ACTION_GENERATE
        state["user_input"] = "modify"  # Signal that we're modifying existing code
        return NODE_GENERATE_TERRAFORM
    else:
        # Return to main menu
        state["next_action"] = ACTION_USER_INTERACTION
        return NODE_USER_INTERACTION