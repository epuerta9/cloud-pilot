"""Node for handling Terraform plan approval."""

import os
from typing import Dict

from src.state import CloudPilotState
from src.constants import (
    ACTION_USER_INTERACTION, ACTION_EXECUTE, ACTION_GENERATE
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

        # Get user approval
        print("\nWhat would you like to do?")
        print("1. Apply the plan")
        print("2. Modify the code")
        print("3. Cancel")

        choice = input("\nEnter your choice (1-3): ")

        if choice == "1":
            # Proceed with terraform apply
            new_state["next_action"] = ACTION_EXECUTE
        elif choice == "2":
            # Return to generate terraform for modifications
            new_state["next_action"] = ACTION_GENERATE
            new_state["user_input"] = "modify"  # Signal that we're modifying existing code
        else:
            # Return to main menu
            new_state["next_action"] = ACTION_USER_INTERACTION

    except Exception as e:
        new_state["error"] = f"Error in plan approval: {str(e)}"
        new_state["next_action"] = ACTION_USER_INTERACTION

    return new_state