"""Main entry point for the Cloud Pilot application."""

import os
from typing import Dict, Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage

from src.nodes.generate_terraform import generate_terraform
from src.nodes.analyze_terraform import analyze_terraform
from src.nodes.terraform_plan import terraform_plan

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


def build_example_graph() -> StateGraph:
    """Build the Terraform generation workflow graph."""
    
    # Create the graph with our state type
    graph = StateGraph(State)
    
    # Add nodes for each step
    graph.add_node("generate", generate_terraform)
    graph.add_node("plan", terraform_plan)
    
    # Add edges to define the workflow
    graph.add_edge("generate", "plan")
    graph.add_edge("plan", END)
    
    # Set the entry point
    graph.set_entry_point("generate")
    
    return graph.compile()


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