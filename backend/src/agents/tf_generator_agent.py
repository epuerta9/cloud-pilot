"""Generator agent for creating Terraform configurations."""

import os
import subprocess
from typing import Dict, List, Optional, Tuple
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic


class TerraformGeneratorAgent:
    """Agent for generating and managing Terraform configurations."""
    
    def __init__(self, model_name: str = "claude-3-5-sonnet-20240620"):
        """Initialize the Terraform generator agent."""
        self.terraform_dir = "./terraform"
        self.existing_files = {}
        self.llm = Anthropic(model=model_name)
    
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

    def generate_terraform(self, aws_specification: str, output_dir: str = "terraform_prod", retry_count: int = 0) -> Tuple[str, str]:
        """Generate Terraform configuration based on AWS specification."""
        if retry_count >= 4:
            return "", "Max retries reached - unable to generate valid Terraform configuration"
        
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

EXAMPLE OF COMPLETE, VALID CODE:
provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "cloudpilot_vpc" {
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = "cloudpilot_vpc"
  }
}

resource "aws_security_group" "cloudpilot_sg" {
  name        = "cloudpilot_sg"
  description = "Allow HTTP traffic"
  vpc_id      = aws_vpc.cloudpilot_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "cloudpilot_sg"
  }
}

Generate ONLY complete, valid Terraform code following this exact format. Make sure ALL blocks are properly closed.
"""
        
        # Generate the Terraform code
        response = self.llm.complete(prompt)
        print(f"\n=== Attempt {retry_count + 1} ===")
        print(response.text)
        tf_code = response.text.strip()
        
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
        
        # Write the generated code to main.tf
        output_file = os.path.join(output_dir, "main.tf")
        with open(output_file, "w") as f:
            f.write(tf_code)
        
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