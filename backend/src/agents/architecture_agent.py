"""Architecture Agent for Cloud Pilot.

This agent provides architecture recommendations and cost estimates.
"""

import os
from typing import Dict, List, Optional, Any
from llama_index.llms.anthropic import Anthropic
from src.constants import ANTHROPIC_MODEL

# Architecture mode prompt templates
ARCHITECT_MODE_SYSTEM_PROMPT = """You are Cloud Pilot's Architecture Expert. Your role is to provide detailed architecture recommendations based on user requirements.

When responding to users:
1. Analyze their requirements carefully
2. Recommend the optimal cloud architecture design
3. Explain the pros and cons of different architectural patterns
4. Provide diagrams using ASCII art or markdown
5. Explain why your recommended architecture is suitable for their use case
6. Suggest best practices for implementation
7. Highlight potential scalability, security, and reliability considerations
8. Provide detailed cost estimates for different user scales (e.g., 1k, 10k, 100k users)

Always be thorough in your explanations and provide reasoning for your recommendations.
"""

DEPLOY_MODE_SYSTEM_PROMPT = """You are Cloud Pilot's Deployment and Cost Expert. Your role is to provide detailed deployment options and cost estimates based on user requirements.

When responding to users:
1. Analyze their requirements carefully
2. Recommend deployment options across different cloud providers (AWS, Azure, GCP)
3. Provide detailed cost breakdowns for each option
4. Compare pricing tiers and service levels
5. Highlight cost optimization strategies
6. Explain trade-offs between cost, performance, and reliability
7. Provide monthly and yearly cost projections
8. Suggest ways to reduce costs without compromising quality
9. Include specific deployment steps and example code/configurations

Always be thorough in your cost analysis and provide reasoning for your recommendations.
"""

