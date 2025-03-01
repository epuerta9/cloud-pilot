"""Node for generating infrastructure code."""

import os
from typing import Dict

from llama_index.llms.openai import OpenAI
from llama_index.core import Settings

# Import the CloudPilotState type and agents
from src.state import CloudPilotState
from src.agents.interpreter_agent import InterpreterAgent
from src.agents.cdk_generator_agent import CDKGeneratorAgent


def generate_terraform(state: CloudPilotState) -> CloudPilotState:
    """
    Generate infrastructure code based on the task description.
    Uses CDK for infrastructure as code.
    
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
        cdk_generator = CDKGeneratorAgent()
        
        # First, interpret the user's request into AWS services
        aws_specification = interpreter.interpret_request(state["task"])
        
        # Generate and validate CDK code
        cdk_code, cdk_validation = cdk_generator.generate_cdk(aws_specification)
        
        # Update the state with the results
        new_state["cdk_code"] = cdk_code
        new_state["cdk_file_path"] = os.path.join("cdk_prod", "stack.py")
        
        # Store results
        new_state["result"] = f"""
        Interpreted Request: {aws_specification}
        
        CDK Validation: {cdk_validation}
        
        Generated file:
        - CDK: {new_state["cdk_file_path"]}
        """
        
        # Set error if validation failed
        if "valid" not in cdk_validation.lower():
            new_state["error"] = "Validation failed. Check result for details."
        else:
            new_state["error"] = ""
        
    except Exception as e:
        new_state["error"] = f"Error in generate_terraform: {str(e)}"
    
    return new_state 