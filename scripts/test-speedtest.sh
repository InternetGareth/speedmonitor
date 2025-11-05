#!/bin/bash

echo "Testing Speed Monitor speedtest functionality..."
echo ""

# Check if containers are running
if ! docker compose ps speedmonitor 2>/dev/null | grep -q "Up"; then
    echo "❌ speedmonitor container is not running"
    echo "Run: docker compose up -d"
    exit 1
fi

echo "✅ Container is running"
echo ""

# Test speedtest without server constraint
echo "Running speed test (this may take 30-60 seconds)..."
echo ""

RESULT=$(docker compose exec -T speedmonitor python -c "
import speedtest
import sys
import traceback

try:
    st = speedtest.Speedtest()
    print('Finding best server...')
    best = st.get_best_server()
    print(f'Using server: {best[\"sponsor\"]} in {best[\"name\"]}, {best[\"country\"]} (ID: {best[\"id\"]})')
    print('')

    print('Testing download speed...')
    download = st.download() / 1_000_000
    print(f'Download: {download:.2f} Mbps')

    print('Testing upload speed...')
    upload = st.upload() / 1_000_000
    print(f'Upload: {upload:.2f} Mbps')

    print(f'Ping: {st.results.ping:.2f} ms')
    print('')
    print('✅ Speed test completed successfully!')
    sys.exit(0)
except Exception as e:
    print(f'❌ Speed test failed: {e}')
    traceback.print_exc()
    sys.exit(1)
" 2>&1)

echo "$RESULT"
echo ""

# Check exit code
if echo "$RESULT" | grep -q "✅ Speed test completed successfully"; then
    echo "=========================================="
    echo "✅ Speed test is working correctly!"
    echo "=========================================="
    echo ""
    echo "Your speed monitor should collect data every ${TEST_INTERVAL_MINUTES:-60} minutes."
    echo "Check logs: docker compose logs -f speedmonitor"
    exit 0
else
    echo "=========================================="
    echo "❌ Speed test failed"
    echo "=========================================="
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check internet connectivity"
    echo "  2. Check logs: docker compose logs speedmonitor"
    echo "  3. Try restarting: docker compose restart speedmonitor"
    exit 1
fi
