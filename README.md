# Internet Speed Monitor

A self-hosted internet speed monitoring service for Raspberry Pi that continuously tests your internet connection and displays results in a beautiful Grafana dashboard.

## Features

- **Automated Testing**: Hourly speed tests (configurable interval)
- **Rich Dashboard**: Beautiful Grafana visualizations
- **Docker Ready**: One-command deployment
- **Historical Data**: Long-term trend analysis with InfluxDB
- **Configurable**: Customizable test intervals and servers
- **Reliable**: Built-in error handling and restart policies

## Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd speedmonitor
   ./scripts/setup.sh
   ```

2. **Access your dashboards**:
   - Grafana: http://localhost:3000 (admin/speedmonitor-grafana)
   - InfluxDB: http://localhost:8086 (admin/speedmonitor-admin)

## Requirements

- Docker and Docker Compose V2 (V1 supported but deprecated)
- 2GB+ RAM (recommended for Raspberry Pi 4)
- Internet connection for speed tests

**Note**: This project uses Docker Compose V2 (`docker compose` command). The setup scripts will automatically detect and use V1 (`docker-compose`) if V2 is not available, but upgrading to V2 is recommended.

## Configuration

The application works out-of-the-box with secure defaults. To customize, edit the `.env` file:

```bash
# Test frequency (minutes)
TEST_INTERVAL_MINUTES=60

# Specific speedtest server (optional)
SPEEDTEST_SERVER_ID=12345

# Security tokens (change for production)
INFLUXDB_TOKEN=speedmonitor-admin-token
GF_SECURITY_ADMIN_PASSWORD=speedmonitor-grafana
DOCKER_INFLUXDB_INIT_PASSWORD=speedmonitor-admin
```

## Development

### Setup Development Environment

```bash
# Install UV (if needed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup environment
uv sync

# Run tests
uv run pytest tests/ -v

# Run locally (requires InfluxDB)
uv run python -m speed_tester.monitor
```

### Project Structure

```
speedmonitor/
├── speed_tester/          # Python application
│   ├── models.py         # Data models
│   ├── speed_test_service.py  # Speed test logic
│   ├── influx_client.py  # InfluxDB integration
│   ├── config.py         # Configuration management
│   └── monitor.py        # Main application
├── tests/                # Unit tests
├── docker/               # Docker configurations
├── scripts/              # Deployment scripts
└── docker-compose.yml    # Service orchestration
```

## Monitoring

- **View logs**: `docker compose logs -f speedmonitor`
- **Service status**: `docker compose ps`
- **Restart service**: `docker compose restart speedmonitor`

## Troubleshooting

### Common Issues

1. **Speed tests failing**: Check internet connection and try different server
2. **Dashboard not loading**: Verify Grafana is running on port 3000
3. **No data in graphs**: Check speedmonitor service logs

### Useful Commands

```bash
# View application logs
docker compose logs -f speedmonitor

# Restart all services
docker compose restart

# Reset everything (WARNING: deletes data)
docker compose down -v
```

## License

MIT License - see LICENSE file for details.
