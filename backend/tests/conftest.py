"""Pytest configuration for Cloud Pilot tests."""

import os
import sys
import pytest
from unittest.mock import patch

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        "OPENAI_API_KEY": "test-api-key",
        "ENVIRONMENT": "test",
        "LOG_LEVEL": "ERROR"
    }):
        yield


@pytest.fixture
def terraform_template():
    """Return a sample Terraform template for testing."""
    return """
    provider "aws" {
      region = "us-west-2"
    }

    resource "aws_s3_bucket" "example" {
      bucket = "my-example-bucket"

      tags = {
        Name        = "My Example Bucket"
        Environment = "Dev"
      }
    }
    """ 