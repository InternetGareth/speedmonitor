"""
Integration tests for Grafana and InfluxDB configuration files.

Tests validate:
1. Dashboard JSON structure and UID presence
2. Datasource YAML uses environment variable tokens
3. Configuration file integrity and format
"""

import json
import re
import pytest
from pathlib import Path


# Define paths relative to project root
PROJECT_ROOT = Path(__file__).parent.parent
DASHBOARD_PATH = PROJECT_ROOT / "docker/grafana/dashboards/speed-monitor.json"
DATASOURCE_PATH = PROJECT_ROOT / "docker/grafana/provisioning/datasources/influxdb.yml"


class TestDashboardConfiguration:
    """Test suite for Grafana dashboard JSON configuration."""

    def test_dashboard_file_exists(self):
        """Verify dashboard JSON file exists at expected location."""
        assert DASHBOARD_PATH.exists(), f"Dashboard file not found at {DASHBOARD_PATH}"

    def test_dashboard_is_valid_json(self):
        """Verify dashboard file is valid JSON."""
        with open(DASHBOARD_PATH, 'r') as f:
            try:
                dashboard = json.load(f)
            except json.JSONDecodeError as e:
                pytest.fail(f"Dashboard JSON is invalid: {e}")

        assert isinstance(dashboard, dict), "Dashboard should be a JSON object"

    def test_dashboard_has_uid_field(self):
        """Verify dashboard has a UID field defined."""
        with open(DASHBOARD_PATH, 'r') as f:
            dashboard = json.load(f)

        assert "uid" in dashboard, "Dashboard must have a 'uid' field"
        assert dashboard["uid"] is not None, "Dashboard UID cannot be null"
        assert dashboard["uid"] != "", "Dashboard UID cannot be empty"

    def test_dashboard_uid_value(self):
        """Verify dashboard UID matches expected value."""
        with open(DASHBOARD_PATH, 'r') as f:
            dashboard = json.load(f)

        expected_uid = "speedmonitor-dashboard"
        actual_uid = dashboard["uid"]

        assert actual_uid == expected_uid, (
            f"Dashboard UID should be '{expected_uid}', got '{actual_uid}'"
        )

    def test_dashboard_uid_format(self):
        """Verify dashboard UID follows Grafana naming conventions."""
        with open(DASHBOARD_PATH, 'r') as f:
            dashboard = json.load(f)

        uid = dashboard["uid"]

        # Grafana UIDs should be alphanumeric with hyphens/underscores
        # Typically 8-40 characters, no special chars except - and _
        uid_pattern = re.compile(r'^[a-zA-Z0-9_-]+$')

        assert uid_pattern.match(uid), (
            f"Dashboard UID '{uid}' contains invalid characters. "
            "Must be alphanumeric with hyphens or underscores only."
        )

        assert 3 <= len(uid) <= 40, (
            f"Dashboard UID '{uid}' length ({len(uid)}) should be between 3 and 40 characters"
        )

    def test_dashboard_has_required_fields(self):
        """Verify dashboard has all required top-level fields."""
        with open(DASHBOARD_PATH, 'r') as f:
            dashboard = json.load(f)

        required_fields = ["uid", "title", "panels", "schemaVersion"]

        for field in required_fields:
            assert field in dashboard, f"Dashboard must have '{field}' field"

    def test_dashboard_panels_reference_correct_datasource(self):
        """Verify all panels reference the correct datasource UID."""
        with open(DASHBOARD_PATH, 'r') as f:
            dashboard = json.load(f)

        expected_datasource_uid = "influxdb-datasource"
        panels = dashboard.get("panels", [])

        assert len(panels) > 0, "Dashboard should have at least one panel"

        for panel in panels:
            panel_id = panel.get("id", "unknown")
            targets = panel.get("targets", [])

            for target in targets:
                datasource = target.get("datasource", {})
                datasource_uid = datasource.get("uid")

                assert datasource_uid == expected_datasource_uid, (
                    f"Panel {panel_id} references datasource '{datasource_uid}', "
                    f"expected '{expected_datasource_uid}'"
                )

    def test_dashboard_url_predictability(self):
        """Verify dashboard UID enables predictable URL access."""
        with open(DASHBOARD_PATH, 'r') as f:
            dashboard = json.load(f)

        uid = dashboard["uid"]

        # Expected URL format: http://localhost:3000/d/{uid}/{slug}
        expected_url_pattern = f"/d/{uid}/"

        # This test documents the expected URL structure
        assert uid == "speedmonitor-dashboard", (
            f"Dashboard should be accessible at {expected_url_pattern}"
        )


