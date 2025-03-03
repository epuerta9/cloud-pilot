#!/bin/bash

# Stop any running containers
docker compose down

# Build and start the production environment
docker compose up --build -d

echo "Production deployment complete. Services are running in the background." 