"""Node for handling user interaction."""

import os
from typing import Dict

from llama_index.llms.openai import OpenAI

# Import the CloudPilotState type
from src.main import CloudPilotState


def user_interaction(state: CloudPilotState) -> CloudPilotState:
    """
    Handle user interaction and determine the next action to take.
    
    Args:
        state: The current state of the graph
        
    Returns:
        Updated state with next action
    """
    # Create a copy of the state to modify
    new_state = state.copy()
    
    try:
        # Display the current state to the user
        print("\n" + "="*50)
        print("Cloud Pilot - Terraform Agent")
        print("="*50)
        
        # Display the current task
        print(f"\nCurrent Task: {state['task']}")
        
        # Display the result of the last operation, if any
        if state["result"]:
            print("\nResult:")
            print(state["result"])
        
        # Display any errors
        if state["error"]:
            print("\nError:")
            print(state["error"])
        
        # Get user input
        print("\nWhat would you like to do next?")
        print("1. Analyze Terraform code")
        print("2. Generate/modify Terraform code")
        print("3. Execute Terraform commands")
        print("4. Perform file system operations")
        print("5. Change the current task")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ")
        
        if choice == "1":
            # Analyze Terraform code
            new_state["next_action"] = "analyze"
            
            # If there's no terraform file path, ask for one
            if not state["terraform_file_path"]:
                file_path = input("Enter the path to the Terraform file: ")
                new_state["terraform_file_path"] = file_path
        
        elif choice == "2":
            # Generate/modify Terraform code
            new_state["next_action"] = "generate"
            
            # If there's a current task, confirm or update it
            current_task = state["task"]
            print(f"\nCurrent task: {current_task}")
            update_task = input("Would you like to update the task? (y/n): ")
            
            if update_task.lower() == "y":
                new_task = input("Enter the new task: ")
                new_state["task"] = new_task
        
        elif choice == "3":
            # Execute Terraform commands
            new_state["next_action"] = "execute"
            
            # If there's no terraform file path, ask for one
            if not state["terraform_file_path"]:
                file_path = input("Enter the path to the Terraform file: ")
                new_state["terraform_file_path"] = file_path
        
        elif choice == "4":
            # Perform file system operations
            new_state["next_action"] = "file_ops"
            
            # Get the file system operation to perform
            operation = input("Describe the file operation you want to perform: ")
            new_state["user_input"] = operation
        
        elif choice == "5":
            # Change the current task
            new_task = input("Enter the new task: ")
            new_state["task"] = new_task
            
            # Ask for the next action
            print("\nWhat would you like to do with this new task?")
            print("1. Analyze existing Terraform code")
            print("2. Generate new Terraform code")
            
            next_action = input("Enter your choice (1-2): ")
            
            if next_action == "1":
                new_state["next_action"] = "analyze"
                file_path = input("Enter the path to the Terraform file: ")
                new_state["terraform_file_path"] = file_path
            else:
                new_state["next_action"] = "generate"
                # Clear existing terraform code to generate fresh code
                new_state["terraform_code"] = ""
        
        elif choice == "6":
            # Exit
            new_state["next_action"] = "end"
            print("\nExiting Cloud Pilot. Goodbye!")
        
        else:
            # Invalid choice
            print("\nInvalid choice. Please try again.")
            # Keep the current next_action
            new_state["next_action"] = state["next_action"]
        
    except Exception as e:
        new_state["error"] = f"Error in user interaction: {str(e)}"
        # Default to user interaction again
        new_state["next_action"] = state["next_action"]
    
    return new_state 