provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "cloudpilot_vpc" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "cloudpilot_vpc"
  }
}

resource "aws_subnet" "cloudpilot_subnet" {
  vpc_id     = aws_vpc.cloudpilot_vpc.id
  cidr_block = "10.0.1.0/24"

  tags = {
    Name = "cloudpilot_subnet"
  }
}

resource "aws_security_group" "cloudpilot_sg" {
  name        = "cloudpilot_sg"
  description = "Allow inbound traffic"
  vpc_id      = aws_vpc.cloudpilot_vpc.id

  ingress {
    description = "HTTP from VPC"
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

resource "aws_instance" "cloudpilot_web_server" {
  ami           = "ami-05b10e08d247fb927"
  instance_type = "t2.micro"
  subnet_id     = aws_subnet.cloudpilot_subnet.id

  vpc_security_group_ids = [aws_security_group.cloudpilot_sg.id]

  tags = {
    Name = "cloudpilot_web_server"
  }
}

resource "aws_s3_bucket" "cloudpilot_static_content" {
  bucket = "cloudpilot-static-content"

  tags = {
    Name = "cloudpilot_static_content"
  }
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

resource "aws_route53_zone" "cloudpilot_zone" {
  name = "cloudpilot.example.com"
}

resource "aws_network_acl" "cloudpilot_nacl" {
  vpc_id = aws_vpc.cloudpilot_vpc.id

  egress {
    protocol   = "tcp"
    rule_no    = 200
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 443
    to_port    = 443
  }

  ingress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 80
    to_port    = 80
  }

  tags = {
    Name = "cloudpilot_nacl"
  }
}

resource "aws_cloudwatch_log_group" "cloudpilot_log_group" {
  name = "cloudpilot_log_group"

  tags = {
    Name = "cloudpilot_log_group"
  }
}

resource "aws_lb" "cloudpilot_lb" {
  name               = "cloudpilot-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.cloudpilot_sg.id]
  subnets            = [aws_subnet.cloudpilot_subnet.id]

  tags = {
    Name = "cloudpilot_lb"
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

resource "aws_lb_listener" "cloudpilot_front_end" {
  load_balancer_arn = aws_lb.cloudpilot_lb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.cloudpilot_tg.arn
  }
}