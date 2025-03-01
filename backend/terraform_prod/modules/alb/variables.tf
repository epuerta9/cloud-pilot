variable "vpc_id" {
  description = "VPC ID where ALB will be created"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for ALB"
  type        = list(string)
}

variable "security_groups" {
  description = "List of security group IDs for ALB"
  type        = list(string)
}

variable "environment" {
  description = "Environment name"
  type        = string
} 