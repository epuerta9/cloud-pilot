"""Client for interacting with the Cloud Pilot LangGraph server."""

import sys
from typing import Optional
from langgraph_sdk import get_sync_client
from langgraph.types import Command
from rich.console import Console
from rich.markdown import Markdown
import json
console = Console()

class CloudPilotClient:
    """Client for interacting with the Cloud Pilot service."""

    def __init__(self, url: str = "http://localhost:2024"):
        """Initialize the client."""
        self.client = get_sync_client(url=url)
        self.thread_id = self.create_thread()
        self.current_run_id = None

    def create_thread(self) -> str:
        """Create a new thread for conversation."""
        thread = self.client.threads.create()
        # The response is a dict with thread_id key
        self.thread_id = thread["thread_id"]
        return self.thread_id

    def handle_interrupt(self, run_id: str) -> None:
        """Handle an interrupt by getting user input and resuming."""
        # Get user approval
        user_input = input("\nDo you approve? (y/n): ").lower().strip()
        approved = user_input.startswith('y')
        
        # Resume the run with user's response
        self.client.runs.create(self.thread_id,"agent", command=Command(resume={"approved": approved}))

    def chat(self, message: str) -> None:
        """
        Send a message to the Cloud Pilot service and stream the response.

        Args:
            message: The user's message
        """
        try:
            # # Create thread if needed


            # Stream the response
            input_data = {
                "messages": [{
                    "role": "user",
                    "content": message,
                }]
            }

            

            for chunk in self.client.runs.stream(
                self.thread_id,
                "agent",
                input=input_data,
                stream_mode="updates",
            ):
                print(f"Receiving new event of type: {chunk.event}...")
                print(chunk.data)
                print("\n\n")

                # Print event type for debugging
                console.print(f"\n[dim]Event: {chunk.event}[/dim]")

                # Handle interrupts
                if "__interrupt__" in chunk.data:
                    self.handle_interrupt(self.current_run_id)
                    continue

                if chunk.event == "message":
                    # Print assistant messages
                    if "messages" in chunk.data:
                        for msg in chunk.data["messages"]:
                            if msg["role"] == "assistant":
                                console.print(Markdown(msg["content"]))

                elif chunk.event == "terraform":
                    # Print Terraform related updates
                    if "terraform_code" in chunk.data:
                        console.print("\n[bold blue]Generated Terraform Code:[/bold blue]")
                        console.print(chunk.data["terraform_code"])
                    if "result" in chunk.data:
                        console.print("\n[bold green]Terraform Result:[/bold green]")
                        console.print(Markdown(chunk.data["result"]))

                elif chunk.event == "error":
                    # Print any errors
                    if "error" in chunk.data:
                        console.print(f"\n[bold red]Error:[/bold red] {chunk.data['error']}")

        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}")

def main():
    """Run the client in interactive mode."""
    client = CloudPilotClient()
    
    console.print("\n[bold green]=== Cloud Pilot Client ===[/bold green]")
    console.print("Type your infrastructure requirements or 'quit' to exit")

    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            # Check for exit command
            if user_input.lower() in ['quit', 'exit', 'q']:
                console.print("\n[bold green]Goodbye![/bold green]")
                break
            
            # Process the message
            client.chat(user_input)

        except KeyboardInterrupt:
            console.print("\n[bold yellow]Session interrupted[/bold yellow]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
            break

if __name__ == "__main__":
    main()
