provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "cloudpilot_webserver" {
  ami           = "ami-05b10e08d247fb927"
  instance_type = "t3.micro"

  tags = {
    Name = "cloudpilot_webserver"
  }
}

resource "aws_s3_bucket" "cloudpilot_static_files" {
  bucket = "cloudpilot-static-files"

  tags = {
    Name = "cloudpilot_static_files"
  }
}

resource "aws_s3_bucket_public_access_block" "cloudpilot_static_files" {
  bucket = aws_s3_bucket.cloudpilot_static_files.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_ownership_controls" "cloudpilot_static_files" {
  bucket = aws_s3_bucket.cloudpilot_static_files.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "cloudpilot_static_files" {
  depends_on = [
    aws_s3_bucket_public_access_block.cloudpilot_static_files,
    aws_s3_bucket_ownership_controls.cloudpilot_static_files,
  ]

  bucket = aws_s3_bucket.cloudpilot_static_files.id
  acl    = "public-read"
}