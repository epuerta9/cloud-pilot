provider "aws" {
  region = "us-east-1"
}

# Data source for availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# VPC and Network Resources
resource "aws_vpc" "main" {
  count = var.create_vpc ? 1 : 0

  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "cloudpilot-${var.environment}-vpc"
  }
}

resource "aws_subnet" "public" {
  count = var.create_vpc ? 2 : 0

  vpc_id                  = aws_vpc.main[0].id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "cloudpilot-${var.environment}-public-${count.index + 1}"
  }
}

resource "aws_internet_gateway" "main" {
  count = var.create_vpc ? 1 : 0

  vpc_id = aws_vpc.main[0].id

  tags = {
    Name = "cloudpilot-${var.environment}-igw"
  }
}

resource "aws_route_table" "public" {
  count = var.create_vpc ? 1 : 0

  vpc_id = aws_vpc.main[0].id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main[0].id
  }

  tags = {
    Name = "cloudpilot-${var.environment}-public-rt"
  }
}

# Security Groups
resource "aws_security_group" "web" {
  count = var.create_vpc ? 1 : 0

  name        = "cloudpilot-${var.environment}-web-sg"
  description = "Security group for web servers"
  vpc_id      = aws_vpc.main[0].id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "cloudpilot-${var.environment}-web-sg"
  }
}

# Web Server Resources
module "webserver" {
  count = var.create_webserver ? 1 : 0
  
  source = "./modules/webserver"

  vpc_id            = var.create_vpc ? aws_vpc.main[0].id : ""
  subnet_ids        = var.create_vpc ? aws_subnet.public[*].id : []
  security_group_id = var.create_vpc ? aws_security_group.web[0].id : ""
  
  use_autoscaling = var.use_autoscaling
  instance_type   = var.instance_type
  min_size        = var.min_size
  max_size        = var.max_size
  environment     = var.environment
}

# S3 Bucket
resource "aws_s3_bucket" "static" {
  count = var.create_s3 ? 1 : 0

  bucket = var.bucket_name

  tags = {
    Name = "cloudpilot-${var.environment}-static"
  }
}

# Application Load Balancer
module "alb" {
  count = var.create_alb ? 1 : 0
  
  source = "./modules/alb"

  vpc_id          = var.create_vpc ? aws_vpc.main[0].id : ""
  subnet_ids      = var.create_vpc ? aws_subnet.public[*].id : []
  security_groups = var.create_vpc ? [aws_security_group.web[0].id] : []
  environment     = var.environment
}

# Elastic Beanstalk
module "beanstalk" {
  count = var.create_beanstalk ? 1 : 0
  
  source = "./modules/beanstalk"

  environment_name = var.beanstalk_env
  vpc_id          = var.create_vpc ? aws_vpc.main[0].id : ""
  subnet_ids      = var.create_vpc ? aws_subnet.public[*].id : []
  environment     = var.environment
}
