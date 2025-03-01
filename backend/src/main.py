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

# Load environment variables
load_dotenv()

def build_graph() -> StateGraph:
    """Build the LangGraph for Cloud Pilot."""
    # Initialize the graph
    graph = StateGraph(CloudPilotState)

    # Add nodes
    graph.add_node("analyze_terraform", analyze_terraform)
    graph.add_node("generate_terraform", generate_terraform)
    graph.add_node("execute_terraform", execute_terraform)
    graph.add_node("file_system_operations", file_system_operations)
    graph.add_node("user_interaction", user_interaction)
    graph.add_node("terraform_plan", terraform_plan)
    graph.add_node("plan_approval", plan_approval)

    # Define edges

    # From user_interaction, decide what to do next
    graph.add_conditional_edges(
        "user_interaction",
        lambda state: state["next_action"],
        {
            "analyze": "analyze_terraform",
            "generate": "generate_terraform",
            "execute": "execute_terraform",
            "file_ops": "file_system_operations",
            "plan": "terraform_plan",
            "end": END,
        }
    )

    # From analyze_terraform, go to generate_terraform
    graph.add_edge("analyze_terraform", "generate_terraform")

    # From generate_terraform, go to terraform_plan
    graph.add_edge("generate_terraform", "terraform_plan")

    # From terraform_plan, go to plan_approval or user_interaction based on result
    graph.add_conditional_edges(
        "terraform_plan",
        lambda state: state["next_action"],
        {
            "plan_approval": "plan_approval",
            "user_interaction": "user_interaction"
        }
    )

    # From plan_approval, go to execute_terraform, generate_terraform, or user_interaction
    graph.add_conditional_edges(
        "plan_approval",
        lambda state: state["next_action"],
        {
            "execute_terraform": "execute_terraform",
            "generate_terraform": "generate_terraform",
            "user_interaction": "user_interaction"
        }
    )

    # From execute_terraform, go to user_interaction
    graph.add_edge("execute_terraform", "user_interaction")

    # From file_system_operations, go to user_interaction
    graph.add_edge("file_system_operations", "user_interaction")

    # Set the entry point
    graph.set_entry_point("user_interaction")

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
        "next_action": "analyze"
    }

    # Run the graph
    for state in app.stream(initial_state):
        current_node = state.current_node
        if current_node:
            print(f"Executing node: {current_node}")

    print("Cloud Pilot execution completed.")



if __name__ == "__main__":
    main()