"""Terraform agent for Cloud Pilot."""

import os
from typing import Dict, List, Optional

from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from llama_index.core.tools import BaseTool, FunctionTool
import subprocess


class TerraformAgent:
    """Agent for working with Terraform code."""
    
    def __init__(self, model_name: str = "gpt-4"):
        """
        Initialize the Terraform agent.
        
        Args:
            model_name: The name of the OpenAI model to use
        """
        self.llm = OpenAI(model=model_name)
        self.tools = self._create_tools()
    
    def _create_tools(self) -> List[BaseTool]:
        """Create tools for the agent to use."""
        tools = [
            FunctionTool.from_defaults(
                name="read_terraform_file",
                fn=self.read_terraform_file,
                description="Read a Terraform file from disk"
            ),
            FunctionTool.from_defaults(
                name="write_terraform_file",
                fn=self.write_terraform_file,
                description="Write Terraform code to a file"
            ),
            FunctionTool.from_defaults(
                name="terraform_init",
                fn=self.terraform_init,
                description="Initialize a Terraform working directory"
            ),
            FunctionTool.from_defaults(
                name="terraform_plan",
                fn=self.terraform_plan,
                description="Create a Terraform execution plan"
            ),
            FunctionTool.from_defaults(
                name="terraform_apply",
                fn=self.terraform_apply,
                description="Apply a Terraform execution plan"
            ),
            FunctionTool.from_defaults(
                name="terraform_destroy",
                fn=self.terraform_destroy,
                description="Destroy Terraform-managed infrastructure"
            ),
        ]
        return tools
    
    def read_terraform_file(self, file_path: str) -> str:
        """
        Read a Terraform file from disk.
        
        Args:
            file_path: Path to the Terraform file
            
        Returns:
            The contents of the file
        """
        try:
            with open(file_path, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def write_terraform_file(self, file_path: str, content: str) -> str:
        """
        Write Terraform code to a file.
        
        Args:
            file_path: Path to write the file to
            content: The Terraform code to write
            
        Returns:
            A success or error message
        """
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, "w") as f:
                f.write(content)
            
            return f"Successfully wrote Terraform code to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
    
    def terraform_init(self, directory: str) -> str:
        """
        Initialize a Terraform working directory.
        
        Args:
            directory: The directory containing Terraform configuration files
            
        Returns:
            The output of the terraform init command
        """
        try:
            # Change to the specified directory
            original_dir = os.getcwd()
            os.chdir(directory)
            
            # Run terraform init
            result = subprocess.run(
                ["terraform", "init"],
                capture_output=True,
                text=True
            )
            
            # Change back to the original directory
            os.chdir(original_dir)
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running terraform init: {str(e)}"
    
    def terraform_plan(self, directory: str) -> str:
        """
        Create a Terraform execution plan.
        
        Args:
            directory: The directory containing Terraform configuration files
            
        Returns:
            The output of the terraform plan command
        """
        try:
            # Change to the specified directory
            original_dir = os.getcwd()
            os.chdir(directory)
            
            # Run terraform plan
            result = subprocess.run(
                ["terraform", "plan", "-no-color"],
                capture_output=True,
                text=True
            )
            
            # Change back to the original directory
            os.chdir(original_dir)
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running terraform plan: {str(e)}"
    
    def terraform_apply(self, directory: str, auto_approve: bool = False) -> str:
        """
        Apply a Terraform execution plan.
        
        Args:
            directory: The directory containing Terraform configuration files
            auto_approve: Whether to automatically approve the plan
            
        Returns:
            The output of the terraform apply command
        """
        try:
            # Change to the specified directory
            original_dir = os.getcwd()
            os.chdir(directory)
            
            # Prepare the command
            cmd = ["terraform", "apply", "-no-color"]
            if auto_approve:
                cmd.append("-auto-approve")
            
            # Run terraform apply
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            # Change back to the original directory
            os.chdir(original_dir)
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running terraform apply: {str(e)}"
    
    def terraform_destroy(self, directory: str, auto_approve: bool = False) -> str:
        """
        Destroy Terraform-managed infrastructure.
        
        Args:
            directory: The directory containing Terraform configuration files
            auto_approve: Whether to automatically approve the destruction
            
        Returns:
            The output of the terraform destroy command
        """
        try:
            # Change to the specified directory
            original_dir = os.getcwd()
            os.chdir(directory)
            
            # Prepare the command
            cmd = ["terraform", "destroy", "-no-color"]
            if auto_approve:
                cmd.append("-auto-approve")
            
            # Run terraform destroy
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            # Change back to the original directory
            os.chdir(original_dir)
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running terraform destroy: {str(e)}"
    
    def analyze_terraform(self, terraform_code: str) -> Dict:
        """
        Analyze Terraform code to understand its purpose and structure.
        
        Args:
            terraform_code: The Terraform code to analyze
            
        Returns:
            A dictionary containing the analysis results
        """
        prompt = f"""
        Analyze the following Terraform code and provide a structured analysis:
        
        ```
        {terraform_code}
        ```
        
        Return a JSON object with the following structure:
        {{
            "resources": [
                {{
                    "type": "resource_type",
                    "name": "resource_name",
                    "purpose": "brief description"
                }}
            ],
            "providers": ["provider1", "provider2"],
            "variables": ["var1", "var2"],
            "outputs": ["output1", "output2"],
            "summary": "brief summary of what this Terraform code does",
            "recommendations": ["recommendation1", "recommendation2"]
        }}
        
        Return only the JSON, no explanations.
        """
        
        response = self.llm.complete(prompt)
        
        # Parse the response to get the analysis
        import json
        try:
            analysis = json.loads(response.text)
            return analysis
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse analysis",
                "raw_response": response.text
            }
    
    def generate_terraform(self, task_description: str, existing_code: Optional[str] = None) -> str:
        """
        Generate Terraform code based on a task description.
        
        Args:
            task_description: Description of what the Terraform code should do
            existing_code: Existing Terraform code to modify, if any
            
        Returns:
            Generated Terraform code
        """
        if existing_code:
            prompt = f"""
            Modify the following Terraform code based on this task: {task_description}
            
            Current Terraform code:
            ```
            {existing_code}
            ```
            
            Return only the modified Terraform code, no explanations.
            """
        else:
            prompt = f"""
            Generate Terraform code for the following task: {task_description}
            
            Return only the Terraform code, no explanations.
            """
        
        response = self.llm.complete(prompt)
        
        # Extract the code from the response
        terraform_code = response.text
        
        # Clean up the code (remove markdown code blocks if present)
        if terraform_code.startswith("```") and terraform_code.endswith("```"):
            terraform_code = terraform_code.split("```")[1]
            if terraform_code.startswith("terraform") or terraform_code.startswith("hcl"):
                terraform_code = terraform_code[terraform_code.find("\n")+1:]
        
        return terraform_code 