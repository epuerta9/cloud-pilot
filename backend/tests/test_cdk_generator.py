"""Tests for the CDK generator agent."""

import os
import pytest
from typing import Dict

from src.agents.cdk_generator_agent import CDKGeneratorAgent
from src.agents.interpreter_agent import InterpreterAgent


def test_user_request_flow(capfd):
    """Test handling a user request to create AWS infrastructure."""
    
    # Initialize agents
    interpreter = InterpreterAgent()
    generator = CDKGeneratorAgent()
    
    # Simulate user request
    # user_request = """
    # I need a secure S3 bucket for storing sensitive data with:
    # - Versioning enabled
    # - Encryption
    # - No public access
    # - Auto cleanup when deleted
    # """
    user_request = """
    I need a web server
    """
    
    print("\n=== Processing User Request ===")
    print(f"User Request: {user_request}")
    
    try:
        # First, interpret the request into AWS specifications
        print("\n=== Interpreting Request ===")
        aws_spec = interpreter.interpret_request(user_request)
        print(f"Interpreted Spec: {aws_spec}")
        
        # Generate and deploy CDK code
        print("\n=== Generating and Deploying Infrastructure ===")
        code, result = generator.generate_cdk(aws_spec)
        
        # Print the generated code
        print("\n=== Generated CDK Code ===")
        print(code)
        
        # Print deployment results
        print("\n=== Deployment Results ===")
        print(result)
        
        # Verify the code meets requirements
        assert "aws_s3 as s3" in code
        assert "versioned=True" in code
        assert "encryption" in code.lower()
        assert "block_public_access" in code.lower()
        assert "removal_policy" in code.lower()
        
        print("\n=== Infrastructure successfully created! ===")
        print("You can find the CDK code in ./cdk_test")
        print("To manage the infrastructure manually:")
        print("  cd cdk_test")
        print("  cdk diff     # to see changes")
        print("  cdk deploy   # to deploy changes")
        print("  cdk destroy  # to cleanup")
        
    except Exception as e:
        print(f"\nError during test: {str(e)}")
        raise
    finally:
        # Capture and print all output
        out, err = capfd.readouterr()
        if err:
            print("\nErrors:")
            print(err)


def test_complex_user_request(capfd):
    """Test handling a more complex infrastructure request."""
    
    interpreter = InterpreterAgent()
    generator = CDKGeneratorAgent()
    
    # More complex user request
    user_request = """
    I need a web application setup with:
    - An EC2 server for the website
    - An S3 bucket for static files
    - Make sure it's secure
    """
    
    print("\n=== Processing Complex User Request ===")
    print(f"User Request: {user_request}")
    
    try:
        # Interpret and generate
        aws_spec = interpreter.interpret_request(user_request)
        code, result = generator.generate_cdk(aws_spec)
        
        # Verify all components are included
        assert "aws_s3 as s3" in code
        assert "aws_ec2 as ec2" in code
        assert "ami-0abe47a8515be836d" in code  # Specific AMI
        assert "vpc" in code.lower()
        assert "security_group" in code.lower()
        
        print("\n=== Generated Infrastructure ===")
        print(code)
        print("\n=== Deployment Results ===")
        print(result)
        
    except Exception as e:
        print(f"\nError during test: {str(e)}")
        raise
    finally:
        out, err = capfd.readouterr()
        if err:
            print("\nErrors:")
            print(err)


def test_cdk_generator_output(capfd):
    """Test to show the raw output of the CDK generator."""
    
    # Initialize generator
    generator = CDKGeneratorAgent()
    
    # # Simple web server request
    # specification = """
    # Create a web server with:
    # - EC2 instance (t3.micro)
    # - Security group allowing HTTP
    # - Application load balancer
    # - VPC with 2 AZs
    # """
    # Simple web server request
    specification = """
    Create a web server with:
    - EC2 instance (t3.micro)
    - S3 bucket for static files
    """
    
    print("\n=== Testing CDK Generator Output ===")
    print(f"Input Specification:\n{specification}")
    
    # Generate CDK code
    code, result = generator.generate_cdk(specification)
    
    # Capture all stdout/stderr
    out, err = capfd.readouterr()
    
    # Print the captured output
    print("\n=== Generator Output ===")
    print(out)
    
    if err:
        print("\n=== Generator Errors ===")
        print(err)
    
    print("\n=== Generated Code ===")
    print(code)
    
    print("\n=== Deployment Result ===")
    print(result)


if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__]) 