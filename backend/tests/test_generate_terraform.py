"""Tests for the Terraform generation flow."""

import os
import shutil
import pytest
from typing import Dict

from src.nodes.generate_terraform import generate_terraform
from src.agents.interpreter_agent import InterpreterAgent
from src.agents.tf_generator_agent import TerraformGeneratorAgent
from src.state import CloudPilotState


@pytest.fixture
def clean_terraform_dirs():
    """Fixture to ensure clean terraform directories for each test."""
    dirs_to_clean = ["./terraform"]
    
    # Remove directories if they exist
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
    
    # Run the test
    yield
    
    # Cleanup after test
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)


@pytest.fixture
def mock_state() -> CloudPilotState:
    """Create a mock state for testing."""
    return {
        "messages": [],
        "task": "I want to store files securely with versioning and encryption and a server to run my website",
        "terraform_code": "",
        "terraform_file_path": "",
        "result": "",
        "error": "",
        "user_input": "",
        "next_action": "generate"
    }


def test_interpreter_agent():
    """Test the interpreter agent's ability to convert requests to AWS specifications."""
    interpreter = InterpreterAgent()
    
    # Test simple storage request
    simple_request = "I want to store files"
    simple_spec = interpreter.interpret_request(simple_request)
    assert "S3" in simple_spec
    assert "bucket" in simple_spec.lower()
    
    # Test complex request
    complex_request = "I need secure file storage with versioning and encryption"
    complex_spec = interpreter.interpret_request(complex_request)
    assert "S3" in complex_spec
    assert "encryption" in complex_spec.lower()
    assert "versioning" in complex_spec.lower()


def test_tf_generator_agent(clean_terraform_dirs):
    """Test the Terraform generator agent's ability to create valid configurations."""
    generator = TerraformGeneratorAgent()
    
    # Test generating S3 configuration
    aws_spec = "Create an S3 bucket with versioning and server-side encryption enabled"
    terraform_code, validation_result = generator.generate_tf(aws_spec)
    
    # Check the generated code
    assert "provider" in terraform_code
    assert "aws_s3_bucket" in terraform_code
    assert "versioning" in terraform_code.lower()
    assert "encryption" in terraform_code.lower()
    
    # Check that the file was created
    assert os.path.exists("terraform_prod/main.tf")
    
    # Check validation result
    assert "valid" in validation_result.lower()


def test_generate_terraform_flow(clean_terraform_dirs, mock_state):
    """Test the complete Terraform generation flow."""
    # Run the generate_terraform function
    result_state = generate_terraform(mock_state)
    
    # Check that no errors occurred
    assert result_state["error"] == "", f"Unexpected error: {result_state['error']}"
    
    # Check the result contains both interpretation and validation
    assert "Interpreted Request:" in result_state["result"]
    assert "Validation Result:" in result_state["result"]
    
    # Check that terraform code was generated
    assert result_state["terraform_code"] != ""
    assert "provider" in result_state["terraform_code"]
    assert "aws_s3_bucket" in result_state["terraform_code"]
    
    # Check that the file was created
    assert os.path.exists(result_state["terraform_file_path"])
    
    # Read the generated file and verify contents
    with open(result_state["terraform_file_path"], "r") as f:
        file_content = f.read()
        assert "provider" in file_content
        assert "aws_s3_bucket" in file_content
        assert "versioning" in file_content.lower()
        assert "encryption" in file_content.lower()


def test_generate_terraform_with_complex_requirements(clean_terraform_dirs):
    """Test generation with complex infrastructure requirements."""
    complex_state = CloudPilotState({
        "messages": [],
        "task": "I need a secure S3 bucket. I also want a server to run my website",
        "terraform_code": "",
        "terraform_file_path": "",
        "result": "",
        "error": "",
        "user_input": "",
        "next_action": "generate"
    })
    
    # Run the generate_terraform function
    result_state = generate_terraform(complex_state)
    
    # Check that no errors occurred
    assert result_state["error"] == "", f"Unexpected error: {result_state['error']}"
    
    # Check for advanced features in the generated code
    terraform_code = result_state["terraform_code"].lower()
    assert "versioning" in terraform_code
    assert "encryption" in terraform_code
    assert "logging" in terraform_code
    assert "cloudtrail" in terraform_code
    
    # Verify the file exists and contains the same features
    with open(result_state["terraform_file_path"], "r") as f:
        file_content = f.read().lower()
        assert "versioning" in file_content
        assert "encryption" in file_content
        assert "logging" in file_content
        assert "cloudtrail" in file_content


def test_terraform_generator_output(capfd):
    """Test to show the raw output of the Terraform generator."""
    
    # Initialize generator
    generator = TerraformGeneratorAgent()
    
    # Simple web server request
    specification = """
    Create a web server with:
    - EC2 instance (t3.micro)
    - S3 bucket for static files
    """
    
    print("\n=== Testing Terraform Generator Output ===")
    print(f"Input Specification:\n{specification}")
    
    # Generate Terraform code
    code, result = generator.generate_terraform(specification)
    
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