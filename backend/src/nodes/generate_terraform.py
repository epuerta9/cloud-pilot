"""Node for generating Terraform code."""

import os
from typing import Dict

from llama_index.llms.openai import OpenAI
from llama_index.core import Settings

# Import the CloudPilotState type
from src.state import CloudPilotState


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
        # Initialize the LLM
        llm = OpenAI(model="gpt-4")
        
        # Prepare the prompt based on whether we're creating new code or modifying existing code
        if state["terraform_code"]:
            # We're modifying existing code
            prompt = f"""
            Modify the following Terraform code based on this task: {state["task"]}
            
            Current Terraform code:
            ```
            {state["terraform_code"]}
            ```
            
            If there was an analysis result, consider it: {state["result"]}
            
            Return only the modified Terraform code, no explanations.
            """
        else:
            # We're creating new code
            prompt = f"""
            Generate Terraform code for the following task: {state["task"]}
            
            Return only the Terraform code, no explanations.
            """
        
        # Generate the Terraform code
        response = llm.complete(prompt)
        
        # Extract the code from the response
        terraform_code = response.text
        
        # Clean up the code (remove markdown code blocks if present)
        if terraform_code.startswith("```") and terraform_code.endswith("```"):
            terraform_code = terraform_code.split("```")[1]
            if terraform_code.startswith("terraform") or terraform_code.startswith("hcl"):
                terraform_code = terraform_code[terraform_code.find("\n")+1:]
        
        # Update the state with the generated code
        new_state["terraform_code"] = terraform_code
        
        # If there's no file path yet, create one
        if not state["terraform_file_path"]:
            # Create a directory for the Terraform files if it doesn't exist
            os.makedirs("terraform", exist_ok=True)
            new_state["terraform_file_path"] = "terraform/main.tf"
        
        # Write the code to the file
        with open(new_state["terraform_file_path"], "w") as f:
            f.write(terraform_code)
        
        new_state["result"] = f"Terraform code generated and saved to {new_state['terraform_file_path']}"
        new_state["error"] = ""
        
    except Exception as e:
        new_state["error"] = f"Error generating Terraform code: {str(e)}"
    
    return new_state 