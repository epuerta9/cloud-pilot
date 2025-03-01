"""Node for generating infrastructure code."""

import os
import json
import subprocess
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

    # Get absolute paths
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output_dir = os.path.join(project_root, "terraform_prod")

    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Initialize agents
        interpreter = InterpreterAgent()
        tf_generator = TerraformGeneratorAgent()

        print(f"State: {state['messages']}")

        # Get AWS specification from messages
        aws_specification = " ".join([message.content for message in state["messages"]])

        # Generate Terraform code
        tf_code = tf_generator.generate_code(aws_specification)

        # Write the generated code to main.tf
        with open(os.path.join(output_dir, "main.tf"), "w") as f:
            f.write(tf_code)
            f.flush()
            os.fsync(f.fileno())

        # Run terraform init with -chdir
        init_result = subprocess.run(
            ["terraform", "-chdir=" + output_dir, "init"],
            capture_output=True,
            text=True
        )
        print(init_result.stdout)
        if init_result.stderr:
            print("Init Errors:", init_result.stderr)

        # Run terraform plan with -chdir and save to file
        plan_result = subprocess.run(
            ["terraform", "-chdir=" + output_dir, "plan", "-out=tfplan"],
            capture_output=True,
            text=True
        )
        print(plan_result.stdout)
        if plan_result.stderr:
            print("Plan Errors:", plan_result.stderr)

        # Convert plan to JSON using -chdir
        show_result = subprocess.run(
            ["terraform", "-chdir=" + output_dir, "show", "-json", "tfplan"],
            capture_output=True,
            text=True
        )

        # Save JSON plan to file
        plan_json_path = os.path.join(output_dir, "plan.json")
        try:
            with open(plan_json_path, "w") as f:
                f.write(show_result.stdout)
        except Exception as e:
            print(f"Error saving plan JSON: {str(e)}")

        # Load the plan JSON if it exists
        plan_data = None
        if os.path.exists(plan_json_path):
            try:
                with open(plan_json_path, 'r') as f:
                    plan_data = json.load(f)
            except Exception as e:
                print(f"Error loading plan JSON: {str(e)}")

        # Update the state with the results using absolute paths
        new_state["terraform_code"] = tf_code
        new_state["terraform_file_path"] = os.path.join(output_dir, "main.tf")
        new_state["terraform_json"] = plan_data

        # Add sentinel to indicate Terraform was built
        new_state["terraform_built"] = True

        # Store results with validation output
        validation_output = f"""
        Init Output:
        {init_result.stdout}
        {init_result.stderr if init_result.stderr else ''}

        Plan Output:
        {plan_result.stdout}
        {plan_result.stderr if plan_result.stderr else ''}
        """

        new_state["result"] = f"""
        Terraform Output: {validation_output}

        Generated files:
        - Terraform: {new_state["terraform_file_path"]}
        - Plan JSON: {plan_json_path if plan_data else "Not available"}

        Plan Summary:
        {json.dumps(plan_data["planned_values"], indent=2) if plan_data else "No plan data available"}
        """

        # Set error if validation failed
        if plan_result.returncode != 0:
            new_state["error"] = "Plan failed. Check result for details."
            new_state["terraform_built"] = False
        else:
            new_state["error"] = ""

    except Exception as e:
        new_state["error"] = f"Error in generate_terraform: {str(e)}"
        new_state["terraform_built"] = False

    return new_state