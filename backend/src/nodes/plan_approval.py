"""Node for handling Terraform plan approval."""

from typing import Literal
from langgraph.types import interrupt, Command
from src.state import CloudPilotState
from src.constants import ACTION_EXECUTE, ACTION_GENERATE, ACTION_USER_INTERACTION

def plan_approval(state: CloudPilotState) -> Command[Literal["execute_terraform", "generate_terraform"]]:
    is_approved = interrupt(
        {
            "question": "Is this correct?",
            # Surface the output that should be
            # reviewed and approved by the human.
            "llm_output": state.get("result")
        }
    )
    print(is_approved)
    if is_approved:
        print("yes")
        return Command(goto="execute_terraform")
    else:
        print("no")
        return Command(goto="generate_terraform")

def plan_approval2(state: CloudPilotState) -> CloudPilotState:
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

        # Return state with interrupt for user feedback
        return interrupt(
            {
                "question": "Is this correct?",
                "plan_output": state["result"],
                "terraform_code": state["terraform_code"]
            }
        )

    except Exception as e:
        new_state["error"] = f"Error in plan approval: {str(e)}"
        new_state["next_action"] = ACTION_USER_INTERACTION
        return new_state


def handle_plan_feedback(state: CloudPilotState) -> Literal['execute', 'generate', 'user_interaction']:
    """
    Handle the user's feedback on the Terraform plan.

    Args:
        state: The current state containing the user's feedback

    Returns:
        The next action to take based on the feedback
    """
    try:
        # Get user's decision
        is_approved = input("\nDo you want to apply this plan? (yes/no): ").lower().startswith('y')

        if is_approved:
            return ACTION_EXECUTE
        else:
            return ACTION_GENERATE

    except Exception as e:
        print(f"Error handling feedback: {str(e)}")
        return ACTION_USER_INTERACTION