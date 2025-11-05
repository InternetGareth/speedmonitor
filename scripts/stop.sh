#!/bin/bash

echo "Stopping Speed Monitor services..."

# Detect which Docker Compose command to use (V2 preferred, V1 fallback)
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "ERROR: Docker Compose is not installed."
    exit 1
fi

$COMPOSE_CMD down

echo "All services stopped."
echo "Data is preserved in Docker volumes."
echo "To restart: ./scripts/setup.sh"