"""Node for generating Terraform code."""

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
    Generate or modify Terraform code based on the task description.
    
    Args:
        state: The current state of the graph
        
    Returns:
        Updated state with generated Terraform code
    """
    # Create a copy of the state to modify
    new_state = state.copy()
    
    try:
        # Initialize agents
        interpreter = InterpreterAgent()
        tf_generator = TerraformGeneratorAgent()
        
        # First, interpret the user's request into AWS services
        aws_specification = interpreter.interpret_request(state["task"])
        
        # Initialize the Terraform workspace
        tf_generator.initialize_workspace()
        
        # Store the interpreted specification in the result
        new_state["result"] = f"Interpreted Request: {aws_specification}"
        new_state["error"] = ""
        
        # We'll continue with the rest of the tf_generator functionality
        # in the next steps...
        
    except Exception as e:
        new_state["error"] = f"Error in generate_terraform: {str(e)}"
    
    return new_state 