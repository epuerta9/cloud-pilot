# Core infrastructure variables
variable "create_vpc" {
  description = "Whether to create VPC resources"
  type        = bool
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

# Web server variables
variable "create_webserver" {
  description = "Whether to create web server resources"
  type        = bool
}

variable "use_autoscaling" {
  description = "Whether to use Auto Scaling Group instead of single EC2"
  type        = bool
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
}

variable "min_size" {
  description = "Minimum number of instances in ASG"
  type        = number
}

variable "max_size" {
  description = "Maximum number of instances in ASG"
  type        = number
}

# Storage variables
variable "create_s3" {
  description = "Whether to create S3 bucket"
  type        = bool
}

variable "bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
}

# Load balancer variables
variable "create_alb" {
  description = "Whether to create Application Load Balancer"
  type        = bool
}

# Elastic Beanstalk variables
variable "create_beanstalk" {
  description = "Whether to create Elastic Beanstalk environment"
  type        = bool
}

variable "beanstalk_env" {
  description = "Elastic Beanstalk environment name"
  type        = string
} 