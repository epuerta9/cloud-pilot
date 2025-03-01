"""Generator agent for creating AWS CDK configurations in Python."""

import os
import subprocess
from typing import Dict, List, Optional, Tuple
from llama_index.llms.anthropic import Anthropic


class CDKGeneratorAgent:
    """Agent for generating and managing AWS CDK configurations."""
    
    def __init__(self, model_name: str = "claude-3-5-sonnet-20240620"):
        """Initialize the CDK generator agent."""
        self.cdk_dir = "./cdk"
        self.existing_files = {}
        self.llm = Anthropic(model=model_name)
    
    def initialize_workspace(self) -> None:
        """
        Initialize the CDK workspace by creating the directory
        and reading any existing files.
        """
        # Create CDK directory if it doesn't exist
        if not os.path.exists(self.cdk_dir):
            os.makedirs(self.cdk_dir)
            
        # Read all existing .py files into memory
        self.existing_files = {}
        for file in os.listdir(self.cdk_dir):
            if file.endswith('.py'):
                file_path = os.path.join(self.cdk_dir, file)
                with open(file_path, 'r') as f:
                    self.existing_files[file] = f.read()
    
    def validate_code(self, code: str) -> bool:
        """Validate the generated code for common syntax errors."""
        # Check for incomplete statements
        if code.count('(') != code.count(')'):
            return False
        if code.count('[') != code.count(']'):
            return False
        if code.count('{') != code.count('}'):
            return False
        
        # Check for incomplete method calls
        if code.endswith('.ad') or code.endswith('.add'):
            return False
        
        # Check for basic Python syntax
        try:
            compile(code, '<string>', 'exec')
            return True
        except SyntaxError:
            return False

    def generate_cdk(self, aws_specification: str, output_dir: str = "cdk_test", retry_count: int = 0) -> Tuple[str, str]:
        """Generate CDK configuration based on AWS specification."""
        if retry_count >= 4:
            return "", "Max retries reached - unable to generate valid CDK configuration"
        
        prompt = """You are a Python CDK code generator. Generate ONLY the complete, valid Python code for a CDK stack.

SPECIFICATION:
""" + aws_specification + """

REQUIREMENTS:
1. Generate ONLY the complete Python file contents - no explanations or markdown
2. Start with all necessary imports
3. Use proper Python indentation (4 spaces)
4. Include proper closing brackets/parentheses
5. Follow AWS CDK best practices
6. Use cloudpilot_ prefix for all resource IDs
7. For EC2 instances:
   - Use ami-0c7217cdde317cfec for x86_64 architecture (t3.micro)
   - ALWAYS match instance type architecture with AMI architecture
   - For t3.micro, use x86_64 AMI
8. Keep the implementation simple and focused
9. ALWAYS complete all code blocks
10. ALWAYS close all parentheses and brackets
11. NEVER leave any statements incomplete

EXAMPLE OF COMPLETE, VALID CODE:
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_elasticloadbalancingv2_targets as targets
)
from constructs import Construct

class CloudPilotStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # VPC with 2 AZs
        vpc = ec2.Vpc(self, "cloudpilot_vpc",
            max_azs=2
        )
        
        # Security group allowing HTTP
        security_group = ec2.SecurityGroup(self, "cloudpilot_sg",
            vpc=vpc,
            allow_all_outbound=True,
            description="Allow HTTP traffic"
        )
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            "Allow HTTP traffic"
        )
        
        # EC2 instance
        instance = ec2.Instance(self, "cloudpilot_instance",
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
            machine_image=ec2.MachineImage.generic_linux({
                "us-east-1": "ami-0c7217cdde317cfec"
            }),
            vpc=vpc,
            security_group=security_group
        )
        
        # Application load balancer
        alb = elbv2.ApplicationLoadBalancer(self, "cloudpilot_alb",
            vpc=vpc,
            internet_facing=True,
            security_group=security_group
        )
        
        # Target group
        target_group = elbv2.ApplicationTargetGroup(self, "cloudpilot_tg",
            vpc=vpc,
            port=80,
            targets=[targets.InstanceTarget(instance)]
        )
        
        # Listener
        listener = alb.add_listener("cloudpilot_listener",
            port=80,
            open=True,
            default_action=elbv2.ListenerAction.forward([target_group])
        )

Generate ONLY complete, valid Python code following this exact format. Make sure ALL code blocks are properly closed.
"""
        
        # Generate the CDK code
        response = self.llm.complete(prompt)
        print(f"\n=== Attempt {retry_count + 1} ===")
        print(response.text)
        cdk_code = response.text.strip()
        
        # Validate the generated code
        if not self.validate_code(cdk_code):
            print(f"\nCode validation failed on attempt {retry_count + 1}, retrying...")
            return self.generate_cdk(
                aws_specification=aws_specification,
                output_dir=output_dir,
                retry_count=retry_count + 1
            )
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Write the generated code to stack.py
        output_file = os.path.join(output_dir, "stack.py")
        with open(output_file, "w") as f:
            f.write(cdk_code)
        
        # Create app.py if it doesn't exist
        app_file = os.path.join(output_dir, "app.py")
        if not os.path.exists(app_file):
            app_code = """#!/usr/bin/env python3
from aws_cdk import App
from stack import CloudPilotStack

app = App()
CloudPilotStack(app, "CloudPilotStack")
app.synth()
"""
            with open(app_file, "w") as f:
                f.write(app_code)
        
        # Store current directory
        original_dir = os.getcwd()
        deployment_output = ""
        
        try:
            # Change to the CDK directory
            os.chdir(output_dir)
            
            # Run CDK diff
            print("\n=== Running CDK diff ===")
            diff_result = subprocess.run(
                ["cdk", "diff"],
                capture_output=True,
                text=True
            )
            print(diff_result.stdout)
            if diff_result.stderr:
                print("Diff Errors:", diff_result.stderr)
            
            # If diff failed, retry with a new generation
            if diff_result.returncode != 0:
                print(f"\nDiff failed on attempt {retry_count + 1}, retrying...")
                os.chdir(original_dir)
                return self.generate_cdk(
                    aws_specification=aws_specification,
                    output_dir=output_dir,
                    retry_count=retry_count + 1
                )
            
            # Run CDK deploy
            print("\n=== Running CDK deploy ===")
            deploy_result = subprocess.run(
                ["cdk", "deploy", "--require-approval", "never"],
                capture_output=True,
                text=True
            )
            print(deploy_result.stdout)
            if deploy_result.stderr:
                print("Deploy Errors:", deploy_result.stderr)
            
            deployment_output = f"""
Diff Output:
{diff_result.stdout}
{diff_result.stderr if diff_result.stderr else ''}

Deploy Output:
{deploy_result.stdout}
{deploy_result.stderr if deploy_result.stderr else ''}
"""
        except Exception as e:
            print(f"\nError during attempt {retry_count + 1}: {str(e)}")
            os.chdir(original_dir)
            return self.generate_cdk(
                aws_specification=aws_specification,
                output_dir=output_dir,
                retry_count=retry_count + 1
            )
        finally:
            # Return to original directory
            os.chdir(original_dir)

        return cdk_code, deployment_output
    
    def validate_cdk(self, cdk_dir: str) -> str:
        """
        Validate the CDK configuration in the specified directory.
        
        Args:
            cdk_dir: Directory containing CDK configuration
            
        Returns:
            Validation result message
        """
        try:
            # Store current directory
            original_dir = os.getcwd()
            
            try:
                # Change to the CDK directory
                os.chdir(cdk_dir)
                
                # Run CDK synth to validate
                print("\n=== Running CDK validation ===")
                validate_result = subprocess.run(
                    ["cdk", "synth"],
                    capture_output=True,
                    text=True
                )
                
                print(validate_result.stdout)
                if validate_result.stderr:
                    print("Validation Errors:", validate_result.stderr)
                
                if validate_result.returncode == 0:
                    return "CDK configuration is valid"
                else:
                    return f"CDK validation failed: {validate_result.stderr}"
                
            finally:
                # Return to original directory
                os.chdir(original_dir)
            
        except Exception as e:
            return f"Error validating CDK: {str(e)}" 