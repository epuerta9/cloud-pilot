"""Node for performing file system operations."""

import os
import shutil
import glob
from typing import Dict

from llama_index.llms.openai import OpenAI

# Import the CloudPilotState type
from src.main import CloudPilotState


def file_system_operations(state: CloudPilotState) -> CloudPilotState:
    """
    Perform file system operations based on user input.
    
    Args:
        state: The current state of the graph
        
    Returns:
        Updated state with file operation results
    """
    # Create a copy of the state to modify
    new_state = state.copy()
    
    try:
        # Check if we have user input
        if not state["user_input"]:
            new_state["error"] = "No file system operation specified"
            return new_state
        
        # Initialize the LLM to interpret the user's request
        llm = OpenAI(model="gpt-4")
        
        # Parse the user's request to determine the file operation
        prompt = f"""
        Parse the following user request for a file system operation:
        "{state["user_input"]}"
        
        Determine:
        1. The type of operation (list, copy, move, delete, create, read)
        2. The source path(s)
        3. The destination path (if applicable)
        4. The content (if creating a file)
        
        Return a JSON object with these fields:
        {{
            "operation": "list|copy|move|delete|create|read",
            "source": "path/to/source",
            "destination": "path/to/destination",
            "content": "file content if creating"
        }}
        
        Only include relevant fields. Return only the JSON, no explanations.
        """
        
        response = llm.complete(prompt)
        
        # Parse the response to get the operation details
        import json
        try:
            operation_details = json.loads(response.text)
        except json.JSONDecodeError:
            new_state["error"] = "Failed to parse operation details"
            return new_state
        
        # Perform the requested operation
        operation = operation_details.get("operation", "").lower()
        source = operation_details.get("source", "")
        destination = operation_details.get("destination", "")
        content = operation_details.get("content", "")
        
        result = ""
        
        if operation == "list":
            # List files in a directory
            if os.path.isdir(source):
                files = os.listdir(source)
                result = f"Files in {source}:\n" + "\n".join(files)
            else:
                # Try using glob pattern
                files = glob.glob(source)
                result = f"Files matching {source}:\n" + "\n".join(files)
        
        elif operation == "copy":
            # Copy a file or directory
            if os.path.isfile(source):
                shutil.copy2(source, destination)
                result = f"Copied file from {source} to {destination}"
            elif os.path.isdir(source):
                shutil.copytree(source, destination)
                result = f"Copied directory from {source} to {destination}"
            else:
                new_state["error"] = f"Source not found: {source}"
                return new_state
        
        elif operation == "move":
            # Move a file or directory
            shutil.move(source, destination)
            result = f"Moved from {source} to {destination}"
        
        elif operation == "delete":
            # Delete a file or directory
            if os.path.isfile(source):
                os.remove(source)
                result = f"Deleted file: {source}"
            elif os.path.isdir(source):
                shutil.rmtree(source)
                result = f"Deleted directory: {source}"
            else:
                new_state["error"] = f"Source not found: {source}"
                return new_state
        
        elif operation == "create":
            # Create a file with content
            os.makedirs(os.path.dirname(source), exist_ok=True)
            with open(source, "w") as f:
                f.write(content)
            result = f"Created file: {source}"
        
        elif operation == "read":
            # Read a file
            if os.path.isfile(source):
                with open(source, "r") as f:
                    content = f.read()
                result = f"Content of {source}:\n{content}"
            else:
                new_state["error"] = f"File not found: {source}"
                return new_state
        
        else:
            new_state["error"] = f"Unknown operation: {operation}"
            return new_state
        
        # Update the state with the operation result
        new_state["result"] = result
        new_state["error"] = ""
        
    except Exception as e:
        new_state["error"] = f"Error performing file system operation: {str(e)}"
    
    return new_state 