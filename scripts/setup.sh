#!/bin/bash

set -e

echo "Starting Speed Monitor Setup..."

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "ERROR: Docker Compose is not installed. Please install Docker Compose first."
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
docker-compose down || true

# Pull latest images
echo "Pulling latest images..."
docker-compose pull

# Build the speed monitor application
echo "Building Speed Monitor application..."
docker-compose build speedmonitor

# Start the services
echo "Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "Waiting for services to start..."
sleep 30

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "Services are running!"
    echo ""
    echo "Validating setup..."
    ./scripts/validate-setup.sh
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "Access your dashboards:"
        echo "   Speed Monitor Dashboard: http://localhost:3000/d/speedmonitor-dashboard/internet-speed-monitor"
        echo "   Grafana Home: http://localhost:3000"
        echo "   InfluxDB UI: http://localhost:8086"
        echo ""
        echo "Default credentials:"
        echo "   Grafana: admin / speedmonitor-grafana"
        echo "   InfluxDB: admin / speedmonitor-admin"
        echo ""
        echo "To view logs: docker-compose logs -f"
        echo "To stop: docker-compose down"
    else
        echo "Setup validation failed. Check logs with: docker-compose logs"
        exit 1
    fi
else
    echo "ERROR: Some services failed to start. Check logs with: docker-compose logs"
    exit 1
fi