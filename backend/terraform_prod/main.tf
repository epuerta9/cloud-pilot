provider "aws" {
region = "us-west-2"
}

resource "aws_s3_bucket" "cloudpilot_website_bucket" {
bucket = "cloudpilot-website-bucket"

server_side_encryption_configuration {
rule {
apply_server_side_encryption_by_default {
sse_algorithm = "AES256"
}
}
}

tags = {
Name = "CloudPilot Website Bucket"
}
}

resource "aws_s3_bucket_public_access_block" "cloudpilot_website_bucket_public_access_block" {
bucket = aws_s3_bucket.cloudpilot_website_bucket.id

block_public_acls       = true
block_public_policy     = true
ignore_public_acls      = true
restrict_public_buckets = true
}

resource "aws_iam_role" "cloudpilot_ec2_role" {
name = "cloudpilot_ec2_role"

assume_role_policy = jsonencode({
Version = "2012-10-17"
Statement = [
{
Action = "sts:AssumeRole"
Effect = "Allow"
Principal = {
Service = "ec2.amazonaws.com"
}
}
]
})
}

resource "aws_iam_role_policy_attachment" "cloudpilot_s3_access" {
policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
role       = aws_iam_role.cloudpilot_ec2_role.name
}

resource "aws_security_group" "cloudpilot_web_sg" {
name        = "cloudpilot_web_sg"
description = "Security group for web server"

ingress {
from_port   = 80
to_port     = 80
protocol    = "tcp"
cidr_blocks = ["0.