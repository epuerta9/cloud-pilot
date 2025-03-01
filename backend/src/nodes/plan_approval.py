"""Node for handling approval of Terraform plans."""

import os
from typing import Dict

from src.state import CloudPilotState


def plan_approval(state: CloudPilotState) -> CloudPilotState:
    """
    Handle approval for Terraform plans.

    Args:
        state: The current state of the graph

    Returns:
        Updated state with approval decision
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
            new_state["next_action"] = "user_interaction"
            return new_state

        # Get user approval
        print("\nDo you want to:")
        print("1. Apply the Terraform plan")
        print("2. Reject the plan and modify")
        print("3. Cancel and return to main menu")

        choice = input("\nEnter your choice (1-3): ")

        if choice == "1":
            # Proceed with terraform apply
            new_state["next_action"] = "execute_terraform"
        elif choice == "2":
            # Return to generate terraform for modifications
            new_state["next_action"] = "generate_terraform"
            new_state["user_input"] = "modify"  # Signal that we're modifying existing code
        else:
            # Return to main menu
            new_state["next_action"] = "user_interaction"

    except Exception as e:
        new_state["error"] = f"Error in plan approval: {str(e)}"
        new_state["next_action"] = "user_interaction"

    return new_state