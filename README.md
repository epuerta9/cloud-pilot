# Cloud Pilot

Vibe and fly with your infrastructure - an AI-powered cloud infrastructure assistant.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Deployment](#deployment)
  - [Docker Deployment (Recommended)](#docker-deployment-recommended)
  - [Manual Deployment](#manual-deployment)
    - [Backend Deployment](#backend-deployment)
    - [Frontend Deployment](#frontend-deployment)
  - [Cloud Deployment](#cloud-deployment)
    - [AWS Deployment](#aws-deployment)
    - [Other Cloud Providers](#other-cloud-providers)
- [Environment Variables](#environment-variables)
- [Development Workflow](#development-workflow)

## Overview

Cloud Pilot is an AI-powered assistant that helps you design, deploy, and manage cloud infrastructure. It provides an intuitive chat interface for interacting with your cloud resources.

## Prerequisites

Before you begin, ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) (for containerized deployment)
- [Node.js](https://nodejs.org/) (v14 or later) and [npm](https://www.npmjs.com/) (for frontend development)
- [Python](https://www.python.org/) (v3.9 or later) (for backend development)
- [Terraform](https://www.terraform.io/) (v1.0 or later) (for infrastructure provisioning)

You'll also need:
- An Anthropic API key for Claude AI
- AWS credentials (access key ID and secret access key)

## Local Development

Make sure you have the following environment variables set:

```bash
export ANTHROPIC_API_KEY=<your-anthropic-api-key>
export AWS_ACCESS_KEY_ID=<your-aws-access-key-id>
export AWS_SECRET_ACCESS_KEY=<your-aws-secret-access-key>
```

Then run the following command to start the development frontend and backend:

```bash
docker compose up --build
```

## Deployment

### Docker Deployment (Recommended)

The easiest way to deploy Cloud Pilot is using Docker Compose:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cloud-pilot.git
   cd cloud-pilot
   ```

2. Set up environment variables:
   ```bash
   # Create a .env file
   cat > .env << EOL
   ANTHROPIC_API_KEY=your-anthropic-api-key
   AWS_ACCESS_KEY_ID=your-aws-access-key-id
   AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
   EOL
   ```

3. Deploy using the provided script:
   ```bash
   ./deploy.sh
   ```

This will:
- Build the frontend and backend Docker images
- Start the containers in detached mode
- Expose the frontend on port 3000 and the backend on port 8000

To check the status of your deployment:
```bash
docker compose ps
```

To view logs:
```bash
docker compose logs -f
```

To stop the deployment:
```bash
docker compose down
```

### Manual Deployment

If you prefer to deploy without Docker, follow these steps:

#### Backend Deployment

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Set environment variables:
   ```bash
   export ANTHROPIC_API_KEY=your-anthropic-api-key
   export AWS_ACCESS_KEY_ID=your-aws-access-key-id
   export AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
   ```

4. Start the backend server:
   ```bash
   uvicorn src.api:app --host 0.0.0.0 --port 8000
   ```

#### Frontend Deployment

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install --legacy-peer-deps
   ```

3. Build the production version:
   ```bash
   npm run build
   ```

4. Serve the built files (using a static file server like serve):
   ```bash
   npm install -g serve
   serve -s build -l 3000
   ```

Alternatively, you can use Nginx to serve the frontend:

```bash
# Install Nginx
sudo apt-get install nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/cloud-pilot

# Add the following configuration
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /path/to/cloud-pilot/frontend/build;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Enable the site
sudo ln -s /etc/nginx/sites-available/cloud-pilot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Cloud Deployment

#### AWS Deployment

To deploy Cloud Pilot on AWS:

1. **EC2 Deployment**:
   - Launch an EC2 instance (t2.micro or larger recommended)
   - Install Docker and Docker Compose
   - Clone the repository and follow the Docker deployment steps above

2. **ECS Deployment**:
   - Create an ECS cluster
   - Create task definitions for the frontend and backend
   - Set up the necessary environment variables in the task definitions
   - Deploy the services

3. **Using Elastic Beanstalk**:
   - Create a `Dockerrun.aws.json` file in the project root:
     ```json
     {
       "AWSEBDockerrunVersion": 2,
       "containerDefinitions": [
         {
           "name": "backend",
           "image": "your-ecr-repo/cloud-pilot-backend:latest",
           "essential": true,
           "memory": 512,
           "portMappings": [
             {
               "hostPort": 8000,
               "containerPort": 8000
             }
           ],
           "environment": [
             {
               "name": "ANTHROPIC_API_KEY",
               "value": "your-anthropic-api-key"
             },
             {
               "name": "AWS_ACCESS_KEY_ID",
               "value": "your-aws-access-key-id"
             },
             {
               "name": "AWS_SECRET_ACCESS_KEY",
               "value": "your-aws-secret-access-key"
             }
           ]
         },
         {
           "name": "frontend",
           "image": "your-ecr-repo/cloud-pilot-frontend:latest",
           "essential": true,
           "memory": 256,
           "portMappings": [
             {
               "hostPort": 80,
               "containerPort": 3000
             }
           ],
           "links": [
             "backend"
           ]
         }
       ]
     }
     ```
   - Create a new Elastic Beanstalk application and environment
   - Upload the Dockerrun.aws.json file

#### Other Cloud Providers

The deployment process for other cloud providers (GCP, Azure, etc.) is similar:

1. Set up virtual machines or container services
2. Install Docker and Docker Compose
3. Clone the repository and follow the Docker deployment steps

## Environment Variables

The following environment variables are required:

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key for Claude AI |
| `AWS_ACCESS_KEY_ID` | Your AWS access key ID |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret access key |

## Development Workflow

### Development Mode with Hot Reloading

For a better development experience with hot reloading (changes reflect immediately without rebuilding):

```bash
# Start development environment with hot reloading
./dev.sh
```

This uses a special development configuration that:
- Mounts your local frontend code directly into the container
- Uses React's development server instead of Nginx
- Enables hot reloading so changes appear instantly in the browser
- Preserves node_modules in the container (faster builds)

### Production Deployment

When you're ready to deploy to production:

```bash
# Deploy to production
./deploy.sh
```

This builds optimized production containers with:
- Minified frontend build
- Nginx for serving static files
- Better performance for end users

### Making Frontend Changes

With development mode:
1. Start the environment with `./dev.sh`
2. Edit any frontend files in the `frontend/src` directory
3. Changes will automatically appear in the browser
4. No need to rebuild or restart containers
