terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "cloudpilot_bucket" {
  bucket = "cloudpilot-example-bucket"
}

resource "aws_s3_bucket_public_access_block" "cloudpilot_bucket_public_access_block" {
  bucket = aws_s3_bucket.cloudpilot_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "cloudpilot_bucket_versioning" {
  bucket = aws_s3_bucket.cloudpilot_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "cloudpilot_bucket_encryption" {
  bucket = aws_s3_bucket.cloudpilot_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}