class TestDatasourceConfiguration:
    """Test suite for InfluxDB datasource YAML configuration."""

    def test_datasource_file_exists(self):
        """Verify datasource YAML file exists at expected location."""
        assert DATASOURCE_PATH.exists(), f"Datasource file not found at {DATASOURCE_PATH}"

    def test_datasource_is_valid_yaml(self):
        """Verify datasource file is valid YAML format."""
        with open(DATASOURCE_PATH, 'r') as f:
            content = f.read()

        # Basic YAML structure validation
        assert "apiVersion:" in content, "YAML should have apiVersion field"
        assert "datasources:" in content, "YAML should have datasources field"

    def test_datasource_uses_environment_variable(self):
        """Verify datasource token uses environment variable syntax."""
        with open(DATASOURCE_PATH, 'r') as f:
            content = f.read()

        # Check for environment variable syntax ${INFLUXDB_TOKEN}
        assert "${INFLUXDB_TOKEN}" in content, (
            "Datasource should use ${INFLUXDB_TOKEN} environment variable syntax"
        )

    def test_datasource_no_hardcoded_tokens(self):
        """Verify no hard-coded tokens exist in datasource configuration."""
        with open(DATASOURCE_PATH, 'r') as f:
            content = f.read()

        # Common token patterns to avoid
        suspicious_patterns = [
            r'token:\s+[a-zA-Z0-9]{20,}',  # Long alphanumeric strings after 'token:'
            r'token:\s+"[^$][a-zA-Z0-9_-]+"',  # Quoted strings not starting with $
            r'token:\s+\'[^$][a-zA-Z0-9_-]+\'',  # Single-quoted strings not starting with $
        ]

        for pattern in suspicious_patterns:
            matches = re.findall(pattern, content)
            # Filter out the valid ${INFLUXDB_TOKEN} pattern
            hardcoded = [m for m in matches if "${INFLUXDB_TOKEN}" not in m]

            assert len(hardcoded) == 0, (
                f"Found potential hard-coded token: {hardcoded}. "
                "Use environment variable ${INFLUXDB_TOKEN} instead."
            )

    def test_datasource_token_in_secure_section(self):
        """Verify token is in secureJsonData section (not exposed in API)."""
        with open(DATASOURCE_PATH, 'r') as f:
            content = f.read()

        # Token should be under secureJsonData, not jsonData
        lines = content.split('\n')
        token_line_idx = None
        secure_section_idx = None

        for i, line in enumerate(lines):
            if 'secureJsonData:' in line:
                secure_section_idx = i
            if 'token:' in line and '${INFLUXDB_TOKEN}' in line:
                token_line_idx = i

        assert secure_section_idx is not None, "Should have secureJsonData section"
        assert token_line_idx is not None, "Should have token field"
        assert token_line_idx > secure_section_idx, (
            "Token should be under secureJsonData section for security"
        )

    def test_datasource_has_correct_uid(self):
        """Verify datasource has the expected UID for dashboard references."""
        with open(DATASOURCE_PATH, 'r') as f:
            content = f.read()

        expected_uid = "influxdb-datasource"

        assert f"uid: {expected_uid}" in content, (
            f"Datasource should have UID '{expected_uid}' to match dashboard references"
        )

    def test_datasource_configuration_structure(self):
        """Verify datasource has required configuration fields."""
        with open(DATASOURCE_PATH, 'r') as f:
            content = f.read()

        required_fields = [
            "name:",
            "type:",
            "access:",
            "url:",
            "uid:",
            "jsonData:",
            "organization:",
            "defaultBucket:",
            "secureJsonData:",
            "token:"
        ]

        for field in required_fields:
            assert field in content, f"Datasource configuration should have '{field}' field"

    def test_datasource_influxdb_settings(self):
        """Verify InfluxDB-specific settings are correct."""
        with open(DATASOURCE_PATH, 'r') as f:
            content = f.read()

        # Check for InfluxDB v2 (Flux) configuration
        assert "version: Flux" in content, "Should use InfluxDB v2 (Flux)"
        assert "organization: speedmonitor" in content, "Should reference speedmonitor org"
        assert "defaultBucket: speedtest" in content, "Should reference speedtest bucket"
        assert "url: http://influxdb:8086" in content, "Should reference InfluxDB container"


