output "environment_id" {
  description = "ID of the Elastic Beanstalk Environment"
  value       = aws_elastic_beanstalk_environment.env.id
}

output "environment_endpoint" {
  description = "Endpoint URL of the Elastic Beanstalk Environment"
  value       = aws_elastic_beanstalk_environment.env.endpoint_url
} 