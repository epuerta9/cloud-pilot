"""Tests for the file system agent."""

import os
import pytest
from unittest.mock import patch, MagicMock

from src.agents.file_system_agent import FileSystemAgent


@pytest.fixture
def file_system_agent():
    """Create a FileSystemAgent instance for testing."""
    with patch("src.agents.file_system_agent.OpenAI") as mock_openai:
        # Mock the OpenAI LLM
        mock_llm = MagicMock()
        mock_openai.return_value = mock_llm
        
        agent = FileSystemAgent()
        agent.llm = mock_llm
        yield agent


def test_list_files(file_system_agent, tmp_path):
    """Test listing files in a directory."""
    # Create some temporary files
    (tmp_path / "file1.txt").write_text("content1")
    (tmp_path / "file2.txt").write_text("content2")
    
    # Test listing files
    files = file_system_agent.list_files(str(tmp_path))
    
    assert "file1.txt" in files
    assert "file2.txt" in files
    assert len(files) == 2


def test_read_file(file_system_agent, tmp_path):
    """Test reading a file."""
    # Create a temporary file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello, world!")
    
    # Test reading the file
    content = file_system_agent.read_file(str(test_file))
    
    assert content == "Hello, world!"


def test_write_file(file_system_agent, tmp_path):
    """Test writing a file."""
    # Define the file path and content
    test_file = tmp_path / "output.txt"
    content = "This is a test file."
    
    # Test writing the file
    result = file_system_agent.write_file(str(test_file), content)
    
    assert "Successfully wrote" in result
    assert test_file.exists()
    assert test_file.read_text() == content


def test_copy_file(file_system_agent, tmp_path):
    """Test copying a file."""
    # Create a source file
    source_file = tmp_path / "source.txt"
    source_file.write_text("Source content")
    
    # Define the destination path
    dest_file = tmp_path / "dest.txt"
    
    # Test copying the file
    result = file_system_agent.copy_file(str(source_file), str(dest_file))
    
    assert "Copied file" in result
    assert dest_file.exists()
    assert dest_file.read_text() == "Source content"


def test_move_file(file_system_agent, tmp_path):
    """Test moving a file."""
    # Create a source file
    source_file = tmp_path / "source.txt"
    source_file.write_text("Source content")
    
    # Define the destination path
    dest_file = tmp_path / "dest.txt"
    
    # Test moving the file
    result = file_system_agent.move_file(str(source_file), str(dest_file))
    
    assert "Moved from" in result
    assert dest_file.exists()
    assert not source_file.exists()
    assert dest_file.read_text() == "Source content"


def test_delete_file(file_system_agent, tmp_path):
    """Test deleting a file."""
    # Create a file to delete
    test_file = tmp_path / "delete_me.txt"
    test_file.write_text("Delete me")
    
    # Test deleting the file
    result = file_system_agent.delete_file(str(test_file))
    
    assert "Deleted file" in result
    assert not test_file.exists()


def test_create_directory(file_system_agent, tmp_path):
    """Test creating a directory."""
    # Define the directory path
    test_dir = tmp_path / "new_dir"
    
    # Test creating the directory
    result = file_system_agent.create_directory(str(test_dir))
    
    assert "Created directory" in result
    assert test_dir.exists()
    assert test_dir.is_dir()


def test_parse_file_operation(file_system_agent):
    """Test parsing a file operation request."""
    # Mock the LLM response
    mock_response = MagicMock()
    mock_response.text = '{"operation": "read", "source": "/path/to/file.txt"}'
    file_system_agent.llm.complete.return_value = mock_response
    
    # Test parsing a file operation request
    user_input = "Read the file at /path/to/file.txt"
    result = file_system_agent.parse_file_operation(user_input)
    
    assert file_system_agent.llm.complete.called
    assert result["operation"] == "read"
    assert result["source"] == "/path/to/file.txt"


def test_execute_operation(file_system_agent, tmp_path):
    """Test executing a file operation."""
    # Create a test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test content")
    
    # Define the operation details
    operation_details = {
        "operation": "read",
        "source": str(test_file)
    }
    
    # Test executing the operation
    result = file_system_agent.execute_operation(operation_details)
    
    assert "Test content" in result 