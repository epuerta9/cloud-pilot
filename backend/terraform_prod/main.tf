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

resource "aws_subnet" "cloudpilot_public_subnet" {
  vpc_id            = aws_vpc.cloudpilot_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name = "cloudpilot_public_subnet"
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

resource "aws_route_table_association" "cloudpilot_public_rta" {
  subnet_id      = aws_subnet.cloudpilot_public_subnet.id
  route_table_id = aws_route_table.cloudpilot_public_rt.id
}

resource "aws_security_group" "cloudpilot_sg" {
  name        = "cloudpilot_sg"
  description = "Allow HTTP inbound traffic"
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

resource "aws_instance" "cloudpilot_webserver" {
  ami           = "ami-05b10e08d247fb927"
  instance_type = "t2.micro"
  subnet_id     = aws_subnet.cloudpilot_public_subnet.id

  vpc_security_group_ids = [aws_security_group.cloudpilot_sg.id]

  user_data = <<-EOF
              #!/bin/bash
              echo "Hello, World!" > index.html
              nohup python -m SimpleHTTPServer 80 &
              EOF

  tags = {
    Name = "cloudpilot_webserver"
  }
}

resource "aws_eip" "cloudpilot_eip" {
  instance = aws_instance.cloudpilot_webserver.id
  vpc      = true

  tags = {
    Name = "cloudpilot_eip"
  }
}

output "webserver_public_ip" {
  value = aws_eip.cloudpilot_eip.public_ip
}