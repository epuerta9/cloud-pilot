"""Tests for the execute_terraform node."""

import os
import pytest
from unittest.mock import patch, MagicMock

from src.nodes.execute_terraform import execute_terraform
from src.constants import ACTION_USER_INTERACTION

@pytest.fixture
def mock_terraform_config():
    """Create a mock Terraform configuration for S3 bucket with CloudFront."""
    return '''
# Configure AWS Provider
provider "aws" {
  region = "us-west-2"
}

# Create S3 bucket
resource "aws_s3_bucket" "cdn_bucket" {
  bucket = "my-cdn-bucket-12345"
}

# Configure S3 bucket versioning
resource "aws_s3_bucket_versioning" "cdn_bucket_versioning" {
  bucket = aws_s3_bucket.cdn_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Configure S3 bucket lifecycle rule
resource "aws_s3_bucket_lifecycle_rule" "cdn_bucket_lifecycle" {
  bucket = aws_s3_bucket.cdn_bucket.id
  id      = "expire-after-30-days"
  enabled = true

  expiration {
    days = 30
  }
}

# Create Origin Access Identity for CloudFront
resource "aws_cloudfront_origin_access_identity" "oai" {
  comment = "OAI for CDN bucket"
}

# Configure bucket policy to allow CloudFront access
resource "aws_s3_bucket_policy" "cdn_bucket_policy" {
  bucket = aws_s3_bucket.cdn_bucket.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowCloudFrontAccess"
        Effect    = "Allow"
        Principal = {
          AWS = aws_cloudfront_origin_access_identity.oai.iam_arn
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.cdn_bucket.arn}/*"
      }
    ]
  })
}

# Create CloudFront distribution
resource "aws_cloudfront_distribution" "s3_distribution" {
  origin {
    domain_name = aws_s3_bucket.cdn_bucket.bucket_regional_domain_name
    origin_id   = "S3Origin"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.oai.cloudfront_access_identity_path
    }
  }

  enabled             = true
  is_ipv6_enabled    = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3Origin"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}
'''

@pytest.fixture
def mock_state(mock_terraform_config, tmp_path):
    """Create a mock state with the terraform configuration."""
    # Create a temporary directory for terraform files
    tf_dir = tmp_path / "terraform"
    tf_dir.mkdir()
    tf_file = tf_dir / "main.tf"
    tf_file.write_text(mock_terraform_config)

    return {
        "task": "Deploy S3 bucket with CloudFront CDN",
        "terraform_code": mock_terraform_config,
        "terraform_file_path": str(tf_file),
        "result": "",
        "error": "",
        "user_input": "",
        "next_action": ""
    }

@patch('subprocess.run')
def test_execute_terraform_success(mock_run, mock_state):
    """Test successful terraform execution."""
    # Mock successful terraform init
    init_result = MagicMock()
    init_result.stdout = "Terraform has been successfully initialized!"
    init_result.stderr = ""

    # Mock successful terraform apply
    apply_result = MagicMock()
    apply_result.stdout = """
Apply complete! Resources: 6 added, 0 changed, 0 destroyed.

Outputs:

cloudfront_domain_name = "d1234567890.cloudfront.net"
s3_bucket_name = "my-cdn-bucket-12345"
"""
    apply_result.stderr = ""

    # Configure mock to return different results for init and apply
    mock_run.side_effect = [init_result, apply_result]

    # Run the execute_terraform function
    result = execute_terraform(mock_state)

    # Verify terraform commands were called correctly
    assert mock_run.call_count == 2
    init_call, apply_call = mock_run.call_args_list

    # Check init call
    assert init_call[0][0] == ["terraform", "init"]
    assert init_call[1]["check"] == True

    # Check apply call
    assert apply_call[0][0] == ["terraform", "apply", "-auto-approve", "-no-color"]
    assert apply_call[1]["check"] == True

    # Verify state updates
    assert "Apply complete!" in result["result"]
    assert "cloudfront_domain_name" in result["result"]
    assert result["error"] == ""
    assert result["next_action"] == ACTION_USER_INTERACTION

@patch('subprocess.run')
def test_execute_terraform_init_failure(mock_run, mock_state):
    """Test terraform execution with init failure."""
    # Mock failed terraform init
    mock_run.side_effect = Exception("Failed to initialize backend")

    # Run the execute_terraform function
    result = execute_terraform(mock_state)

    # Verify error handling
    assert "Failed to initialize backend" in result["error"]
    assert result["next_action"] == ACTION_USER_INTERACTION

@patch('subprocess.run')
def test_execute_terraform_apply_failure(mock_run, mock_state):
    """Test terraform execution with apply failure."""
    # Mock successful init but failed apply
    init_result = MagicMock()
    init_result.stdout = "Terraform has been successfully initialized!"
    init_result.stderr = ""

    # Mock apply failure
    mock_run.side_effect = [
        init_result,  # init succeeds
        Exception("Error: Error creating CloudFront distribution: InvalidOrigin")  # apply fails
    ]

    # Run the execute_terraform function
    result = execute_terraform(mock_state)

    # Verify error handling
    assert "Error creating CloudFront distribution" in result["error"]
    assert result["next_action"] == ACTION_USER_INTERACTION

def test_execute_terraform_no_file_path():
    """Test terraform execution with no file path."""
    state = {
        "task": "Deploy S3 bucket with CloudFront CDN",
        "terraform_code": "",
        "terraform_file_path": "",
        "result": "",
        "error": "",
        "user_input": "",
        "next_action": ""
    }

    # Run the execute_terraform function
    result = execute_terraform(state)

    # Verify error handling
    assert "No Terraform file path specified" in result["error"]
    assert result["next_action"] == ACTION_USER_INTERACTION