class TestConfigurationIntegration:
    """Integration tests validating dashboard and datasource work together."""

    def test_datasource_uid_matches_dashboard_references(self):
        """Verify datasource UID matches all dashboard panel references."""
        # Load dashboard
        with open(DASHBOARD_PATH, 'r') as f:
            dashboard = json.load(f)

        # Load datasource configuration
        with open(DATASOURCE_PATH, 'r') as f:
            datasource_content = f.read()

        # Extract datasource UID from YAML (simple regex)
        datasource_uid_match = re.search(r'uid:\s+([a-zA-Z0-9_-]+)', datasource_content)
        assert datasource_uid_match, "Could not find datasource UID in YAML"
        datasource_uid = datasource_uid_match.group(1)

        # Check all dashboard panels reference this datasource UID
        panels = dashboard.get("panels", [])

        for panel in panels:
            targets = panel.get("targets", [])
            for target in targets:
                panel_datasource_uid = target.get("datasource", {}).get("uid")

                assert panel_datasource_uid == datasource_uid, (
                    f"Panel {panel.get('id')} references '{panel_datasource_uid}', "
                    f"but datasource UID is '{datasource_uid}'"
                )

    def test_bucket_names_consistent(self):
        """Verify bucket names are consistent between datasource and dashboard queries."""
        # Load dashboard
        with open(DASHBOARD_PATH, 'r') as f:
            dashboard = json.load(f)

        # Load datasource
        with open(DATASOURCE_PATH, 'r') as f:
            datasource_content = f.read()

        # Extract bucket from datasource
        bucket_match = re.search(r'defaultBucket:\s+(\w+)', datasource_content)
        assert bucket_match, "Could not find defaultBucket in datasource"
        datasource_bucket = bucket_match.group(1)

        # Check dashboard queries reference the same bucket
        panels = dashboard.get("panels", [])

        for panel in panels:
            targets = panel.get("targets", [])
            for target in targets:
                query = target.get("query", "")
                if query:
                    # Extract bucket from Flux query
                    query_bucket_match = re.search(r'from\(bucket:\s+"(\w+)"\)', query)
                    if query_bucket_match:
                        query_bucket = query_bucket_match.group(1)
                        assert query_bucket == datasource_bucket, (
                            f"Panel {panel.get('id')} queries bucket '{query_bucket}', "
                            f"but datasource default bucket is '{datasource_bucket}'"
                        )

    def test_environment_variable_format(self):
        """Verify environment variables use consistent format."""
        with open(DATASOURCE_PATH, 'r') as f:
            content = f.read()

        # Find all environment variable references
        env_vars = re.findall(r'\$\{([A-Z_]+)\}', content)

        # Should have at least INFLUXDB_TOKEN
        assert len(env_vars) >= 1, "Should have at least one environment variable reference"
        assert "INFLUXDB_TOKEN" in env_vars, "Should reference INFLUXDB_TOKEN"

        # Verify format is ${VAR_NAME} not $VAR_NAME or other formats
        invalid_formats = re.findall(r'\$[A-Z_]+(?!\{)', content)
        assert len(invalid_formats) == 0, (
            f"Found invalid environment variable format: {invalid_formats}. "
            "Use ${VAR_NAME} format."
        )


class TestConfigurationSecurity:
    """Security-focused tests for configuration files."""

    def test_no_credentials_in_dashboard(self):
        """Verify dashboard JSON doesn't contain any credentials."""
        with open(DASHBOARD_PATH, 'r') as f:
            content = f.read().lower()

        # Sensitive keywords that shouldn't appear in plain text
        sensitive_patterns = ['password', 'secret', 'apikey', 'api_key']

        for pattern in sensitive_patterns:
            assert pattern not in content or f'"{pattern}"' in content, (
                f"Dashboard should not contain '{pattern}' credentials"
            )

    def test_datasource_token_not_in_jsondata(self):
        """Verify token is not in jsonData (which is exposed via API)."""
        with open(DATASOURCE_PATH, 'r') as f:
            lines = f.read().split('\n')

        in_jsondata = False
        in_securejsondata = False

        for line in lines:
            if 'jsonData:' in line and 'secureJsonData' not in line:
                in_jsondata = True
                in_securejsondata = False
            elif 'secureJsonData:' in line:
                in_securejsondata = True
                in_jsondata = False
            elif 'token:' in line:
                assert not in_jsondata, (
                    "Token should not be in jsonData section (security risk). "
                    "Use secureJsonData instead."
                )
                assert in_securejsondata, (
                    "Token should be in secureJsonData section"
                )
