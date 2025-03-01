"""Tests for the Terraform plan and approval nodes."""

import os
import pytest
from unittest.mock import patch, MagicMock

from src.nodes.terraform_plan import terraform_plan
from src.nodes.plan_approval import plan_approval
from src.agents.terraform_agent import TerraformAgent


@pytest.fixture
def mock_terraform_file(tmp_path):
    """Create a mock terraform file for testing."""
    terraform_dir = tmp_path / "terraform"
    terraform_dir.mkdir()

    # Create a simple S3 bucket terraform file
    tf_file = terraform_dir / "main.tf"
    tf_file.write_text("""
    provider "aws" {
        region = "us-west-2"
    }

    resource "aws_s3_bucket" "test_bucket" {
        bucket = "test-bucket-name"
    }
    """)

    return str(tf_file)


@pytest.fixture
def mock_terraform_agent():
    """Create a mock TerraformAgent."""
    with patch('src.nodes.terraform_plan.TerraformAgent') as mock:
        agent_instance = mock.return_value
        # Mock successful plan
        agent_instance.terraform_plan.return_value = """
        Terraform will perform the following actions:

        # aws_s3_bucket.test_bucket will be created
        + resource "aws_s3_bucket" "test_bucket" {
            + bucket = "test-bucket-name"
            + id     = (known after apply)
        }

        Plan: 1 to add, 0 to change, 0 to destroy.
        """
        yield agent_instance


def test_terraform_plan_success(mock_terraform_file, mock_terraform_agent):
    """Test successful terraform plan creation."""
    # Initial state
    state = {
        "task": "Create an S3 bucket",
        "terraform_code": "",
        "terraform_file_path": mock_terraform_file,
        "result": "",
        "error": "",
        "user_input": "",
        "next_action": "plan"
    }

    # Run the plan node
    new_state = terraform_plan(state)

    # Verify the agent was called correctly
    mock_terraform_agent.terraform_plan.assert_called_once_with(
        os.path.dirname(mock_terraform_file)
    )

    # Check the state was updated correctly
    assert new_state["error"] == ""
    assert "Plan: 1 to add" in new_state["result"]
    assert new_state["next_action"] == "plan_approval"
    assert os.path.exists(os.path.join(
        os.path.dirname(mock_terraform_file),
        "terraform.plan.out.tf"
    ))


def test_terraform_plan_error(mock_terraform_file, mock_terraform_agent):
    """Test terraform plan with error."""
    # Mock an error response
    mock_terraform_agent.terraform_plan.return_value = "Error: Invalid resource type"

    # Initial state
    state = {
        "task": "Create an S3 bucket",
        "terraform_code": "",
        "terraform_file_path": mock_terraform_file,
        "result": "",
        "error": "",
        "user_input": "",
        "next_action": "plan"
    }

    # Run the plan node
    new_state = terraform_plan(state)

    # Check error handling
    assert "Error:" in new_state["error"]
    assert new_state["next_action"] == "user_interaction"


def test_plan_approval_approve(monkeypatch):
    """Test plan approval with 'approve' choice."""
    # Mock user input
    monkeypatch.setattr('builtins.input', lambda _: "1")

    # Initial state with successful plan
    state = {
        "task": "Create an S3 bucket",
        "terraform_code": "",
        "terraform_file_path": "/tmp/test.tf",
        "result": "Plan: 1 to add, 0 to change, 0 to destroy.",
        "error": "",
        "user_input": "",
        "next_action": "plan_approval"
    }

    # Run the approval node
    new_state = plan_approval(state)

    # Check the state was updated correctly
    assert new_state["next_action"] == "execute_terraform"
    assert new_state["error"] == ""


def test_plan_approval_reject(monkeypatch):
    """Test plan approval with 'reject' choice."""
    # Mock user input
    monkeypatch.setattr('builtins.input', lambda _: "2")

    # Initial state with successful plan
    state = {
        "task": "Create an S3 bucket",
        "terraform_code": "",
        "terraform_file_path": "/tmp/test.tf",
        "result": "Plan: 1 to add, 0 to change, 0 to destroy.",
        "error": "",
        "user_input": "",
        "next_action": "plan_approval"
    }

    # Run the approval node
    new_state = plan_approval(state)

    # Check the state was updated correctly
    assert new_state["next_action"] == "generate_terraform"
    assert new_state["user_input"] == "modify"
    assert new_state["error"] == ""


def test_plan_approval_cancel(monkeypatch):
    """Test plan approval with 'cancel' choice."""
    # Mock user input
    monkeypatch.setattr('builtins.input', lambda _: "3")

    # Initial state with successful plan
    state = {
        "task": "Create an S3 bucket",
        "terraform_code": "",
        "terraform_file_path": "/tmp/test.tf",
        "result": "Plan: 1 to add, 0 to change, 0 to destroy.",
        "error": "",
        "user_input": "",
        "next_action": "plan_approval"
    }

    # Run the approval node
    new_state = plan_approval(state)

    # Check the state was updated correctly
    assert new_state["next_action"] == "user_interaction"
    assert new_state["error"] == ""


def test_plan_approval_with_error():
    """Test plan approval when there's an error in the state."""
    # Initial state with error
    state = {
        "task": "Create an S3 bucket",
        "terraform_code": "",
        "terraform_file_path": "/tmp/test.tf",
        "result": "",
        "error": "Failed to create plan",
        "user_input": "",
        "next_action": "plan_approval"
    }

    # Run the approval node
    new_state = plan_approval(state)

    # Check error handling
    assert new_state["next_action"] == "user_interaction"
    assert new_state["error"] == "Failed to create plan"