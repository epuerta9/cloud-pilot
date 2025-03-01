"""Node for executing Terraform commands."""

import os
import subprocess
from typing import Dict

# Import the CloudPilotState type
from src.main import CloudPilotState


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
            return new_state
        
        # Check if the file exists
        if not os.path.exists(state["terraform_file_path"]):
            new_state["error"] = f"Terraform file not found: {state['terraform_file_path']}"
            return new_state
        
        # Get the directory containing the Terraform file
        terraform_dir = os.path.dirname(state["terraform_file_path"])
        
        # Change to the directory containing the Terraform file
        original_dir = os.getcwd()
        os.chdir(terraform_dir)
        
        # Initialize Terraform
        init_result = subprocess.run(
            ["terraform", "init"],
            capture_output=True,
            text=True
        )
        
        # Check if initialization was successful
        if init_result.returncode != 0:
            new_state["error"] = f"Terraform initialization failed: {init_result.stderr}"
            os.chdir(original_dir)
            return new_state
        
        # Run Terraform plan
        plan_result = subprocess.run(
            ["terraform", "plan", "-no-color"],
            capture_output=True,
            text=True
        )
        
        # Change back to the original directory
        os.chdir(original_dir)
        
        # Update the state with the execution results
        new_state["result"] = f"Terraform initialization successful.\n\nTerraform plan output:\n{plan_result.stdout}"
        
        # If there was an error in the plan, add it to the result
        if plan_result.returncode != 0:
            new_state["error"] = f"Terraform plan failed: {plan_result.stderr}"
        else:
            new_state["error"] = ""
        
    except Exception as e:
        new_state["error"] = f"Error executing Terraform: {str(e)}"
    
    return new_state 