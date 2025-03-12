"""Generator agent for creating Terraform configurations."""

import os
import subprocess
from typing import Tuple
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

    def generate_code(self, aws_specification: str, retry_count: int = 0) -> str:
        """Generate Terraform configuration based on AWS specification."""
        if retry_count >= 4:
            return ""

        try:
            # Get current infrastructure state
            show_result = subprocess.run(
                ["terraform", "show"],
                capture_output=True,
                text=True
            )
            current_state = show_result.stdout if show_result.returncode == 0 else "No existing infrastructure"

            # Define the prompt for Terraform generation
            prompt = """You are a Terraform code generator. Generate ONLY the complete, valid Terraform code.

CRITICAL: Output ONLY valid Terraform code. Do not include any explanations, comments, or natural language text.
Start directly with the terraform block. Do not include any introductory text or descriptions.

CURRENT_INFRASTRUCTURE:
""" + current_state + """

SPECIFICATION:
""" + aws_specification + """

Analyze carefully the user requests and don't duplicate any resources you don't have to. 
Remove any resources that the user does not want and add the resources that the user DOES want.
Modify the current infrastructure to fulfill the user needs.

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
10. IF the user wants a server, ALWAYS use the following AMI ami-05b10e08d247fb927
11. NEVER include any natural language text or descriptions
12. Start DIRECTLY with the terraform block

If the user request requires a VPC and networking refer to the following requirements.
CRITICAL VPC REQUIREMENTS:
1. Create public and private subnets in different availability zones
2. Ensure EC2 instances and ELB/ALB are in the same VPC
3. Place EC2 instances in public subnets if they need internet access
4. Configure route tables and internet gateway properly
5. Use consistent CIDR blocks (e.g., 10.0.1.0/24 for public, 10.0.2.0/24 for private)
6. Associate subnets with the load balancer
7. Ensure security groups allow traffic between ELB and EC2 instances
8. ALWAYS use us-east-1 as the region for any resource that needs it.

EXAMPLE VPC CONFIGURATION:
resource "aws_vpc" "cloudpilot_vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
}

resource "aws_subnet" "cloudpilot_public_subnet" {
  vpc_id     = aws_vpc.cloudpilot_vpc.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "us-east-1a"
}

resource "aws_lb" "cloudpilot_alb" {
  subnets = [aws_subnet.cloudpilot_public_subnet.id]
  security_groups = [aws_security_group.cloudpilot_sg.id]
  internal = false
}

resource "aws_instance" "cloudpilot_ec2" {
  subnet_id = aws_subnet.cloudpilot_public_subnet.id
  vpc_security_group_ids = [aws_security_group.cloudpilot_sg.id]
}

COMMON ERRORS TO AVOID:
1. EC2 instance not in same VPC as ELB
2. Missing subnet associations
3. Incorrect security group rules
4. Missing route table associations
5. Improper availability zone configuration


IF the user request does not require a VPC and networking, for example, an S3 bucket, then do not include any VPC.
GENERAL REQUIREMENTS:
1. If the user request does not require a VPC and networking, do not include any VPC.
2. If the user request does not require a server, do not include any EC2 instances.
3. Only include the required resources to fulfill the user request.

Generate ONLY the Terraform configuration, starting with the terraform block:
"""

            # Generate the Terraform code
            response = self.llm.complete(prompt)
            print(f"\n=== Attempt {retry_count + 1} ===")

            # Get and validate the response text
            tf_code = response.text.strip()
            
            # Remove any natural language text before terraform block
            if "terraform {" in tf_code:
                tf_code = tf_code[tf_code.index("terraform {"):]
            
            print(tf_code)

            # Additional validation for response completeness
            if not tf_code or len(tf_code) < 50:  # Basic length check
                print(f"\nResponse too short on attempt {retry_count + 1}, retrying...")
                return self.generate_code(
                    aws_specification=aws_specification,
                    retry_count=retry_count + 1
                )

            # Validate the generated code
            if not self.validate_code(tf_code):
                print(f"\nCode validation failed on attempt {retry_count + 1}, retrying...")
                return self.generate_code(
                    aws_specification=aws_specification,
                    retry_count=retry_count + 1
                )

            return tf_code

        except Exception as e:
            print(f"\nError during attempt {retry_count + 1}: {str(e)}")
            return self.generate_code(
                aws_specification=aws_specification,
                retry_count=retry_count + 1
            )

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