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
  description = "Allow HTTP traffic"
  vpc_id      = aws_vpc.cloudpilot_vpc.id

  ingress {
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
  subnet_id     = aws_subnet.cloudpilot_subnet.id

  vpc_security_group_ids = [aws_security_group.cloudpilot_sg.id]

  tags = {
    Name = "cloudpilot_webserver"
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

resource "aws_iam_role_policy_attachment" "cloudpilot_s3_access" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
  role       = aws_iam_role.cloudpilot_ec2_role.name
}

resource "aws_elb" "cloudpilot_elb" {
  name               = "cloudpilot-elb"
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]

  listener {
    instance_port     = 80
    instance_protocol = "http"
    lb_port           = 80
    lb_protocol       = "http"
  }

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    target              = "HTTP:80/"
    interval            = 30
  }

  instances                   = [aws_instance.cloudpilot_webserver.id]
  cross_zone_load_balancing   = true
  idle_timeout                = 400
  connection_draining         = true
  connection_draining_timeout = 400

  tags = {
    Name = "cloudpilot_elb"
  }
}

resource "aws_route53_zone" "cloudpilot_zone" {
  name = "cloudpilot.example.com"
}

resource "aws_route53_record" "cloudpilot_record" {
  zone_id = aws_route53_zone.cloudpilot_zone.zone_id
  name    = "www.cloudpilot.example.com"
  type    = "A"

  alias {
    name                   = aws_elb.cloudpilot_elb.dns_name
    zone_id                = aws_elb.cloudpilot_elb.zone_id
    evaluate_target_health = true
  }
}

resource "aws_cloudwatch_metric_alarm" "cloudpilot_cpu_alarm" {
  alarm_name          = "cloudpilot-cpu-alarm"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ec2 cpu utilization"
  alarm_actions       = []

  dimensions = {
    InstanceId = aws_instance.cloudpilot_webserver.id
  }
}