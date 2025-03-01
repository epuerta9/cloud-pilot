"""User interaction node for the Cloud Pilot application."""

import os
from typing import Dict
from pathlib import Path

from llama_index.llms.openai import OpenAI

# Import the CloudPilotState type
from src.state import CloudPilotState
from src.constants import (
    ACTION_ANALYZE, ACTION_GENERATE, ACTION_EXECUTE, ACTION_FILE_OPS,
    ACTION_PLAN, ACTION_USER_INTERACTION, ACTION_END
)


def user_interaction(state: CloudPilotState) -> CloudPilotState:
    """
    Handle user interaction and determine the next action to take.

    Args:
        state: The current state of the graph

    Returns:
        Updated state with next action
    """
    # Create a new state to avoid modifying the input
    new_state = state.copy()

    # If there's an error, display it and clear it
    if new_state.get("error"):
        print(f"Error: {new_state['error']}")
        new_state["error"] = ""

    # If there's a result, display it and clear it
    if new_state.get("result"):
        print(f"Result: {new_state['result']}")
        new_state["result"] = ""

    # If there's a task, display it
    if new_state.get("task"):
        print(f"\nCurrent task: {new_state['task']}")

    # If there's terraform code, display it
    if new_state.get("terraform_code"):
        print("\nCurrent Terraform code:")
        print(new_state["terraform_code"])

    # Get user input based on the current state
    if not new_state.get("task"):
        # If there's no task, ask for one
        task = input("\nWhat would you like to do? ")
        new_state["task"] = task
        new_state["next_action"] = ACTION_ANALYZE

    elif not new_state.get("terraform_code"):
        # If there's no terraform code, ask what to do
        print("\nWhat would you like to do?")
        print("1. Analyze existing code")
        print("2. Generate new code")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ")

        if choice == "1":
            # Get the path to the terraform code
            path = input("\nEnter the path to your Terraform code: ")
            new_state["terraform_file_path"] = path
            new_state["next_action"] = ACTION_ANALYZE

        elif choice == "2":
            new_state["next_action"] = ACTION_GENERATE

        else:
            new_state["next_action"] = ACTION_END

    else:
        # If we have both a task and terraform code, show the menu
        print("\nWhat would you like to do?")
        print("1. Plan changes")
        print("2. Generate new code")
        print("3. Execute changes")
        print("4. File operations")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            new_state["next_action"] = ACTION_PLAN
        elif choice == "2":
            new_state["next_action"] = ACTION_GENERATE
        elif choice == "3":
            new_state["next_action"] = ACTION_EXECUTE
        elif choice == "4":
            new_state["next_action"] = ACTION_FILE_OPS
        else:
            new_state["next_action"] = ACTION_END

    return new_state