"""Tests for the Cloud Pilot graph."""

import pytest
from unittest.mock import patch, MagicMock

from src.main import build_graph
from src.constants import (
    NODE_ANALYZE_TERRAFORM, NODE_GENERATE_TERRAFORM, NODE_EXECUTE_TERRAFORM,
    NODE_FILE_SYSTEM_OPERATIONS, NODE_USER_INTERACTION, NODE_TERRAFORM_PLAN,
    NODE_PLAN_APPROVAL, ACTION_ANALYZE, ACTION_GENERATE, ACTION_EXECUTE,
    ACTION_FILE_OPS, ACTION_PLAN, ACTION_END
)

@pytest.fixture
def mock_nodes():
    """Create mock nodes for testing."""
    with patch("src.main.analyze_terraform") as mock_analyze, \
         patch("src.main.generate_terraform") as mock_generate, \
         patch("src.main.execute_terraform") as mock_execute, \
         patch("src.main.file_system_operations") as mock_file_ops, \
         patch("src.main.terraform_plan") as mock_plan, \
         patch("src.main.plan_approval") as mock_approval, \
         patch("src.main.user_interaction") as mock_user:

        # Configure mock returns
        mock_analyze.return_value = {"next_action": ACTION_GENERATE}
        mock_generate.return_value = {"next_action": ACTION_PLAN}
        mock_execute.return_value = {"next_action": ACTION_END}
        mock_file_ops.return_value = {"next_action": ACTION_END}
        mock_plan.return_value = {"next_action": ACTION_END}
        mock_approval.return_value = {"next_action": ACTION_END}
        mock_user.return_value = {"next_action": ACTION_ANALYZE}

        yield {
            NODE_ANALYZE_TERRAFORM: mock_analyze,
            NODE_GENERATE_TERRAFORM: mock_generate,
            NODE_EXECUTE_TERRAFORM: mock_execute,
            NODE_FILE_SYSTEM_OPERATIONS: mock_file_ops,
            NODE_TERRAFORM_PLAN: mock_plan,
            NODE_PLAN_APPROVAL: mock_approval,
            NODE_USER_INTERACTION: mock_user
        }

def test_graph_initialization(mock_nodes):
    """Test that the graph is initialized with all required nodes."""
    graph = build_graph()

    # Check that all nodes are present
    assert NODE_ANALYZE_TERRAFORM in graph.nodes
    assert NODE_GENERATE_TERRAFORM in graph.nodes
    assert NODE_EXECUTE_TERRAFORM in graph.nodes
    assert NODE_FILE_SYSTEM_OPERATIONS in graph.nodes
    assert NODE_USER_INTERACTION in graph.nodes
    assert NODE_TERRAFORM_PLAN in graph.nodes
    assert NODE_PLAN_APPROVAL in graph.nodes

def test_analyze_flow(mock_nodes):
    """Test the flow from user_interaction to analyze_terraform to generate_terraform."""
    graph = build_graph()
    app = graph.compile()

    # Initial state
    initial_state = {
        "task": "Create an S3 bucket",
        "terraform_code": "",
        "terraform_file_path": "test.tf",
        "result": "",
        "error": "",
        "user_input": "",
        "next_action": ACTION_ANALYZE
    }

    # Run the graph
    for _ in app.stream(initial_state):
        pass

    # Verify the flow
    assert mock_nodes[NODE_USER_INTERACTION].called
    assert mock_nodes[NODE_ANALYZE_TERRAFORM].called
    assert mock_nodes[NODE_GENERATE_TERRAFORM].called

def test_generate_flow(mock_nodes):
    """Test the flow from user_interaction to generate_terraform."""
    # Modify the user_interaction mock to return "generate"
    mock_nodes[NODE_USER_INTERACTION].side_effect = lambda state: {
        "next_action": ACTION_GENERATE
    }

    graph = build_graph()
    app = graph.compile()

    # Initial state
    initial_state = {
        "task": "Create an S3 bucket",
        "terraform_code": "",
        "terraform_file_path": "",
        "result": "",
        "error": "",
        "user_input": "",
        "next_action": ACTION_GENERATE
    }

    # Run the graph
    for _ in app.stream(initial_state):
        pass

    # Verify the flow
    assert mock_nodes[NODE_USER_INTERACTION].called
    assert mock_nodes[NODE_GENERATE_TERRAFORM].called

def test_execute_flow(mock_nodes):
    """Test the flow from user_interaction to execute_terraform."""
    # Modify the user_interaction mock to return "execute"
    mock_nodes[NODE_USER_INTERACTION].side_effect = lambda state: {
        "next_action": ACTION_EXECUTE
    }

    graph = build_graph()
    app = graph.compile()

    # Initial state
    initial_state = {
        "task": "Apply Terraform changes",
        "terraform_code": "resource \"aws_s3_bucket\" \"test\" {}",
        "terraform_file_path": "test.tf",
        "result": "",
        "error": "",
        "user_input": "",
        "next_action": ACTION_EXECUTE
    }

    # Run the graph
    for _ in app.stream(initial_state):
        pass

    # Verify the flow
    assert mock_nodes[NODE_USER_INTERACTION].called
    assert mock_nodes[NODE_EXECUTE_TERRAFORM].called

def test_file_ops_flow(mock_nodes):
    """Test the flow from user_interaction to file_system_operations."""
    # Modify the user_interaction mock to return "file_ops"
    mock_nodes[NODE_USER_INTERACTION].side_effect = lambda state: {
        "next_action": ACTION_FILE_OPS
    }

    graph = build_graph()
    app = graph.compile()

    # Initial state
    initial_state = {
        "task": "List Terraform files",
        "terraform_code": "",
        "terraform_file_path": "",
        "result": "",
        "error": "",
        "user_input": "list files",
        "next_action": ACTION_FILE_OPS
    }

    # Run the graph
    for _ in app.stream(initial_state):
        pass

    # Verify the flow
    assert mock_nodes[NODE_USER_INTERACTION].called
    assert mock_nodes[NODE_FILE_SYSTEM_OPERATIONS].called

def test_end_flow(mock_nodes):
    """Test the flow from user_interaction to END."""
    # Modify the user_interaction mock to return "end"
    mock_nodes[NODE_USER_INTERACTION].side_effect = lambda state: {
        "next_action": ACTION_END
    }

    graph = build_graph()
    app = graph.compile()

    # Initial state
    initial_state = {
        "task": "Exit",
        "terraform_code": "",
        "terraform_file_path": "",
        "result": "",
        "error": "",
        "user_input": "",
        "next_action": ACTION_END
    }

    # Run the graph
    for _ in app.stream(initial_state):
        pass

    # Check that only the user_interaction node was called
    assert mock_nodes[NODE_USER_INTERACTION].called
    assert not mock_nodes[NODE_ANALYZE_TERRAFORM].called
    assert not mock_nodes[NODE_GENERATE_TERRAFORM].called