#!/bin/bash

echo "Validating Speed Monitor setup..."

# Wait for services
sleep 15

# Test InfluxDB
echo "Testing InfluxDB connection..."
if curl -sf "http://localhost:8086/health" > /dev/null; then
    echo "✅ InfluxDB is healthy"
else
    echo "❌ InfluxDB connection failed"
    exit 1
fi

# Test Grafana
echo "Testing Grafana connection..."
if curl -sf "http://localhost:3000/api/health" > /dev/null; then
    echo "✅ Grafana is healthy"
else
    echo "❌ Grafana connection failed"
    exit 1
fi

# Test Grafana datasource
echo "Testing Grafana datasource..."
DATASOURCE_TEST=$(curl -s -X POST "http://localhost:3000/api/datasources/uid/influxdb-datasource/health" \
  -H "Authorization: Basic $(echo -n 'admin:speedmonitor-grafana' | base64)" \
  -H "Content-Type: application/json" | jq -r '.status')

if [ "$DATASOURCE_TEST" = "OK" ]; then
    echo "✅ Grafana datasource is working"
else
    echo "❌ Grafana datasource connection failed"
    exit 1
fi

echo ""
echo "🎉 All services are working correctly!"
echo "Access your dashboard at: http://localhost:3000"