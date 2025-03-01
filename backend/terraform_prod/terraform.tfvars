# Core infrastructure
create_vpc = true
vpc_cidr   = "10.0.0.0/16"
environment = "prod"

# Web server configuration
create_webserver = true
use_autoscaling  = true
instance_type    = "t2.micro"
min_size         = 2
max_size         = 4

# Storage configuration
create_s3     = true
bucket_name   = "my-cloudpilot-static-content"

# Load balancer configuration
create_alb = true

# Elastic Beanstalk configuration
create_beanstalk = false
beanstalk_env    = "cloudpilot-nginx-prod"

# Example configurations for different scenarios:

# For development environment with minimal resources:
# environment = "dev"
# create_webserver = true
# use_autoscaling = false
# instance_type = "t2.micro"
# create_alb = false
# create_s3 = true

# For production environment with high availability:
# environment = "prod"
# create_webserver = true
# use_autoscaling = true
# instance_type = "t2.small"
# min_size = 2
# max_size = 6
# create_alb = true
# create_s3 = true

# For testing environment with Elastic Beanstalk:
# environment = "test"
# create_webserver = false
# create_beanstalk = true
# create_s3 = true
# create_alb = false 