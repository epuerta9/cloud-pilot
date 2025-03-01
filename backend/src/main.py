"""Main entry point for the Cloud Pilot application."""

import os
from typing import Annotated, Dict, Union

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

# Import nodes
from src.nodes.analyze_terraform import analyze_terraform
from src.nodes.generate_terraform import generate_terraform
from src.nodes.execute_terraform import execute_terraform
from src.nodes.file_system_operations import file_system_operations
from src.nodes.user_interaction import user_interaction
from src.nodes.terraform_plan import terraform_plan
from src.nodes.plan_approval import plan_approval
from src.state import CloudPilotState
from src.constants import (
    NODE_ANALYZE_TERRAFORM, NODE_GENERATE_TERRAFORM, NODE_EXECUTE_TERRAFORM,
    NODE_FILE_SYSTEM_OPERATIONS, NODE_USER_INTERACTION, NODE_TERRAFORM_PLAN,
    NODE_PLAN_APPROVAL, ACTION_ANALYZE, ACTION_GENERATE, ACTION_EXECUTE,
    ACTION_FILE_OPS, ACTION_PLAN, ACTION_APPROVE_PLAN, ACTION_USER_INTERACTION,
    ACTION_END
)

# Load environment variables
load_dotenv()

def build_graph() -> StateGraph:
    """Build the LangGraph for Cloud Pilot."""
    # Initialize the graph
    graph = StateGraph(CloudPilotState)

    # Add nodes
    graph.add_node(NODE_ANALYZE_TERRAFORM, analyze_terraform)
    graph.add_node(NODE_GENERATE_TERRAFORM, generate_terraform)
    graph.add_node(NODE_EXECUTE_TERRAFORM, execute_terraform)
    graph.add_node(NODE_FILE_SYSTEM_OPERATIONS, file_system_operations)
    graph.add_node(NODE_USER_INTERACTION, user_interaction)
    graph.add_node(NODE_TERRAFORM_PLAN, terraform_plan)
    graph.add_node(NODE_PLAN_APPROVAL, plan_approval)

    # Define edges

    # From user_interaction, decide what to do next
    graph.add_conditional_edges(
        NODE_USER_INTERACTION,
        lambda state: state["next_action"],
        {
            ACTION_ANALYZE: NODE_ANALYZE_TERRAFORM,
            ACTION_GENERATE: NODE_GENERATE_TERRAFORM,
            ACTION_EXECUTE: NODE_EXECUTE_TERRAFORM,
            ACTION_FILE_OPS: NODE_FILE_SYSTEM_OPERATIONS,
            ACTION_PLAN: NODE_TERRAFORM_PLAN,
            ACTION_END: END,
        }
    )

    # From analyze_terraform, go to generate_terraform
    graph.add_edge(NODE_ANALYZE_TERRAFORM, NODE_GENERATE_TERRAFORM)

    # From generate_terraform, go to terraform_plan
    graph.add_edge(NODE_GENERATE_TERRAFORM, NODE_TERRAFORM_PLAN)

    # From terraform_plan, go to plan_approval or user_interaction based on result
    graph.add_conditional_edges(
        NODE_TERRAFORM_PLAN,
        lambda state: state["next_action"],
        {
            ACTION_APPROVE_PLAN: NODE_PLAN_APPROVAL,
            ACTION_USER_INTERACTION: NODE_USER_INTERACTION
        }
    )

    # From plan_approval, go to execute_terraform, generate_terraform, or user_interaction
    graph.add_conditional_edges(
        NODE_PLAN_APPROVAL,
        lambda state: state["next_action"],
        {
            ACTION_EXECUTE: NODE_EXECUTE_TERRAFORM,
            ACTION_GENERATE: NODE_GENERATE_TERRAFORM,
            ACTION_USER_INTERACTION: NODE_USER_INTERACTION
        }
    )

    # From execute_terraform, go to user_interaction
    graph.add_edge(NODE_EXECUTE_TERRAFORM, NODE_USER_INTERACTION)

    # From file_system_operations, go to user_interaction
    graph.add_edge(NODE_FILE_SYSTEM_OPERATIONS, NODE_USER_INTERACTION)

    # Set the entry point
    graph.set_entry_point(NODE_USER_INTERACTION)

    return graph


def main():
    """Run the Cloud Pilot application."""
    # Build the graph
    graph = build_graph()

    # Compile the graph
    app = graph.compile()

    # Initial state
    initial_state = {
        "task": "Create an AWS S3 bucket using Terraform",
        "terraform_code": "",
        "terraform_file_path": "",
        "result": "",
        "error": "",
        "user_input": "",
        "next_action": ACTION_ANALYZE
    }

    # Run the graph
    for state in app.stream(initial_state):
        current_node = state.current_node
        if current_node:
            print(f"Executing node: {current_node}")

    print("Cloud Pilot execution completed.")



if __name__ == "__main__":
    main()