"""Tests for the generate_terraform node."""

import os
import shutil
import pytest
from typing import Dict

from src.nodes.generate_terraform import generate_terraform
from src.state import CloudPilotState


@pytest.fixture
def clean_terraform_dir():
    """Fixture to ensure a clean terraform directory for each test."""
    # Remove terraform directory if it exists
    if os.path.exists("./terraform"):
        shutil.rmtree("./terraform")
    
    # Run the test
    yield
    
    # Cleanup after test
    if os.path.exists("./terraform"):
        shutil.rmtree("./terraform")


@pytest.fixture
def mock_state() -> CloudPilotState:
    """Create a mock state for testing."""
    return {
        "messages": [],
        "task": "I want to store files",
        "terraform_code": "",
        "terraform_file_path": "",
        "result": "",
        "error": "",
        "user_input": "",
        "next_action": "generate"
    }


def test_generate_terraform_basic(clean_terraform_dir, mock_state):
    """Test basic terraform generation for a simple storage request."""
    # Run the generate_terraform function
    result_state = generate_terraform(mock_state)
    
    # Check that no errors occurred
    assert result_state["error"] == "", f"Unexpected error: {result_state['error']}"
    
    # Check that we got an interpreted request
    assert "Interpreted Request:" in result_state["result"]
    
    # Check that the interpretation mentions S3 (since the task was about storage)
    assert "S3" in result_state["result"]
    
    # Verify terraform directory was created
    assert os.path.exists("./terraform")


# def test_generate_terraform_with_error(clean_terraform_dir):
#     """Test error handling with invalid state."""
#     # Create an invalid state (missing required fields)
#     invalid_state = {
#         "messages": [],
#         "task": None,  # This should cause an error
#         "terraform_code": "",
#         "terraform_file_path": "",
#         "result": "",
#         "error": "",
#         "user_input": "",
#         "next_action": "generate"
#     }
    
#     # Run the generate_terraform function
#     result_state = generate_terraform(invalid_state)
    
#     # Check that an error was recorded
#     assert result_state["error"] != ""
#     assert "Error in generate_terraform" in result_state["error"]


# def test_generate_terraform_complex_request(clean_terraform_dir, mock_state):
#     """Test terraform generation for a more complex infrastructure request."""
#     # Modify the mock state with a more complex task
#     mock_state["task"] = "I need a web application with a database and file storage"
    
#     # Run the generate_terraform function
#     result_state = generate_terraform(mock_state)
    
#     # Check that no errors occurred
#     assert result_state["error"] == "", f"Unexpected error: {result_state['error']}"
    
#     # Check that the interpretation includes relevant AWS services
#     result = result_state["result"].lower()
#     assert any(service in result for service in ["s3", "rds", "ec2", "ecs"])


# def test_generate_terraform_directory_persistence(clean_terraform_dir, mock_state):
#     """Test that the terraform directory persists between runs."""
#     # First run
#     result_state = generate_terraform(mock_state)
#     assert os.path.exists("./terraform")
    
#     # Create a dummy file in the terraform directory
#     with open("./terraform/dummy.tf", "w") as f:
#         f.write("# Dummy terraform file")
    
#     # Second run
#     result_state = generate_terraform(mock_state)
    
#     # Check that the dummy file still exists
#     assert os.path.exists("./terraform/dummy.tf")
    
#     # Check that the file content was preserved
#     with open("./terraform/dummy.tf", "r") as f:
#         content = f.read()
#     assert content == "# Dummy terraform file" 