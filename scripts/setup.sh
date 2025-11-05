#!/bin/bash

set -e

echo "Starting Speed Monitor Setup..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed. Please install Docker first."
    exit 1
fi

# Detect which Docker Compose command to use (V2 preferred, V1 fallback)
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
    echo "WARNING: Using deprecated docker-compose V1. Please upgrade to Docker Compose V2."
else
    echo "ERROR: Docker Compose is not installed. Please install Docker Compose V2."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Created .env file with working defaults."
    echo "   Optional: Edit .env to customize tokens/passwords for security"
    echo "   Current defaults will work for local testing"
    read -p "Press Enter to continue (or Ctrl+C to edit .env first)..."
fi

# Stop any existing containers
echo "Stopping any existing containers..."
$COMPOSE_CMD down || true

# Pull latest images
echo "Pulling latest images..."
$COMPOSE_CMD pull

# Build the speed monitor application
echo "Building Speed Monitor application..."
$COMPOSE_CMD build speedmonitor

# Start the services
echo "Starting services..."
$COMPOSE_CMD up -d

# Wait for services to be healthy
echo "Waiting for services to start..."
sleep 30

# Check if services are running
if $COMPOSE_CMD ps | grep -q "Up"; then
    echo "Services are running!"
    echo ""
    echo "Validating setup..."
    ./scripts/validate-setup.sh

    if [ $? -eq 0 ]; then
        # Detect local IP address
        LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
        if [ -z "$LOCAL_IP" ]; then
            # Fallback for macOS or systems without hostname -I
            LOCAL_IP=$(ifconfig 2>/dev/null | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | head -n 1)
        fi

        echo ""
        echo "Access your dashboards:"
        if [ -n "$LOCAL_IP" ]; then
            echo "   Speed Monitor Dashboard: http://${LOCAL_IP}:3000/d/speedmonitor-dashboard/internet-speed-monitor"
            echo "   Grafana Home: http://${LOCAL_IP}:3000"
            echo "   InfluxDB UI: http://${LOCAL_IP}:8086"
            echo ""
            echo "   (Or from this machine: http://localhost:3000/d/speedmonitor-dashboard/internet-speed-monitor)"
        else
            echo "   Speed Monitor Dashboard: http://localhost:3000/d/speedmonitor-dashboard/internet-speed-monitor"
            echo "   Grafana Home: http://localhost:3000"
            echo "   InfluxDB UI: http://localhost:8086"
        fi
        echo ""
        echo "Default credentials:"
        echo "   Grafana: admin / speedmonitor-grafana"
        echo "   InfluxDB: admin / speedmonitor-admin"
        echo ""
        echo "To view logs: docker compose logs -f"
        echo "To stop: docker compose down"
    else
        echo "Setup validation failed. Check logs with: docker compose logs"
        exit 1
    fi
else
    echo "ERROR: Some services failed to start. Check logs with: docker compose logs"
    exit 1
fi