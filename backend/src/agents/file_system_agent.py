"""File system agent for Cloud Pilot."""

import os
import shutil
import glob
from typing import Dict, List, Optional

from llama_index.llms.anthropic import Anthropic
from llama_index.core import Settings
from llama_index.core.tools import BaseTool, FunctionTool
from src.constants import ANTHROPIC_MODEL

class FileSystemAgent:
    """Agent for performing file system operations."""

    def __init__(self, model_name: str = ANTHROPIC_MODEL):
        """
        Initialize the file system agent.

        Args:
            model_name: The name of the Anthropic model to use
        """
        self.llm = Anthropic(model=model_name)
        self.tools = self._create_tools()

    def _create_tools(self) -> List[BaseTool]:
        """Create tools for the agent to use."""
        tools = [
            FunctionTool.from_defaults(
                name="list_files",
                fn=self.list_files,
                description="List files in a directory"
            ),
            FunctionTool.from_defaults(
                name="read_file",
                fn=self.read_file,
                description="Read a file from disk"
            ),
            FunctionTool.from_defaults(
                name="write_file",
                fn=self.write_file,
                description="Write content to a file"
            ),
            FunctionTool.from_defaults(
                name="copy_file",
                fn=self.copy_file,
                description="Copy a file or directory"
            ),
            FunctionTool.from_defaults(
                name="move_file",
                fn=self.move_file,
                description="Move a file or directory"
            ),
            FunctionTool.from_defaults(
                name="delete_file",
                fn=self.delete_file,
                description="Delete a file or directory"
            ),
            FunctionTool.from_defaults(
                name="create_directory",
                fn=self.create_directory,
                description="Create a directory"
            ),
        ]
        return tools

    def list_files(self, path: str) -> List[str]:
        """
        List files in a directory.

        Args:
            path: Path to the directory

        Returns:
            List of files in the directory
        """
        try:
            if os.path.isdir(path):
                return os.listdir(path)
            else:
                # Try using glob pattern
                return glob.glob(path)
        except Exception as e:
            return [f"Error listing files: {str(e)}"]

    def read_file(self, file_path: str) -> str:
        """
        Read a file from disk.

        Args:
            file_path: Path to the file

        Returns:
            The contents of the file
        """
        try:
            with open(file_path, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def write_file(self, file_path: str, content: str) -> str:
        """
        Write content to a file.

        Args:
            file_path: Path to write the file to
            content: The content to write

        Returns:
            A success or error message
        """
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "w") as f:
                f.write(content)

            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    def copy_file(self, source: str, destination: str) -> str:
        """
        Copy a file or directory.

        Args:
            source: Source path
            destination: Destination path

        Returns:
            A success or error message
        """
        try:
            if os.path.isfile(source):
                shutil.copy2(source, destination)
                return f"Copied file from {source} to {destination}"
            elif os.path.isdir(source):
                shutil.copytree(source, destination)
                return f"Copied directory from {source} to {destination}"
            else:
                return f"Source not found: {source}"
        except Exception as e:
            return f"Error copying: {str(e)}"

    def move_file(self, source: str, destination: str) -> str:
        """
        Move a file or directory.

        Args:
            source: Source path
            destination: Destination path

        Returns:
            A success or error message
        """
        try:
            shutil.move(source, destination)
            return f"Moved from {source} to {destination}"
        except Exception as e:
            return f"Error moving: {str(e)}"

    def delete_file(self, path: str) -> str:
        """
        Delete a file or directory.

        Args:
            path: Path to delete

        Returns:
            A success or error message
        """
        try:
            if os.path.isfile(path):
                os.remove(path)
                return f"Deleted file: {path}"
            elif os.path.isdir(path):
                shutil.rmtree(path)
                return f"Deleted directory: {path}"
            else:
                return f"Path not found: {path}"
        except Exception as e:
            return f"Error deleting: {str(e)}"

    def create_directory(self, path: str) -> str:
        """
        Create a directory.

        Args:
            path: Path to create

        Returns:
            A success or error message
        """
        try:
            os.makedirs(path, exist_ok=True)
            return f"Created directory: {path}"
        except Exception as e:
            return f"Error creating directory: {str(e)}"

    def parse_file_operation(self, user_input: str) -> Dict:
        """
        Parse a user's request for a file system operation.

        Args:
            user_input: The user's request

        Returns:
            A dictionary with the parsed operation details
        """
        prompt = f"""
        Parse the following user request for a file system operation:
        "{user_input}"

        Determine:
        1. The type of operation (list, read, write, copy, move, delete, create_dir)
        2. The source path(s)
        3. The destination path (if applicable)
        4. The content (if writing a file)

        Return a JSON object with these fields:
        {{
            "operation": "list|read|write|copy|move|delete|create_dir",
            "source": "path/to/source",
            "destination": "path/to/destination",
            "content": "file content if writing"
        }}

        Only include relevant fields. Return only the JSON, no explanations.
        """

        response = self.llm.complete(prompt)

        # Parse the response to get the operation details
        import json
        try:
            operation_details = json.loads(response.text)
            return operation_details
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse operation details",
                "raw_response": response.text
            }

    def execute_operation(self, operation_details: Dict) -> str:
        """
        Execute a file system operation based on the parsed details.

        Args:
            operation_details: The parsed operation details

        Returns:
            The result of the operation
        """
        operation = operation_details.get("operation", "").lower()
        source = operation_details.get("source", "")
        destination = operation_details.get("destination", "")
        content = operation_details.get("content", "")

        if operation == "list":
            files = self.list_files(source)
            return f"Files in {source}:\n" + "\n".join(files)

        elif operation == "read":
            return self.read_file(source)

        elif operation == "write":
            return self.write_file(source, content)

        elif operation == "copy":
            return self.copy_file(source, destination)

        elif operation == "move":
            return self.move_file(source, destination)

        elif operation == "delete":
            return self.delete_file(source)

        elif operation == "create_dir":
            return self.create_directory(source)

        else:
            return f"Unknown operation: {operation}"