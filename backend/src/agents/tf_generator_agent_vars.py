"""Generator agent for creating Terraform configurations."""

import os
import subprocess
import json
from typing import Tuple, Dict, Any
from llama_index.llms.anthropic import Anthropic
from src.constants import ANTHROPIC_MODEL

class TerraformGeneratorAgent:
    """Agent for generating and managing Terraform configurations."""

    def __init__(self, model_name: str = ANTHROPIC_MODEL):
        """Initialize the Terraform generator agent."""
        self.terraform_dir = "./terraform"
        self.existing_files = {}
        # Configure Anthropic with max tokens and a higher temperature for more complete responses
        self.llm = Anthropic(
            model=model_name,
            max_tokens=4096,  # Ensure we get complete responses
            temperature=0.7   # Slightly higher temperature for more complete generations
        )

    def initialize_workspace(self) -> None:
        """
        Initialize the Terraform workspace by creating the directory
        and reading any existing files.
        """
        # Create terraform directory if it doesn't exist
        if not os.path.exists(self.terraform_dir):
            os.makedirs(self.terraform_dir)

        # Read all existing .tf files into memory
        self.existing_files = {}
        for file in os.listdir(self.terraform_dir):
            if file.endswith('.tf'):
                file_path = os.path.join(self.terraform_dir, file)
                with open(file_path, 'r') as f:
                    self.existing_files[file] = f.read()

    def validate_code(self, code: str) -> bool:
        """Validate the generated Terraform code for common syntax errors."""
        # Check for incomplete statements
        if code.count('{') != code.count('}'):
            return False
        if code.count('[') != code.count(']'):
            return False
        if code.count('(') != code.count(')'):
            return False

        # Check for incomplete blocks
        if code.endswith('resource') or code.endswith('variable') or code.endswith('provider'):
            return False

        # Check for incomplete resource blocks
        if 'resource "' in code and not code.strip().endswith('}'):
            return False

        return True

    def read_tfvars(self, output_dir: str) -> Dict[str, Any]:
        """Read existing tfvars file if it exists."""
        tfvars_path = os.path.join(output_dir, "terraform.tfvars")
        if os.path.exists(tfvars_path):
            with open(tfvars_path, 'r') as f:
                content = f.read()
                # Parse the HCL content into a dict
                # This is a simple parser, you might want to use a proper HCL parser
                vars_dict = {}
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"')
                            if value.lower() == 'true':
                                value = True
                            elif value.lower() == 'false':
                                value = False
                            elif value.isdigit():
                                value = int(value)
                            vars_dict[key] = value
                        except ValueError:
                            continue
                return vars_dict
        return {}

    def generate_tfvars(self, aws_specification: str, output_dir: str) -> Dict[str, Any]:
        """Generate tfvars based on AWS specification."""
        prompt = f"""Analyze this AWS infrastructure specification and generate appropriate Terraform variable values.
        
SPECIFICATION:
{aws_specification}

Generate a dictionary of Terraform variables that would create only the necessary resources.
Consider:
1. Whether VPC is needed
2. If web servers are required and if they need autoscaling
3. Storage requirements (S3)
4. Load balancer needs
5. Elastic Beanstalk requirements

Example format:
{{
    "create_vpc": true,
    "vpc_cidr": "10.0.0.0/16",
    "environment": "prod",
    "create_webserver": true,
    "use_autoscaling": true,
    "instance_type": "t2.micro",
    "min_size": 2,
    "max_size": 4,
    "create_s3": true,
    "bucket_name": "example-bucket",
    "create_alb": true,
    "create_beanstalk": false,
    "beanstalk_env": "example-env"
}}

Return ONLY the JSON dictionary, no other text.
"""
        response = self.llm.complete(prompt)
        try:
            return json.loads(response.text.strip())
        except json.JSONDecodeError:
            return {}

    def write_tfvars(self, vars_dict: Dict[str, Any], output_dir: str) -> None:
        """Write variables to tfvars file."""
        tfvars_content = []
        
        # Core infrastructure
        tfvars_content.extend([
            "# Core infrastructure",
            f'create_vpc = {str(vars_dict.get("create_vpc", True)).lower()}',
            f'vpc_cidr = "{vars_dict.get("vpc_cidr", "10.0.0.0/16")}"',
            f'environment = "{vars_dict.get("environment", "prod")}"',
            ""
        ])

        # Web server configuration
        tfvars_content.extend([
            "# Web server configuration",
            f'create_webserver = {str(vars_dict.get("create_webserver", True)).lower()}',
            f'use_autoscaling = {str(vars_dict.get("use_autoscaling", True)).lower()}',
            f'instance_type = "{vars_dict.get("instance_type", "t2.micro")}"',
            f'min_size = {vars_dict.get("min_size", 2)}',
            f'max_size = {vars_dict.get("max_size", 4)}',
            ""
        ])

        # Storage configuration
        tfvars_content.extend([
            "# Storage configuration",
            f'create_s3 = {str(vars_dict.get("create_s3", True)).lower()}',
            f'bucket_name = "{vars_dict.get("bucket_name", "my-cloudpilot-static-content")}"',
            ""
        ])

        # Load balancer configuration
        tfvars_content.extend([
            "# Load balancer configuration",
            f'create_alb = {str(vars_dict.get("create_alb", True)).lower()}',
            ""
        ])

        # Elastic Beanstalk configuration
        tfvars_content.extend([
            "# Elastic Beanstalk configuration",
            f'create_beanstalk = {str(vars_dict.get("create_beanstalk", False)).lower()}',
            f'beanstalk_env = "{vars_dict.get("beanstalk_env", "cloudpilot-nginx-prod")}"'
        ])

        # Write to file
        tfvars_path = os.path.join(output_dir, "terraform.tfvars")
        with open(tfvars_path, 'w') as f:
            f.write('\n'.join(tfvars_content))

    def generate_terraform(self, aws_specification: str, output_dir: str = "terraform_prod", retry_count: int = 0) -> Tuple[str, str]:
        """Generate Terraform configuration based on AWS specification."""
        if retry_count >= 4:
            return "", "Max retries reached - unable to generate valid Terraform configuration"

        # Generate or update tfvars
        existing_vars = self.read_tfvars(output_dir)
        new_vars = self.generate_tfvars(aws_specification, output_dir)
        
        # Merge existing and new vars, preferring new values
        final_vars = {**existing_vars, **new_vars}
        
        # Write updated tfvars
        self.write_tfvars(final_vars, output_dir)

        # Generate Terraform code
        prompt = """You are a Terraform code generator. Generate ONLY the complete, valid Terraform code.

SPECIFICATION:
""" + aws_specification + """

REQUIREMENTS:
1. Generate ONLY the complete Terraform file contents - no explanations or markdown
2. Use proper Terraform syntax and indentation (2 spaces)
3. Include proper closing brackets/braces
4. Follow AWS provider best practices
5. Use cloudpilot_ prefix for all resource names
6. Keep the implementation simple and focused
7. ALWAYS complete all blocks
8. ALWAYS close all braces and brackets
9. NEVER leave any blocks incomplete
10. ALWAYS use the following AMI ami-05b10e08d247fb927

IMPORTANT: Only generate resources that are enabled in the tfvars file.
"""

        # Generate the Terraform code
        response = self.llm.complete(prompt)
        print(f"\n=== Attempt {retry_count + 1} ===")

        # Get and validate the response text
        tf_code = response.text.strip()
        print(tf_code)

        # Additional validation for response completeness
        if not tf_code or len(tf_code) < 50:  # Basic length check
            print(f"\nResponse too short on attempt {retry_count + 1}, retrying...")
            return self.generate_terraform(
                aws_specification=aws_specification,
                output_dir=output_dir,
                retry_count=retry_count + 1
            )

        # Validate the generated code
        if not self.validate_code(tf_code):
            print(f"\nCode validation failed on attempt {retry_count + 1}, retrying...")
            return self.generate_terraform(
                aws_specification=aws_specification,
                output_dir=output_dir,
                retry_count=retry_count + 1
            )

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Write the generated code to main.tf with explicit file handling
        output_file = os.path.join(output_dir, "main.tf")
        try:
            with open(output_file, "w") as f:
                f.write(tf_code)
                f.flush()  # Explicitly flush the file
                os.fsync(f.fileno())  # Ensure it's written to disk
        except Exception as e:
            print(f"\nError writing file on attempt {retry_count + 1}: {str(e)}")
            return self.generate_terraform(
                aws_specification=aws_specification,
                output_dir=output_dir,
                retry_count=retry_count + 1
            )

        # Store current directory
        original_dir = os.getcwd()
        deployment_output = ""

        try:
            # Change to the Terraform directory
            os.chdir(output_dir)

            # Run terraform init and plan
            print("\n=== Running Terraform Init & Plan ===")
            init_result = subprocess.run(
                ["terraform", "init"],
                capture_output=True,
                text=True
            )
            print(init_result.stdout)
            if init_result.stderr:
                print("Init Errors:", init_result.stderr)

            plan_result = subprocess.run(
                ["terraform", "plan"],
                capture_output=True,
                text=True
            )
            print(plan_result.stdout)
            if plan_result.stderr:
                print("Plan Errors:", plan_result.stderr)

            # If plan failed, retry with a new generation
            if plan_result.returncode != 0:
                print(f"\nPlan failed on attempt {retry_count + 1}, retrying...")
                os.chdir(original_dir)
                return self.generate_terraform(
                    aws_specification=aws_specification,
                    output_dir=output_dir,
                    retry_count=retry_count + 1
                )

            deployment_output = f"""
Init Output:
{init_result.stdout}
{init_result.stderr if init_result.stderr else ''}

Plan Output:
{plan_result.stdout}
{plan_result.stderr if plan_result.stderr else ''}
"""
        except Exception as e:
            print(f"\nError during attempt {retry_count + 1}: {str(e)}")
            os.chdir(original_dir)
            return self.generate_terraform(
                aws_specification=aws_specification,
                output_dir=output_dir,
                retry_count=retry_count + 1
            )
        finally:
            # Return to original directory
            os.chdir(original_dir)

        return tf_code, deployment_output

    def validate_terraform(self, terraform_dir: str) -> str:
        """
        Validate the Terraform configuration in the specified directory.

        Args:
            terraform_dir: Directory containing Terraform configuration

        Returns:
            Validation result message
        """
        try:
            # Change to the terraform directory
            original_dir = os.getcwd()
            os.chdir(terraform_dir)

            # Run terraform init if .terraform directory doesn't exist
            if not os.path.exists(".terraform"):
                init_result = subprocess.run(
                    ["terraform", "init"],
                    capture_output=True,
                    text=True
                )
                if init_result.returncode != 0:
                    return f"Terraform init failed: {init_result.stderr}"

            # Run terraform validate
            validate_result = subprocess.run(
                ["terraform", "validate"],
                capture_output=True,
                text=True
            )

            # Change back to original directory
            os.chdir(original_dir)

            if validate_result.returncode == 0:
                return "Terraform configuration is valid"
            else:
                return f"Terraform validation failed: {validate_result.stderr}"

        except Exception as e:
            # Make sure we return to the original directory
            os.chdir(original_dir)
            return f"Error validating Terraform: {str(e)}"