#!/bin/bash

echo "🚀 Starting api-research development environment..."

# Stop any containers using conflicting ports
echo "🔍 Checking for port conflicts..."

# Check for containers using port 5173
FRONTEND_CONFLICTS=$(docker ps --filter "publish=5173" --format "{{.Names}}" | grep -v "api-research-frontend")
if [ ! -z "$FRONTEND_CONFLICTS" ]; then
    echo "⚠️  Stopping containers using port 5173: $FRONTEND_CONFLICTS"
    echo "$FRONTEND_CONFLICTS" | xargs docker stop
fi

# Check for containers using port 8000
BACKEND_CONFLICTS=$(docker ps --filter "publish=8000" --format "{{.Names}}" | grep -v "api-research-web")
if [ ! -z "$BACKEND_CONFLICTS" ]; then
    echo "⚠️  Stopping containers using port 8000: $BACKEND_CONFLICTS"
    echo "$BACKEND_CONFLICTS" | xargs docker stop
fi

# Stop any other running compose projects that might conflict
echo "🛑 Stopping other running compose projects..."
docker compose ls -q | while read project; do
    if [ "$project" != "api-research" ]; then
        echo "  Stopping project: $project"
        docker compose -p "$project" down 2>/dev/null || true
    fi
done

# Start api-research containers
echo "🏗️  Starting api-research containers..."
if ! docker compose -f docker-compose.dev.yml up -d; then
    echo "⚠️  Failed to start containers, trying without build..."
    docker compose -f docker-compose.dev.yml up -d --no-build
fi

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5

# Health check
echo "🔍 Checking service health..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
fi

if curl -s http://localhost:5173 > /dev/null; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend health check failed"
fi

# Display URLs
echo ""
./get-windows-urls.sh

echo ""
echo "🎉 Development environment started successfully!"
echo "📝 Use 'docker compose -f docker-compose.dev.yml logs -f' to view logs"
echo "🛑 Use 'docker compose -f docker-compose.dev.yml down' to stop"