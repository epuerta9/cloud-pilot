#!/bin/bash

# Stop any running containers
docker compose down

# Build and start the development environment
docker compose -f docker-compose.dev.yml up --build 