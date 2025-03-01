"""Node for generating infrastructure code."""

import os
from typing import Dict

from llama_index.llms.openai import OpenAI
from llama_index.core import Settings

# Import the CloudPilotState type and agents
from src.state import CloudPilotState
from src.agents.interpreter_agent import InterpreterAgent
from src.agents.tf_generator_agent import TerraformGeneratorAgent


def generate_terraform(state: CloudPilotState) -> CloudPilotState:
    """
    Generate infrastructure code based on the task description.
    Uses Terraform for infrastructure as code.
    
    Args:
        state: The current state of the graph
        
    Returns:
        Updated state with generated infrastructure code
    """
    # Create a copy of the state to modify
    new_state = state.copy()
    
    try:
        # Initialize agents
        interpreter = InterpreterAgent()
        tf_generator = TerraformGeneratorAgent()
        
        # First, interpret the user's request into AWS services
        aws_specification = interpreter.interpret_request(state["task"])
        
        # Generate and validate Terraform code
        tf_code, tf_validation = tf_generator.generate_terraform(state["task"])
        
        # Update the state with the results
        new_state["terraform_code"] = tf_code
        new_state["terraform_file_path"] = os.path.join("terraform_prod", "main.tf")
        
        # Add sentinel to indicate Terraform was built
        new_state["terraform_built"] = True
        
        # Store results
        new_state["result"] = f"""
        Interpreted Request: {aws_specification}
        
        Terraform Output: {tf_validation}
        
        Generated file:
        - Terraform: {new_state["terraform_file_path"]}
        """
        
        # Set error if validation failed
        if "error" in tf_validation.lower() or "failed" in tf_validation.lower():
            new_state["error"] = "Validation failed. Check result for details."
            new_state["terraform_built"] = False
        else:
            new_state["error"] = ""
        
    except Exception as e:
        new_state["error"] = f"Error in generate_terraform: {str(e)}"
        new_state["terraform_built"] = False
    
    return new_state 