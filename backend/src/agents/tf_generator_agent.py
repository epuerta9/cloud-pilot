"""Generator agent for creating Terraform configurations."""

import os
import subprocess
from typing import Dict, List, Optional
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
    
    def generate_tf(self, aws_specification: str, output_dir: str = "terraform_prod") -> tuple[str, str]:
        """
        Generate Terraform configuration based on AWS specification.
        
        Args:
            aws_specification: The AWS service specification
            output_dir: Directory to write the Terraform configuration
            
        Returns:
            Tuple of (generated terraform code, validation result)
        """
        prompt = f"""You are a Terraform code generator. Your ONLY job is to output valid Terraform HCL code.

SPECIFICATION:
{aws_specification}

RULES:
1. Output ONLY valid Terraform code
2. Start with provider block
3. Include all necessary resources
4. Follow AWS best practices
5. Include appropriate tagging
6. Configure security best practices
7. Use clear resource naming
8. If a user requests a server, make sure to use the ami ami-0abe47a8515be836d
9. Prepend every resource name with cloudpilot_
10. KEEP IT SIMPLE don't do extra log buckets or anything. SIMPLE is better.

CRITICAL:
- NO explanations
- NO markdown
- NO backticks
- NO comments outside code
- ONLY valid HCL syntax
- Start IMMEDIATELY with 'provider "aws"'
- NO acm certificates
- NO DNS ZONES

EXAMPLE OUTPUT FORMAT:
provider "aws" {{
  region = "us-west-2"
}}

resource "aws_s3_bucket" "example" {{
  bucket = "example-bucket"
}}
"""
        
        # Generate the Terraform code
        response = self.llm.complete(prompt)
        terraform_code = response.text.strip()
        
        # Clean up any potential explanatory text or markdown
        lines = terraform_code.split("\n")
        clean_lines = []
        in_code = False
        
        for line in lines:
            line = line.strip()
            # Skip empty lines at the start
            if not in_code and not line:
                continue
            
            # Start capturing at provider block
            if line.startswith("provider"):
                in_code = True
            
            # Skip any line that looks like explanation
            if in_code and not any(word in line.lower() for word in ["here's", "this", "note", "explanation", "creates", "sets up"]):
                clean_lines.append(line)
        
        # Ensure we have valid HCL
        terraform_code = "\n".join(clean_lines)
        
        # Additional cleanup
        terraform_code = terraform_code.replace("```hcl", "").replace("```terraform", "").replace("```", "")
        terraform_code = terraform_code.replace("Here's", "").replace("This creates", "")
        
        # Ensure it starts with provider block
        if not terraform_code.strip().startswith("provider"):
            terraform_code = "provider \"aws\" {\n  region = \"us-west-2\"\n}\n\n" + terraform_code
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Write the generated code to main.tf
        output_file = os.path.join(output_dir, "main.tf")
        with open(output_file, "w") as f:
            f.write(terraform_code)
        
        # Validate the generated Terraform code
        validation_result = self.validate_terraform(output_dir)
        
        return terraform_code, validation_result
    
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