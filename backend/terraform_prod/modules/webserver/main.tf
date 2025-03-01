# Single EC2 Instance
resource "aws_instance" "web" {
  count = var.use_autoscaling ? 0 : 1

  ami           = "ami-05b10e08d247fb927"
  instance_type = var.instance_type

  subnet_id              = var.subnet_ids[0]
  vpc_security_group_ids = [var.security_group_id]

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y nginx
              systemctl start nginx
              systemctl enable nginx
              EOF

  tags = {
    Name = "cloudpilot-${var.environment}-webserver"
  }
}

# Auto Scaling Group
resource "aws_launch_template" "web" {
  count = var.use_autoscaling ? 1 : 0

  name_prefix   = "cloudpilot-${var.environment}-template"
  image_id      = "ami-05b10e08d247fb927"
  instance_type = var.instance_type

  network_interfaces {
    associate_public_ip_address = true
    security_groups            = [var.security_group_id]
  }

  user_data = base64encode(<<-EOF
              #!/bin/bash
              yum update -y
              yum install -y nginx
              systemctl start nginx
              systemctl enable nginx
              EOF
  )

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "cloudpilot-${var.environment}-asg-instance"
    }
  }
}

resource "aws_autoscaling_group" "web" {
  count = var.use_autoscaling ? 1 : 0

  desired_capacity    = var.min_size
  max_size           = var.max_size
  min_size           = var.min_size
  target_group_arns  = var.target_group_arns
  vpc_zone_identifier = var.subnet_ids

  launch_template {
    id      = aws_launch_template.web[0].id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "cloudpilot-${var.environment}-asg"
    propagate_at_launch = true
  }
} 