variable "environment_name" {
  description = "Name of the Elastic Beanstalk environment"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where Beanstalk will be created"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for Beanstalk"
  type        = list(string)
}

variable "environment" {
  description = "Environment name"
  type        = string
} 