"""Main entry point for the Cloud Pilot application."""

import os
from typing import Dict, Annotated, Literal
from typing import Dict, Annotated, Literal
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver
from src.nodes.generate_terraform import generate_terraform
from src.nodes.terraform_plan import terraform_plan
from src.nodes.plan_approval import plan_approval, handle_plan_feedback
from src.nodes.execute_terraform import execute_terraform

from src.constants import (
    NODE_GENERATE_TERRAFORM, NODE_TERRAFORM_PLAN, NODE_PLAN_APPROVAL,
    NODE_EXECUTE_TERRAFORM, ACTION_EXECUTE, ACTION_GENERATE, ACTION_USER_INTERACTION
)

class State(TypedDict):
    """State definition for the graph."""
    messages: Annotated[list, add_messages]
    task: str
    terraform_code: str
    terraform_file_path: str
    terraform_built: bool
    result: str
    error: str
    user_input: str
    next_action: str


def human_approval(state: Dict) -> Command[Literal["plan", "generate"]]:
    """Node for human approval of generated terraform."""
    # Copy state to preserve previous state
    new_state = state.copy()

    # Get approval from human
    is_approved = input("\nIs this correct? (y/n): ").lower().startswith('y')

    # Return command to route to next node
    if is_approved:
        return Command(goto="plan")
    else:
        return Command(goto="generate")


def human_approval(state: Dict) -> Command[Literal["plan", "generate"]]:
    """Node for human approval of generated terraform."""
    # Copy state to preserve previous state
    new_state = state.copy()

    # Get approval from human
    is_approved = input("\nIs this correct? (y/n): ").lower().startswith('y')

    # Return command to route to next node
    if is_approved:
        return Command(goto="plan")
    else:
        return Command(goto="generate")


def build_example_graph() -> StateGraph:
    """Build the Terraform generation workflow graph."""

    # Create the graph with our state type
    graph = StateGraph(State)

    # Add nodes for each step
    graph.add_node(NODE_GENERATE_TERRAFORM, generate_terraform)
    graph.add_node(NODE_TERRAFORM_PLAN, terraform_plan)
    graph.add_node(NODE_PLAN_APPROVAL, plan_approval)
    graph.add_node(NODE_EXECUTE_TERRAFORM, execute_terraform)

    # Add edges to define the workflow
    graph.add_edge(NODE_GENERATE_TERRAFORM, NODE_TERRAFORM_PLAN)
    graph.add_edge(NODE_TERRAFORM_PLAN, NODE_PLAN_APPROVAL)

    # Add conditional edges from plan_approval based on user feedback
    # graph.add_conditional_edges(
    #     NODE_PLAN_APPROVAL,
    #     handle_plan_feedback,
    #     {
    #         ACTION_EXECUTE: NODE_EXECUTE_TERRAFORM,
    #         ACTION_GENERATE: NODE_GENERATE_TERRAFORM,
    #         ACTION_USER_INTERACTION: END
    #     }
    # )

    # Add edge from execute to end
    graph.add_edge(NODE_EXECUTE_TERRAFORM, END)

    # Set the entry point
    graph.set_entry_point(NODE_GENERATE_TERRAFORM)

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)


# Build graph at module level for streaming
graph = build_example_graph()

print(graph.get_graph().draw_mermaid())


def stream_graph_updates(user_input: str):
    """Stream updates from the graph execution."""
    # Create initial state with user message
    message = HumanMessage(content=user_input)

    for event in graph.stream({"messages": [message]}):
        for value in event.values():
            if "messages" in value and value["messages"]:
                print("Assistant:", value["messages"][-1].content)


def main():
    """Run an interactive Terraform generation workflow."""
    print("\n=== Starting Cloud Pilot ===")
    print("Describe your infrastructure needs and I'll help generate Terraform code.")
    print("Type 'quit', 'exit', or 'q' to end the session")

    while True:
        try:
            user_input = input("\nUser: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            stream_graph_updates(user_input)

        except Exception as e:
            print(f"\nError: {str(e)}")
            break

    print("\n=== Session Complete ===")


if __name__ == "__main__":
    main()