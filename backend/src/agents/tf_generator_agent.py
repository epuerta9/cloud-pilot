"""Generator agent for creating Terraform configurations."""

import os
from typing import Dict, List, Optional


class TerraformGeneratorAgent:
    """Agent for generating and managing Terraform configurations."""
    
    def __init__(self):
        """Initialize the Terraform generator agent."""
        self.terraform_dir = "./terraform"
        self.existing_files = {}
    
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