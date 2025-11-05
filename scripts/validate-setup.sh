#!/bin/bash

echo "Validating Speed Monitor setup..."

# Wait for services (longer for Raspberry Pi)
echo "Waiting for services to initialize..."
sleep 30

# Test InfluxDB
echo "Testing InfluxDB connection..."
if curl -sf "http://localhost:8086/health" > /dev/null; then
    echo "✅ InfluxDB is healthy"
else
    echo "❌ InfluxDB connection failed"
    exit 1
fi

# Test Grafana with retry logic (can take longer to start on Pi)
echo "Testing Grafana connection..."
GRAFANA_READY=false
for i in {1..10}; do
    if curl -sf "http://localhost:3000/api/health" > /dev/null; then
        GRAFANA_READY=true
        break
    fi
    if [ $i -lt 10 ]; then
        echo "  Grafana not ready yet, waiting... (attempt $i/10)"
        sleep 5
    fi
done

if [ "$GRAFANA_READY" = true ]; then
    echo "✅ Grafana is healthy"
else
    echo "❌ Grafana connection failed after 50 seconds"
    echo "Try: docker compose logs grafana"
    exit 1
fi

# Test Grafana datasource
echo "Testing Grafana datasource..."
DATASOURCE_RESPONSE=$(curl -s -X POST "http://localhost:3000/api/datasources/uid/influxdb-datasource/health" \
  -H "Authorization: Basic $(echo -n 'admin:speedmonitor-grafana' | base64)" \
  -H "Content-Type: application/json")

if echo "$DATASOURCE_RESPONSE" | grep -q '"status":"OK"'; then
    echo "✅ Grafana datasource is working"
else
    echo "❌ Grafana datasource connection failed"
    echo "Response: $DATASOURCE_RESPONSE"
    exit 1
fi

echo ""
echo "🎉 All services are working correctly!"
echo "Access your dashboard at: http://localhost:3000"