class ArchitectureAgent:
    """Agent that provides architecture recommendations and cost estimates."""

    def __init__(self, model_name: str = ANTHROPIC_MODEL):
        """Initialize the architecture agent with Anthropic.
        
        Args:
            model_name: The name of the Anthropic model to use
        """
        self.llm = Anthropic(model=model_name)

    def process_message(self, message: str, mode: str = "architect") -> Dict[str, Any]:
        """Process a message in the specified mode using Anthropic.
        
        Args:
            message: The user message to process
            mode: The mode to use (architect or deploy)
            
        Returns:
            A dictionary with the response
        """
        try:
            # Select the appropriate system prompt based on mode
            system_prompt = ARCHITECT_MODE_SYSTEM_PROMPT if mode == "architect" else DEPLOY_MODE_SYSTEM_PROMPT
            
            # Create a prompt that includes context about what the user is asking for
            prompt = f"""
            User request: {message}
            
            Please provide a detailed response with architecture recommendations or deployment instructions based on the user's request.
            Include specific AWS services, cost estimates, and diagrams where appropriate.
            """
            
            # Call Anthropic with the system prompt and user message
            response = self.llm.complete(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=4000,
                temperature=0.7
            )
            
            return {
                "message": response.text,
                "error": None
            }
        except Exception as e:
            # Fall back to static responses if there's an error
            return self._get_fallback_response(message, mode, str(e))
    
    def _get_fallback_response(self, message: str, mode: str, error: str) -> Dict[str, Any]:
        """Provide fallback responses if the LLM call fails.
        
        Args:
            message: The user message
            mode: The current mode
            error: The error message
            
        Returns:
            A dictionary with the fallback response
        """
        print(f"Error calling Anthropic: {error}")
        
        # Check for specific types of requests in the message
        is_social_media = "social media" in message.lower() or "instagram" in message.lower() or "facebook" in message.lower()
        is_ecommerce = "ecommerce" in message.lower() or "online store" in message.lower() or "shop" in message.lower()
        is_streaming = "streaming" in message.lower() or "video" in message.lower() or "youtube" in message.lower()
        is_mobile = "mobile" in message.lower() or "app" in message.lower()
        
        # EC2 related queries
        is_ec2 = "ec2" in message.lower() or "web server" in message.lower()
        is_serverless = "serverless" in message.lower() or "lambda" in message.lower() or "api gateway" in message.lower()
        is_container = "container" in message.lower() or "docker" in message.lower() or "ecs" in message.lower() or "eks" in message.lower()
        is_static = "static" in message.lower() or "s3" in message.lower() or "cloudfront" in message.lower()
        
        if mode == "architect":
            if is_social_media:
                return {
                    "message": f"# Architecture Recommendation for Social Media Platform\n\n" +
                               "## Recommended Architecture\n\n" +
                               "For a social media platform similar to Instagram, I recommend a microservices architecture with the following components:\n\n" +
                               "1. **Frontend**: React.js SPA hosted on AWS S3 + CloudFront\n" +
                               "2. **API Layer**: Node.js/Express or FastAPI on AWS ECS Fargate\n" +
                               "3. **Authentication**: AWS Cognito for user management\n" +
                               "4. **Media Storage**: S3 for images/videos with CloudFront CDN\n" +
                               "5. **Database**: \n" +
                               "   - User profiles: Amazon RDS (PostgreSQL)\n" +
                               "   - Posts/comments: Amazon DynamoDB\n" +
                               "   - Real-time features: Amazon ElastiCache (Redis)\n" +
                               "6. **Search**: Amazon Elasticsearch Service\n" +
                               "7. **Notifications**: Amazon SNS + SQS\n\n" +
                               "## Estimated Costs (per 10,000 MAU)\n\n" +
                               "- **Compute**: $300-500/month\n" +
                               "- **Storage**: $100-200/month\n" +
                               "- **Database**: $150-300/month\n" +
                               "- **CDN/Transfer**: $100-250/month\n" +
                               "- **Other Services**: $50-150/month\n\n" +
                               "**Total Estimated Cost**: $700-1,400/month for 10,000 monthly active users\n\n" +
                               "Costs will scale approximately linearly with user growth, though you'll see some economies of scale.",
                    "error": None
                }
            elif is_ecommerce:
                return {
                    "message": f"# Architecture Recommendation for E-commerce Platform\n\n" +
                               "## Recommended Architecture\n\n" +
                               "For an e-commerce website handling 50,000 monthly visitors, I recommend:\n\n" +
                               "1. **Frontend**: Next.js with SSR hosted on AWS ECS or Vercel\n" +
                               "2. **API Layer**: Node.js/Express on AWS ECS with Auto Scaling\n" +
                               "3. **Authentication**: AWS Cognito with social login options\n" +
                               "4. **Product Catalog**: Amazon RDS (PostgreSQL) with read replicas\n" +
                               "5. **Product Search**: Amazon Elasticsearch Service\n" +
                               "6. **Shopping Cart**: Amazon DynamoDB + ElastiCache (Redis)\n" +
                               "7. **Payment Processing**: Stripe API integration via AWS Lambda\n" +
                               "8. **Order Management**: Microservice on ECS with SQS queue\n" +
                               "9. **Product Images**: S3 with CloudFront CDN\n" +
                               "10. **Analytics**: AWS Kinesis + Redshift\n\n" +
                               "## Estimated Costs (50,000 monthly visitors)\n\n" +
                               "- **Compute**: $400-600/month\n" +
                               "- **Database**: $200-400/month\n" +
                               "- **Storage & CDN**: $150-300/month\n" +
                               "- **Search & Cache**: $100-200/month\n" +
                               "- **Other Services**: $100-200/month\n\n" +
                               "**Total Estimated Cost**: $950-1,700/month\n\n" +
                               "This architecture provides good performance, reliability, and can scale to handle seasonal traffic spikes.",
                    "error": None
                }
            elif is_streaming:
                return {
                    "message": f"# Architecture Recommendation for Video Streaming Service\n\n" +
                               "## Recommended Architecture\n\n" +
                               "For a video streaming service like YouTube, I recommend:\n\n" +
                               "1. **Frontend**: React.js SPA hosted on S3 + CloudFront\n" +
                               "2. **API Layer**: Node.js or Go microservices on ECS/EKS\n" +
                               "3. **Authentication**: AWS Cognito + Custom JWT service\n" +
                               "4. **Video Processing Pipeline**:\n" +
                               "   - Upload: S3 + Lambda triggers\n" +
                               "   - Transcoding: AWS MediaConvert or Elastic Transcoder\n" +
                               "   - Thumbnail generation: Lambda functions\n" +
                               "5. **Video Storage**: S3 with lifecycle policies\n" +
                               "6. **Video Delivery**: CloudFront with signed URLs\n" +
                               "7. **Metadata**: PostgreSQL RDS for video metadata\n" +
                               "8. **Search**: Amazon Elasticsearch Service\n" +
                               "9. **Analytics**: Kinesis + Redshift\n\n" +
                               "## Estimated Costs (per 1,000 users)\n\n" +
                               "- **Video Storage**: $200-400/month (assuming 5GB/user)\n" +
                               "- **Video Delivery**: $300-600/month (assuming 20GB/user viewing)\n" +
                               "- **Transcoding**: $100-300/month\n" +
                               "- **Compute & Databases**: $200-400/month\n" +
                               "- **Other Services**: $100-200/month\n\n" +
                               "**Total Estimated Cost**: $900-1,900/month per 1,000 active users\n\n" +
                               "Video streaming is bandwidth-intensive, so costs scale primarily with content volume and viewing time.",
                    "error": None
                }
            elif is_mobile:
                return {
                    "message": f"# Architecture Recommendation for Mobile App Backend\n\n" +
                               "## Recommended Architecture\n\n" +
                               "For a mobile app with user profiles, real-time chat, and data synchronization:\n\n" +
                               "1. **API Layer**: AWS AppSync (GraphQL) + API Gateway (REST)\n" +
                               "2. **Authentication**: Amazon Cognito with social login options\n" +
                               "3. **User Profiles**: Amazon DynamoDB\n" +
                               "4. **Real-time Chat**: AWS AppSync with WebSockets + DynamoDB\n" +
                               "5. **Push Notifications**: Amazon SNS with Firebase/APNS integration\n" +
                               "6. **File Storage**: Amazon S3 for user-generated content\n" +
                               "7. **Caching**: Amazon ElastiCache (Redis)\n" +
                               "8. **Offline Sync**: AWS AppSync with conflict resolution\n" +
                               "9. **Analytics**: Amazon Pinpoint + Kinesis\n\n" +
                               "## Estimated Costs (10,000 MAU)\n\n" +
                               "- **API & Real-time**: $200-400/month\n" +
                               "- **Database**: $100-300/month\n" +
                               "- **Authentication**: $50-150/month\n" +
                               "- **Storage**: $50-150/month\n" +
                               "- **Push & Analytics**: $50-150/month\n\n" +
                               "**Total Estimated Cost**: $450-1,150/month for 10,000 monthly active users\n\n" +
                               "This architecture provides excellent mobile experience with offline capabilities and real-time features.",
                    "error": None
                }
            else:
                return {
                    "message": f"# Architecture Recommendation\n\n" +
                               "Based on your request: \"{message}\"\n\n" +
                               "I'd need more specific information about your application requirements to provide a detailed architecture recommendation. Consider specifying:\n\n" +
                               "1. Type of application (web, mobile, IoT, etc.)\n" +
                               "2. Expected user base and growth\n" +
                               "3. Key features and functionality\n" +
                               "4. Performance requirements\n" +
                               "5. Budget constraints\n\n" +
                               "For example, you could ask about architecture for a social media platform, e-commerce site, video streaming service, or mobile app backend.",
                    "error": None
                }
        elif mode == "deploy":
            if is_ec2:
                return {
                    "message": f"# EC2 Web Server Deployment Guide\n\n" +
                               "## Recommended Setup for Node.js Web Application\n\n" +
                               "1. **EC2 Instance**: t3.medium (2 vCPU, 4GB RAM)\n" +
                               "2. **Operating System**: Amazon Linux 2\n" +
                               "3. **Setup Steps**:\n" +
                               "   - Install Node.js and npm\n" +
                               "   - Set up Nginx as reverse proxy\n" +
                               "   - Configure PM2 for process management\n" +
                               "   - Set up auto-scaling group with launch template\n" +
                               "   - Configure Application Load Balancer\n" +
                               "   - Set up Route 53 for domain management\n\n" +
                               "## Terraform Configuration\n\n" +
                               "```hcl\n" +
                               "resource \"aws_instance\" \"web_server\" {\n" +
                               "  ami           = \"ami-0c55b159cbfafe1f0\"\n" +
                               "  instance_type = \"t3.medium\"\n" +
                               "  key_name      = aws_key_pair.deployer.key_name\n" +
                               "  vpc_security_group_ids = [aws_security_group.web.id]\n" +
                               "  user_data = <<-EOF\n" +
                               "    #!/bin/bash\n" +
                               "    yum update -y\n" +
                               "    curl -sL https://rpm.nodesource.com/setup_14.x | bash -\n" +
                               "    yum install -y nodejs\n" +
                               "    # Additional setup steps...\n" +
                               "  EOF\n" +
                               "  tags = {\n" +
                               "    Name = \"WebServer\"\n" +
                               "  }\n" +
                               "}\n" +
                               "```\n\n" +
                               "## Estimated Monthly Cost\n\n" +
                               "- **EC2 Instance**: $30-40/month (on-demand) or $18-25/month (reserved)\n" +
                               "- **EBS Storage**: $5-10/month (30GB gp3)\n" +
                               "- **Load Balancer**: $16-20/month\n" +
                               "- **Data Transfer**: $5-20/month (varies with traffic)\n\n" +
                               "**Total Estimated Cost**: $56-90/month (on-demand) or $44-75/month (reserved)",
                    "error": None
                }
            elif is_serverless:
                return {
                    "message": f"# Serverless API Deployment Guide\n\n" +
                               "## Recommended Setup for REST API\n\n" +
                               "1. **API Gateway**: REST API with regional endpoint\n" +
                               "2. **Lambda Functions**: Node.js 18.x runtime\n" +
                               "3. **Database**: DynamoDB for persistence\n" +
                               "4. **Authentication**: Cognito User Pools or Lambda Authorizer\n" +
                               "5. **Monitoring**: CloudWatch Logs and X-Ray\n\n" +
                               "## Deployment Steps\n\n" +
                               "1. Create Lambda functions for each endpoint\n" +
                               "2. Set up API Gateway with appropriate routes\n" +
                               "3. Configure integration between API Gateway and Lambda\n" +
                               "4. Set up DynamoDB tables with appropriate indexes\n" +
                               "5. Configure authentication and authorization\n" +
                               "6. Deploy to a stage (dev, test, prod)\n" +
                               "7. Set up custom domain with Route 53\n\n" +
                               "## Terraform Configuration\n\n" +
                               "```hcl\n" +
                               "resource \"aws_api_gateway_rest_api\" \"api\" {\n" +
                               "  name = \"serverless-api\"\n" +
                               "}\n\n" +
                               "resource \"aws_lambda_function\" \"api_function\" {\n" +
                               "  function_name = \"api-handler\"\n" +
                               "  handler       = \"index.handler\"\n" +
                               "  runtime       = \"nodejs18.x\"\n" +
                               "  filename      = \"lambda.zip\"\n" +
                               "  role          = aws_iam_role.lambda_role.arn\n" +
                               "}\n\n" +
                               "resource \"aws_dynamodb_table\" \"data_table\" {\n" +
                               "  name         = \"api-data\"\n" +
                               "  billing_mode = \"PAY_PER_REQUEST\"\n" +
                               "  hash_key     = \"id\"\n" +
                               "  attribute {\n" +
                               "    name = \"id\"\n" +
                               "    type = \"S\"\n" +
                               "  }\n" +
                               "}\n" +
                               "```\n\n" +
                               "## Estimated Monthly Cost\n\n" +
                               "- **API Gateway**: $3.50/million requests\n" +
                               "- **Lambda**: $0.20/million invocations + $0.0000166667/GB-second\n" +
                               "- **DynamoDB**: ~$1-5/month for low traffic (pay-per-request)\n" +
                               "- **CloudWatch**: $0-5/month\n\n" +
                               "**Total Estimated Cost**: $5-20/month for moderate usage (1M requests/month)",
                    "error": None
                }
            elif is_container:
                return {
                    "message": f"# Container Deployment Guide\n\n" +
                               "## ECS vs. EKS Comparison\n\n" +
                               "### Amazon ECS (Elastic Container Service)\n" +
                               "- **Best for**: Simpler deployments, AWS-integrated applications\n" +
                               "- **Complexity**: Lower learning curve\n" +
                               "- **Management**: AWS managed control plane\n" +
                               "- **Cost**: Lower operational cost\n" +
                               "- **Flexibility**: Less flexible but easier to use\n\n" +
                               "### Amazon EKS (Elastic Kubernetes Service)\n" +
                               "- **Best for**: Complex applications, multi-cloud strategy\n" +
                               "- **Complexity**: Steeper learning curve\n" +
                               "- **Management**: Kubernetes control plane (AWS managed)\n" +
                               "- **Cost**: Higher operational cost\n" +
                               "- **Flexibility**: More flexible but more complex\n\n" +
                               "## Recommended Setup (ECS Fargate)\n\n" +
                               "1. **Create ECS Cluster** with Fargate launch type\n" +
                               "2. **Define Task Definition** with container specifications\n" +
                               "3. **Create ECS Service** with desired count and auto-scaling\n" +
                               "4. **Set up Application Load Balancer** for traffic distribution\n" +
                               "5. **Configure Service Discovery** if needed\n\n" +
                               "## Terraform Configuration\n\n" +
                               "```hcl\n" +
                               "resource \"aws_ecs_cluster\" \"main\" {\n" +
                               "  name = \"app-cluster\"\n" +
                               "}\n\n" +
                               "resource \"aws_ecs_task_definition\" \"app\" {\n" +
                               "  family                   = \"app\"\n" +
                               "  network_mode             = \"awsvpc\"\n" +
                               "  requires_compatibilities = [\"FARGATE\"]\n" +
                               "  cpu                      = 256\n" +
                               "  memory                   = 512\n" +
                               "  execution_role_arn       = aws_iam_role.ecs_execution_role.arn\n" +
                               "  container_definitions    = jsonencode([\n" +
                               "    {\n" +
                               "      name      = \"app\"\n" +
                               "      image     = \"${aws_ecr_repository.app.repository_url}:latest\"\n" +
                               "      essential = true\n" +
                               "      portMappings = [{\n" +
                               "        containerPort = 80\n" +
                               "        hostPort      = 80\n" +
                               "      }]\n" +
                               "    }\n" +
                               "  ])\n" +
                               "}\n" +
                               "```\n\n" +
                               "## Estimated Monthly Cost (ECS Fargate)\n\n" +
                               "- **Fargate**: $30-40/month per service (0.25 vCPU, 0.5GB RAM)\n" +
                               "- **Load Balancer**: $16-20/month\n" +
                               "- **ECR Storage**: $1-5/month\n" +
                               "- **Data Transfer**: $5-20/month\n\n" +
                               "**Total Estimated Cost**: $52-85/month for a single service",
                    "error": None
                }
            elif is_static:
                return {
                    "message": f"# Static Website Deployment Guide\n\n" +
                               "## Recommended Setup for React Static Website\n\n" +
                               "1. **S3 Bucket**: Configure for static website hosting\n" +
                               "2. **CloudFront Distribution**: CDN for global delivery\n" +
                               "3. **Route 53**: DNS management for custom domain\n" +
                               "4. **ACM**: SSL certificate for HTTPS\n\n" +
                               "## Deployment Steps\n\n" +
                               "1. Create S3 bucket with appropriate permissions\n" +
                               "2. Build React application (`npm run build`)\n" +
                               "3. Upload build artifacts to S3\n" +
                               "4. Create CloudFront distribution pointing to S3\n" +
                               "5. Configure custom domain and SSL certificate\n" +
                               "6. Set up CI/CD pipeline for automated deployments\n\n" +
                               "## Terraform Configuration\n\n" +
                               "```hcl\n" +
                               "resource \"aws_s3_bucket\" \"website\" {\n" +
                               "  bucket = \"my-static-website\"\n" +
                               "}\n\n" +
                               "resource \"aws_s3_bucket_website_configuration\" \"website\" {\n" +
                               "  bucket = aws_s3_bucket.website.id\n" +
                               "  index_document {\n" +
                               "    suffix = \"index.html\"\n" +
                               "  }\n" +
                               "  error_document {\n" +
                               "    key = \"index.html\"\n" +
                               "  }\n" +
                               "}\n\n" +
                               "resource \"aws_cloudfront_distribution\" \"website\" {\n" +
                               "  origin {\n" +
                               "    domain_name = aws_s3_bucket.website.bucket_regional_domain_name\n" +
                               "    origin_id   = \"S3-${aws_s3_bucket.website.id}\"\n" +
                               "  }\n" +
                               "  enabled             = true\n" +
                               "  default_root_object = \"index.html\"\n" +
                               "  # Additional configuration...\n" +
                               "}\n" +
                               "```\n\n" +
                               "## Estimated Monthly Cost\n\n" +
                               "- **S3 Storage**: $0.023/GB/month (~$0.50 for typical site)\n" +
                               "- **CloudFront**: $0.085/GB data transfer (~$0.85 for 10GB/month)\n" +
                               "- **Route 53**: $0.50/month per hosted zone\n" +
                               "- **ACM Certificate**: Free (for CloudFront distributions)\n\n" +
                               "**Total Estimated Cost**: $1-5/month for low to moderate traffic",
                    "error": None
                }
            else:
                return {
                    "message": f"# Deployment Options\n\n" +
                               "Based on your request: \"{message}\"\n\n" +
                               "I can help you deploy various types of applications to AWS. Here are some common deployment options:\n\n" +
                               "1. **EC2 Web Server**: Traditional VM-based deployment for web applications\n" +
                               "2. **Serverless API**: Event-driven architecture using Lambda and API Gateway\n" +
                               "3. **Container Deployment**: Docker containers using ECS or EKS\n" +
                               "4. **Static Website**: S3 and CloudFront for static web content\n\n" +
                               "Please specify which type of deployment you're interested in, and I can provide detailed setup instructions and cost estimates.",
                    "error": None
                }
        else:
            return {
                "message": f"Normal mode response for: {message}\n\n" +
                           "I can help you with cloud infrastructure questions. Try switching to:\n\n" +
                           "- **Architect Mode**: For architecture recommendations and design patterns\n" +
                           "- **Deploy Mode**: For deployment instructions and cost estimates",
                "error": None
            } 