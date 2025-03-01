"""Main entry point for the Cloud Pilot application."""

import os
from typing import Dict, Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

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


def example_node(state: Dict) -> Dict:
    """Example node that just updates state."""
    new_state = state.copy()
    new_state["result"] = f"Processed task: {state['messages'][-1]['content']}"
    new_state["messages"] = [{"role": "assistant", "content": new_state["result"]}]
    new_state["next_action"] = "end"
    return new_state


def build_example_graph() -> StateGraph:
    """Build a minimal example graph."""
    
    # Create the graph with our state type
    graph = StateGraph(State)
    
    # Add a single node
    graph.add_node("process", example_node)
    
    # Add edge to END
    graph.add_edge("process", END)
    
    # Set the entry point
    graph.set_entry_point("process")
    
    return graph


# Build graph at module level for streaming
graph = build_example_graph()


def stream_graph_updates(user_input: str):
    """Stream updates from the graph execution."""
    # for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
    #     for value in event.values():
    #         print("Assistant:", value["messages"][-1]["content"])
    graph.invoke({"messages": [{"role": "user", "content": user_input}]})

def main():
    """Run an interactive example workflow."""
    print("\n=== Starting Interactive Test ===")
    print("Type 'quit', 'exit', or 'q' to end the session")
    
    while True:
        try:
            user_input = input("\nUser: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            stream_graph_updates(user_input)
            
        except Exception as e:
            # fallback if input() is not available
            user_input = "What do you know about LangGraph?"
            print("User: " + user_input)
            stream_graph_updates(user_input)
            break
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    main()