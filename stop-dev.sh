#!/bin/bash

echo "🛑 Stopping api-research development environment..."

# Stop the api-research containers
docker compose -f docker-compose.dev.yml down

# Remove orphaned containers
docker container prune -f

echo "✅ Development environment stopped successfully!"

# Show remaining running containers
RUNNING=$(docker ps --format "table {{.Names}}\t{{.Ports}}")
if [ $(echo "$RUNNING" | wc -l) -gt 1 ]; then
    echo ""
    echo "🔍 Other running containers:"
    echo "$RUNNING"
fi