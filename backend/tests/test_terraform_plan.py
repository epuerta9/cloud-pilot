"""Tests for the Terraform plan and approval nodes."""

import os
import pytest
from unittest.mock import patch, MagicMock

from src.nodes.terraform_plan import terraform_plan
from src.nodes.plan_approval import plan_approval
from src.agents.terraform_agent import TerraformAgent
from src.constants import ACTION_USER_INTERACTION, ACTION_APPROVE_PLAN, ACTION_GENERATE, ACTION_EXECUTE


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


@pytest.fixture
def mock_state():
    """Create a mock state for testing."""
    return {
        "task": "Create an S3 bucket",
        "terraform_code": "resource \"aws_s3_bucket\" \"test\" {}",
        "terraform_file_path": "test.tf",
        "result": "",
        "error": "",
        "user_input": "",
        "next_action": ""
    }


def test_terraform_plan_no_file_path():
    """Test terraform_plan with no file path."""
    state = {
        "task": "Create an S3 bucket",
        "terraform_code": "",
        "terraform_file_path": "",
        "result": "",
        "error": "",
        "user_input": "",
        "next_action": ""
    }

    result = terraform_plan(state)

    assert result["error"] == "No Terraform file path provided"
    assert result["next_action"] == ACTION_USER_INTERACTION


@patch('subprocess.run')
def test_terraform_plan_success(mock_run, mock_state):
    """Test successful terraform plan execution."""
    mock_run.return_value = MagicMock(
        stdout="Plan: 1 to add, 0 to change, 0 to destroy.",
        stderr=""
    )

    result = terraform_plan(mock_state)

    assert "Plan: 1 to add" in result["result"]
    assert result["next_action"] == ACTION_APPROVE_PLAN
    assert not result["error"]


@patch('subprocess.run')
def test_terraform_plan_init_failure(mock_run, mock_state):
    """Test terraform plan with init failure."""
    mock_run.side_effect = Exception("Failed to initialize")

    result = terraform_plan(mock_state)

    assert "Error in terraform_plan" in result["error"]
    assert result["next_action"] == ACTION_USER_INTERACTION


@patch('subprocess.run')
def test_terraform_plan_execution_failure(mock_run, mock_state):
    """Test terraform plan execution failure."""
    mock_run.side_effect = [
        MagicMock(stdout="", stderr=""),  # init succeeds
        Exception("Plan failed")  # plan fails
    ]

    result = terraform_plan(mock_state)

    assert "Error in terraform_plan" in result["error"]
    assert result["next_action"] == ACTION_USER_INTERACTION


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
        "next_action": ACTION_APPROVE_PLAN
    }

    # Run the approval node
    new_state = plan_approval(state)

    # Check the state was updated correctly
    assert new_state["next_action"] == ACTION_EXECUTE
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
        "next_action": ACTION_APPROVE_PLAN
    }

    # Run the approval node
    new_state = plan_approval(state)

    # Check the state was updated correctly
    assert new_state["next_action"] == ACTION_GENERATE
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
        "next_action": ACTION_APPROVE_PLAN
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
        "next_action": ACTION_APPROVE_PLAN
    }

    # Run the approval node
    new_state = plan_approval(state)

    # Check error handling
    assert new_state["next_action"] == "user_interaction"
    assert new_state["error"] == "Failed to create plan"