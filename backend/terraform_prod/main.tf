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

resource "aws_vpc" "cloudpilot_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "cloudpilot_vpc"
  }
}

resource "aws_internet_gateway" "cloudpilot_igw" {
  vpc_id = aws_vpc.cloudpilot_vpc.id

  tags = {
    Name = "cloudpilot_igw"
  }
}

resource "aws_subnet" "cloudpilot_public_subnet_1" {
  vpc_id            = aws_vpc.cloudpilot_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name = "cloudpilot_public_subnet_1"
  }
}

resource "aws_subnet" "cloudpilot_public_subnet_2" {
  vpc_id            = aws_vpc.cloudpilot_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1b"

  tags = {
    Name = "cloudpilot_public_subnet_2"
  }
}

resource "aws_subnet" "cloudpilot_private_subnet_1" {
  vpc_id            = aws_vpc.cloudpilot_vpc.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name = "cloudpilot_private_subnet_1"
  }
}

resource "aws_subnet" "cloudpilot_private_subnet_2" {
  vpc_id            = aws_vpc.cloudpilot_vpc.id
  cidr_block        = "10.0.4.0/24"
  availability_zone = "us-east-1b"

  tags = {
    Name = "cloudpilot_private_subnet_2"
  }
}

resource "aws_route_table" "cloudpilot_public_rt" {
  vpc_id = aws_vpc.cloudpilot_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.cloudpilot_igw.id
  }

  tags = {
    Name = "cloudpilot_public_rt"
  }
}

resource "aws_route_table_association" "cloudpilot_public_1_rt_assoc" {
  subnet_id      = aws_subnet.cloudpilot_public_subnet_1.id
  route_table_id = aws_route_table.cloudpilot_public_rt.id
}

resource "aws_route_table_association" "cloudpilot_public_2_rt_assoc" {
  subnet_id      = aws_subnet.cloudpilot_public_subnet_2.id
  route_table_id = aws_route_table.cloudpilot_public_rt.id
}

resource "aws_security_group" "cloudpilot_sg" {
  name        = "cloudpilot_sg"
  description = "Security group for CloudPilot resources"
  vpc_id      = aws_vpc.cloudpilot_vpc.id

  ingress {
    description = "HTTP from anywhere"
    from_port   = 80
    to_port     = 80
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
    Name = "cloudpilot_sg"
  }
}

resource "aws_lb" "cloudpilot_alb" {
  name               = "cloudpilot-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.cloudpilot_sg.id]
  subnets            = [aws_subnet.cloudpilot_public_subnet_1.id, aws_subnet.cloudpilot_public_subnet_2.id]

  tags = {
    Name = "cloudpilot_alb"
  }
}

resource "aws_lb_target_group" "cloudpilot_tg" {
  name     = "cloudpilot-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.cloudpilot_vpc.id

  health_check {
    path                = "/"
    healthy_threshold   = 2
    unhealthy_threshold = 10
  }
}

resource "aws_lb_listener" "cloudpilot_listener" {
  load_balancer_arn = aws_lb.cloudpilot_alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.cloudpilot_tg.arn
  }
}

resource "aws_instance" "cloudpilot_ec2" {
  ami                    = "ami-05b10e08d247fb927"
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.cloudpilot_public_subnet_1.id
  vpc_security_group_ids = [aws_security_group.cloudpilot_sg.id]

  tags = {
    Name = "cloudpilot_ec2"
  }
}

resource "aws_lb_target_group_attachment" "cloudpilot_tg_attachment" {
  target_group_arn = aws_lb_target_group.cloudpilot_tg.arn
  target_id        = aws_instance.cloudpilot_ec2.id
  port             = 80
}