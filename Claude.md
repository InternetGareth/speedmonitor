# Internet Speed Monitor - Project Brief

## Project Overview
Build a self-hosted internet speed monitoring service for Raspberry Pi that continuously tests internet connection performance and displays results in a Grafana dashboard accessible on the local network.

## Acceptance Criteria
- ✅ Hourly automated speed tests (download, upload, ping)
- ✅ Historical data storage in time-series database
- ✅ Web dashboard accessible on local network
- ✅ Docker-based deployment for easy installation
- ✅ One-command setup for Raspberry Pi users
- ✅ All development in isolated UV environment
- ✅ Unit tests for all components
- ✅ Each step testable locally before proceeding

## Technical Design

### Architecture
```
Speed Test Service (Python)
    ↓ writes metrics
InfluxDB (Time-Series DB)
    ↓ queries data
Grafana (Dashboard)
    ↓ port 3000
Local Network Users
```

### Components
1. **Speed Test Service** (Python 3.11+)
   - Libraries: `speedtest-cli`, `influxdb-client`, `schedule`, `python-dotenv`
   - Runs hourly (configurable)
   - Writes: timestamp, download, upload, ping to InfluxDB

2. **InfluxDB** (v2.7)
   - Bucket: `speedtest`
   - Retention: 365 days (configurable)
   - Measurement: `internet_speed`

3. **Grafana** (latest)
   - Port: 3000
   - Auto-provisioned datasource and dashboard
   - Panels: current speed, trends, averages, latency

4. **Docker Compose**
   - Orchestrates all services
   - Persistent volumes for data
   - Restart policies

### Project Structure
```
speedmonitor/
├── speed_tester/          # Python application
├── tests/                 # Unit tests
├── docker/                # Dockerfiles and configs
├── scripts/               # Deployment scripts
├── pyproject.toml         # UV project config
├── docker-compose.yml
└── README.md
```

## Implementation Instructions

### Setup
All development must be done in an isolated UV environment:
```bash
# Install UV if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Initialize with required dependencies
uv init
uv add speedtest-cli influxdb-client schedule python-dotenv
uv add --dev pytest pytest-cov black ruff mypy
```

### Development Process
1. **Plan the steps**: Map out logical implementation steps to build the complete system
2. **Implement incrementally**: Complete one step at a time
3. **Test each step**: Write and run unit tests before proceeding
4. **Track progress**: Update the Progress Tracking section below after each step
5. **Wait for approval**: Present completed work and wait for user testing/approval

### Agent Usage (REQUIRED)
You MUST use specialized agents at the appropriate stages of development. Do NOT handle everything directly.

**When to Use Agents:**

1. **Explore Agent** - Use for codebase exploration tasks:
   - Understanding project structure
   - Finding where functionality is implemented
   - Searching for patterns across multiple files
   - Any open-ended exploration requiring multiple searches
   - Specify thoroughness: "quick", "medium", or "very thorough"

   Example: "Use Explore agent (medium) to understand how error handling works"

2. **test-engineer Agent** - Use IMMEDIATELY after implementing new code:
   - After writing any new class, function, or service
   - When adding new features or functionality
   - Before marking implementation steps as complete
   - For validating edge cases and error handling

   Example: "After implementing SpeedTestService, launch test-engineer to write and run comprehensive unit tests"

3. **code-reviewer Agent** - Use PROACTIVELY after completing logical chunks:
   - After implementing a complete feature or service
   - After tests pass for a component
   - Before moving to the next major implementation step
   - To get feedback on code quality and best practices

   Example: "After core implementation and passing tests, launch code-reviewer for expert feedback"

**Agent Workflow Pattern:**
```
Implement Code → test-engineer (write/run tests) → code-reviewer (quality check) → Next Step
```

**IMPORTANT:**
- Launch agents using the Task tool with the appropriate subagent_type
- Do NOT skip agents to "save time" - they improve quality significantly
- Use agents in parallel when possible (single message with multiple Task calls)
- Always specify what information the agent should return in its final report

### Testing Requirements
- Work within UV environment (`source .venv/bin/activate`)
- Unit tests required for all components
- Tests must pass before moving forward
- Mock external dependencies (speedtest API, InfluxDB)
- Integration tests after all components complete

## Progress Tracking

**Project Status**: COMPLETED

### Completed Steps
1. **UV Environment Setup** - Initialized project with all required dependencies (speedtest-cli, influxdb-client, schedule, python-dotenv)
2. **Project Structure** - Created organized directory structure with speed_tester/, tests/, docker/, scripts/
3. **Core Implementation** - Implemented all Python components:
   - SpeedTestService for running speed tests
   - InfluxDBService for data storage
   - Config management with environment variables
   - Monitor service with scheduling
4. **Comprehensive Testing** - 12 unit tests with 69% coverage, all passing
5. **Docker Configuration** - Complete containerization setup:
   - Multi-stage Dockerfile with UV
   - Docker Compose with InfluxDB, Grafana, and speedmonitor services
   - Health checks and restart policies
6. **Grafana Dashboard** - Pre-configured dashboard with:
   - Current speed displays
   - Historical trend charts
   - Ping latency monitoring
7. **Deployment Scripts** - One-command setup with ./scripts/setup.sh
8. **Documentation** - Complete README with setup, usage, and troubleshooting
9. **Configuration Improvements** (Post-MVP Enhancements):
   - Fixed dashboard URL with stable UID (`speedmonitor-dashboard`)
   - Environment variable token configuration (removed hard-coded token)
   - Updated setup.sh to display direct dashboard link
   - Added 21 comprehensive integration tests for Grafana configuration
   - All changes validated with test-engineer and code-reviewer agents
10. **Docker Compose V2 Migration** (Raspberry Pi Compatibility):
   - Migrated from deprecated `docker-compose` (V1) to `docker compose` (V2)
   - Smart detection with automatic fallback to V1 if needed
   - Updated all scripts (setup.sh, stop.sh) with version detection
   - Removed deprecated version field from docker-compose.yml
   - Updated all documentation to show V2 syntax
   - Added 32 comprehensive migration tests, all passing
   - Code review rating: 9.5/10 - Production ready
   - Resolves Raspberry Pi deployment compatibility issues

### Current Step
All planned features complete - production-ready deployment

### Configuration Details
- Dashboard URL: http://localhost:3000/d/speedmonitor-dashboard/internet-speed-monitor
- InfluxDB token: Configured via INFLUXDB_TOKEN environment variable
- Grafana datasource: Auto-provisioned with environment variable substitution
- Docker Compose: V2 primary, V1 fallback with auto-detection
- Total test coverage: 65 tests, 100% passing (33 core + 32 migration tests)

### Deployment
1. Copy .env.example to .env and configure tokens
2. Run ./scripts/setup.sh for deployment (uses `docker compose` V2 automatically)
3. Access dashboard at http://localhost:3000/d/speedmonitor-dashboard/internet-speed-monitor
4. Monitor speed tests and data collection