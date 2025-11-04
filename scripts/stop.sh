#!/bin/bash

echo "Stopping Speed Monitor services..."

docker-compose down

echo "All services stopped."
echo "Data is preserved in Docker volumes."
echo "To restart: ./scripts/setup.sh"