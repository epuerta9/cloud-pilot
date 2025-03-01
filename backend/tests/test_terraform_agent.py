"""Tests for the Terraform agent."""

import os
import pytest
from unittest.mock import patch, MagicMock

from src.agents.terraform_agent import TerraformAgent


@pytest.fixture
def terraform_agent():
    """Create a TerraformAgent instance for testing."""
    with patch("src.agents.terraform_agent.OpenAI") as mock_openai:
        # Mock the OpenAI LLM
        mock_llm = MagicMock()
        mock_openai.return_value = mock_llm
        
        agent = TerraformAgent()
        agent.llm = mock_llm
        yield agent


def test_read_terraform_file(terraform_agent, tmp_path):
    """Test reading a Terraform file."""
    # Create a temporary Terraform file
    tf_file = tmp_path / "main.tf"
    tf_file.write_text('provider "aws" {\n  region = "us-west-2"\n}')
    
    # Test reading the file
    content = terraform_agent.read_terraform_file(str(tf_file))
    
    assert 'provider "aws"' in content
    assert 'region = "us-west-2"' in content


def test_write_terraform_file(terraform_agent, tmp_path):
    """Test writing a Terraform file."""
    # Define the file path and content
    tf_file = tmp_path / "output.tf"
    content = 'output "instance_ip" {\n  value = aws_instance.example.public_ip\n}'
    
    # Test writing the file
    result = terraform_agent.write_terraform_file(str(tf_file), content)
    
    assert "Successfully wrote" in result
    assert tf_file.exists()
    assert tf_file.read_text() == content


def test_analyze_terraform(terraform_agent):
    """Test analyzing Terraform code."""
    # Mock the LLM response
    mock_response = MagicMock()
    mock_response.text = '{"resources": [{"type": "aws_s3_bucket", "name": "example", "purpose": "Storage bucket"}], "providers": ["aws"], "variables": [], "outputs": [], "summary": "Creates an S3 bucket", "recommendations": ["Add encryption"]}'
    terraform_agent.llm.complete.return_value = mock_response
    
    # Test analyzing Terraform code
    terraform_code = 'provider "aws" {\n  region = "us-west-2"\n}\n\nresource "aws_s3_bucket" "example" {\n  bucket = "my-example-bucket"\n}'
    result = terraform_agent.analyze_terraform(terraform_code)
    
    assert terraform_agent.llm.complete.called
    assert "resources" in result
    assert result["resources"][0]["type"] == "aws_s3_bucket"
    assert result["providers"] == ["aws"]
    assert result["summary"] == "Creates an S3 bucket"


def test_generate_terraform(terraform_agent):
    """Test generating Terraform code."""
    # Mock the LLM response
    mock_response = MagicMock()
    mock_response.text = 'provider "aws" {\n  region = "us-west-2"\n}\n\nresource "aws_s3_bucket" "example" {\n  bucket = "my-example-bucket"\n}'
    terraform_agent.llm.complete.return_value = mock_response
    
    # Test generating Terraform code
    task = "Create an S3 bucket named my-example-bucket"
    result = terraform_agent.generate_terraform(task)
    
    assert terraform_agent.llm.complete.called
    assert 'provider "aws"' in result
    assert 'resource "aws_s3_bucket"' in result
    assert 'bucket = "my-example-bucket"' in result


@patch("src.agents.terraform_agent.subprocess.run")
def test_terraform_init(mock_run, terraform_agent, tmp_path):
    """Test initializing Terraform."""
    # Create a temporary directory for Terraform
    tf_dir = tmp_path / "terraform"
    tf_dir.mkdir()
    
    # Mock the subprocess.run result
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Terraform has been successfully initialized!"
    mock_run.return_value = mock_result
    
    # Test initializing Terraform
    result = terraform_agent.terraform_init(str(tf_dir))
    
    assert mock_run.called
    assert "terraform" in mock_run.call_args[0][0][0]
    assert "init" in mock_run.call_args[0][0][1]
    assert "successfully initialized" in result


@patch("src.agents.terraform_agent.subprocess.run")
def test_terraform_plan(mock_run, terraform_agent, tmp_path):
    """Test creating a Terraform plan."""
    # Create a temporary directory for Terraform
    tf_dir = tmp_path / "terraform"
    tf_dir.mkdir()
    
    # Mock the subprocess.run result
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Plan: 1 to add, 0 to change, 0 to destroy."
    mock_run.return_value = mock_result
    
    # Test creating a Terraform plan
    result = terraform_agent.terraform_plan(str(tf_dir))
    
    assert mock_run.called
    assert "terraform" in mock_run.call_args[0][0][0]
    assert "plan" in mock_run.call_args[0][0][1]
    assert "Plan: 1 to add" in result 