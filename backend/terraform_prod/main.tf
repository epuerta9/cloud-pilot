provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "cloudpilot_image_bucket" {
  bucket = "cloudpilot-image-bucket"
}

resource "aws_s3_bucket_public_access_block" "cloudpilot_image_bucket_public_access" {
  bucket = aws_s3_bucket.cloudpilot_image_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_cloudfront_distribution" "cloudpilot_distribution" {
  origin {
    domain_name = aws_s3_bucket.cloudpilot_image_bucket.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.cloudpilot_image_bucket.id}"
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.cloudpilot_image_bucket.id}"

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

resource "aws_iam_role" "cloudpilot_s3_role" {
  name = "cloudpilot_s3_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "cloudpilot_s3_policy" {
  name = "cloudpilot_s3_policy"
  role = aws_iam_role.cloudpilot_s3_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Effect = "Allow"
        Resource = [
          aws_s3_bucket.cloudpilot_image_bucket.arn,
          "${aws_s3_bucket.cloudpilot_image_bucket.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role" "cloudpilot_cloudfront_role" {
  name = "cloudpilot_cloudfront_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "cloudpilot_cloudfront_policy" {
  name = "cloudpilot_cloudfront_policy"
  role = aws_iam_role.cloudpilot_cloudfront_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject"
        ]
        Effect = "Allow"
        Resource = "${aws_s3_bucket.cloudpilot_image_bucket.arn}/*"
      }
    ]
  })
}