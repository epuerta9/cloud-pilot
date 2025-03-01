"""Tests for the LangGraph."""

import pytest
from unittest.mock import patch, MagicMock

from src.main import build_graph, CloudPilotState


@pytest.fixture
def mock_nodes():
    """Mock all the nodes in the graph."""
    with patch("src.main.analyze_terraform") as mock_analyze, \
         patch("src.main.generate_terraform") as mock_generate, \
         patch("src.main.execute_terraform") as mock_execute, \
         patch("src.main.file_system_operations") as mock_file_ops, \
         patch("src.main.user_interaction") as mock_user:
        
        # Set up the mock behaviors
        def mock_analyze_fn(state):
            new_state = state.copy()
            new_state["result"] = "Analysis complete"
            return new_state
        
        def mock_generate_fn(state):
            new_state = state.copy()
            new_state["terraform_code"] = 'provider "aws" {}'
            new_state["result"] = "Generation complete"
            return new_state
        
        def mock_execute_fn(state):
            new_state = state.copy()
            new_state["result"] = "Execution complete"
            return new_state
        
        def mock_file_ops_fn(state):
            new_state = state.copy()
            new_state["result"] = "File operation complete"
            return new_state
        
        def mock_user_fn(state):
            new_state = state.copy()
            new_state["next_action"] = "analyze"  # Default to analyze
            return new_state
        
        mock_analyze.side_effect = mock_analyze_fn
        mock_generate.side_effect = mock_generate_fn
        mock_execute.side_effect = mock_execute_fn
        mock_file_ops.side_effect = mock_file_ops_fn
        mock_user.side_effect = mock_user_fn
        
        yield {
            "analyze_terraform": mock_analyze,
            "generate_terraform": mock_generate,
            "execute_terraform": mock_execute,
            "file_system_operations": mock_file_ops,
            "user_interaction": mock_user
        }


def test_build_graph():
    """Test that the graph builds correctly."""
    graph = build_graph()
    
    # Check that the graph has the expected nodes
    assert "analyze_terraform" in graph.nodes
    assert "generate_terraform" in graph.nodes
    assert "execute_terraform" in graph.nodes
    assert "file_system_operations" in graph.nodes
    assert "user_interaction" in graph.nodes


def test_graph_analyze_flow(mock_nodes):
    """Test the flow from user_interaction to analyze_terraform to generate_terraform."""
    # Build and compile the graph
    graph = build_graph()
    app = graph.compile()
    
    # Set up the initial state
    initial_state = {
        "task": "Create an S3 bucket",
        "terraform_code": "",
        "terraform_file_path": "terraform/main.tf",
        "result": "",
        "error": "",
        "user_input": "",
        "next_action": "analyze"
    }
    
    # Run the graph for a few steps
    states = list(app.stream(initial_state, max_steps=3))
    
    # Check that the nodes were called in the expected order
    assert mock_nodes["user_interaction"].called
    assert mock_nodes["analyze_terraform"].called
    assert mock_nodes["generate_terraform"].called
    
    # Check the final state
    final_state = states[-1].values
    assert final_state["result"] == "Generation complete"
    assert final_state["terraform_code"] == 'provider "aws" {}'


def test_graph_generate_flow(mock_nodes):
    """Test the flow from user_interaction to generate_terraform."""
    # Modify the user_interaction mock to return "generate"
    mock_nodes["user_interaction"].side_effect = lambda state: {
        **state,
        "next_action": "generate"
    }
    
    # Build and compile the graph
    graph = build_graph()
    app = graph.compile()
    
    # Set up the initial state
    initial_state = {
        "task": "Create an S3 bucket",
        "terraform_code": "",
        "terraform_file_path": "",
        "result": "",
        "error": "",
        "user_input": "",
        "next_action": "generate"
    }
    
    # Run the graph for a few steps
    states = list(app.stream(initial_state, max_steps=2))
    
    # Check that the nodes were called in the expected order
    assert mock_nodes["user_interaction"].called
    assert mock_nodes["generate_terraform"].called
    
    # Check the final state
    final_state = states[-1].values
    assert final_state["result"] == "Generation complete"
    assert final_state["terraform_code"] == 'provider "aws" {}'


def test_graph_execute_flow(mock_nodes):
    """Test the flow from user_interaction to execute_terraform."""
    # Modify the user_interaction mock to return "execute"
    mock_nodes["user_interaction"].side_effect = lambda state: {
        **state,
        "next_action": "execute"
    }
    
    # Build and compile the graph
    graph = build_graph()
    app = graph.compile()
    
    # Set up the initial state
    initial_state = {
        "task": "Create an S3 bucket",
        "terraform_code": 'provider "aws" {}',
        "terraform_file_path": "terraform/main.tf",
        "result": "",
        "error": "",
        "user_input": "",
        "next_action": "execute"
    }
    
    # Run the graph for a few steps
    states = list(app.stream(initial_state, max_steps=2))
    
    # Check that the nodes were called in the expected order
    assert mock_nodes["user_interaction"].called
    assert mock_nodes["execute_terraform"].called
    
    # Check the final state
    final_state = states[-1].values
    assert final_state["result"] == "Execution complete"


def test_graph_file_ops_flow(mock_nodes):
    """Test the flow from user_interaction to file_system_operations."""
    # Modify the user_interaction mock to return "file_ops"
    mock_nodes["user_interaction"].side_effect = lambda state: {
        **state,
        "next_action": "file_ops"
    }
    
    # Build and compile the graph
    graph = build_graph()
    app = graph.compile()
    
    # Set up the initial state
    initial_state = {
        "task": "Create an S3 bucket",
        "terraform_code": "",
        "terraform_file_path": "",
        "result": "",
        "error": "",
        "user_input": "List files in the terraform directory",
        "next_action": "file_ops"
    }
    
    # Run the graph for a few steps
    states = list(app.stream(initial_state, max_steps=2))
    
    # Check that the nodes were called in the expected order
    assert mock_nodes["user_interaction"].called
    assert mock_nodes["file_system_operations"].called
    
    # Check the final state
    final_state = states[-1].values
    assert final_state["result"] == "File operation complete"


def test_graph_end_flow(mock_nodes):
    """Test the flow from user_interaction to END."""
    # Modify the user_interaction mock to return "end"
    mock_nodes["user_interaction"].side_effect = lambda state: {
        **state,
        "next_action": "end"
    }
    
    # Build and compile the graph
    graph = build_graph()
    app = graph.compile()
    
    # Set up the initial state
    initial_state = {
        "task": "Create an S3 bucket",
        "terraform_code": "",
        "terraform_file_path": "",
        "result": "",
        "error": "",
        "user_input": "",
        "next_action": "end"
    }
    
    # Run the graph
    states = list(app.stream(initial_state))
    
    # Check that only the user_interaction node was called
    assert mock_nodes["user_interaction"].called
    assert not mock_nodes["analyze_terraform"].called
    assert not mock_nodes["generate_terraform"].called
    assert not mock_nodes["execute_terraform"].called
    assert not mock_nodes["file_system_operations"].called
    
    # Check that the graph ended
    assert states[-1].is_last 