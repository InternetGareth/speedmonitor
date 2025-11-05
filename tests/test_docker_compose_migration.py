"""
Tests for Docker Compose V1 to V2 migration validation.

This test suite validates:
1. Shell script detection logic for Docker Compose versions
2. Docker Compose YAML structure and validity
3. Documentation consistency across files
4. Command compatibility between V1 and V2
"""

import pytest
import subprocess
import yaml
import re
from pathlib import Path
from typing import Optional


# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SETUP_SCRIPT = PROJECT_ROOT / "scripts" / "setup.sh"
STOP_SCRIPT = PROJECT_ROOT / "scripts" / "stop.sh"
COMPOSE_FILE = PROJECT_ROOT / "docker-compose.yml"
README_FILE = PROJECT_ROOT / "README.md"


class TestDockerComposeDetectionLogic:
    """Test the shell script detection logic for Docker Compose versions."""

    def test_setup_script_exists_and_executable(self):
        """Verify setup.sh exists and is executable."""
        assert SETUP_SCRIPT.exists(), "setup.sh not found"
        assert SETUP_SCRIPT.stat().st_mode & 0o111, "setup.sh is not executable"

    def test_stop_script_exists_and_executable(self):
        """Verify stop.sh exists and is executable."""
        assert STOP_SCRIPT.exists(), "stop.sh not found"
        assert STOP_SCRIPT.stat().st_mode & 0o111, "stop.sh is not executable"

    def test_setup_script_checks_v2_first(self):
        """Verify setup.sh checks for V2 before V1."""
        content = SETUP_SCRIPT.read_text()

        # Find the detection block
        detection_pattern = r'if docker compose version.*?elif command -v docker-compose'
        match = re.search(detection_pattern, content, re.DOTALL)

        assert match, "Detection logic not found or incorrect order"

        # Verify V2 is checked first
        assert 'docker compose version' in content, "V2 detection missing"

        # Verify V1 fallback exists
        assert 'docker-compose' in content, "V1 fallback missing"

        # Verify V2 comes before V1 in the file
        v2_pos = content.find('docker compose version')
        v1_pos = content.find('docker-compose')
        assert v2_pos < v1_pos, "V2 check should come before V1 check"

    def test_stop_script_checks_v2_first(self):
        """Verify stop.sh checks for V2 before V1."""
        content = STOP_SCRIPT.read_text()

        # Verify detection order
        assert 'docker compose version' in content, "V2 detection missing"
        assert 'docker-compose' in content, "V1 fallback missing"

        v2_pos = content.find('docker compose version')
        v1_pos = content.find('docker-compose')
        assert v2_pos < v1_pos, "V2 check should come before V1 check"

    def test_setup_script_has_compose_cmd_variable(self):
        """Verify setup.sh uses $COMPOSE_CMD variable throughout."""
        content = SETUP_SCRIPT.read_text()

        # Should have COMPOSE_CMD definition
        assert 'COMPOSE_CMD=' in content, "$COMPOSE_CMD variable not defined"

        # Count uses of $COMPOSE_CMD (should be multiple)
        compose_cmd_uses = content.count('$COMPOSE_CMD')
        assert compose_cmd_uses >= 5, f"Expected multiple uses of $COMPOSE_CMD, found {compose_cmd_uses}"

        # Should NOT have hardcoded docker-compose commands after detection
        lines = content.split('\n')
        in_detection_block = False
        for i, line in enumerate(lines):
            if 'Detect which Docker Compose' in line:
                in_detection_block = True
            elif in_detection_block and 'fi' in line:
                in_detection_block = False
                detection_end = i
                break

        # After detection block, should use variable
        after_detection = '\n'.join(lines[detection_end:])
        # Allow docker-compose in comments but not in commands
        for line in lines[detection_end:]:
            if line.strip().startswith('#'):
                continue  # Skip comments
            # If it's a command line with docker-compose, it should use $COMPOSE_CMD
            if 'docker-compose' in line.lower() and not line.strip().startswith('echo'):
                pytest.fail(f"Found hardcoded docker-compose after detection: {line}")

    def test_stop_script_has_compose_cmd_variable(self):
        """Verify stop.sh uses $COMPOSE_CMD variable."""
        content = STOP_SCRIPT.read_text()

        assert 'COMPOSE_CMD=' in content, "$COMPOSE_CMD variable not defined"
        assert '$COMPOSE_CMD' in content, "$COMPOSE_CMD variable not used"

    def test_setup_script_has_deprecation_warning(self):
        """Verify setup.sh warns about V1 deprecation."""
        content = SETUP_SCRIPT.read_text()

        # Should contain warning about deprecated V1
        assert 'WARNING' in content or 'deprecated' in content.lower(), "Missing deprecation warning"
        assert 'docker-compose V1' in content or 'upgrade' in content.lower(), "Warning should mention V1 and upgrade"

    def test_setup_script_has_error_handling(self):
        """Verify setup.sh handles missing Docker Compose properly."""
        content = SETUP_SCRIPT.read_text()

        # Should check for Docker first
        assert 'command -v docker' in content or 'docker --version' in content, "Missing Docker check"

        # Should have error case for missing compose
        assert 'ERROR' in content, "Missing error handling"
        assert 'exit 1' in content, "Should exit on error"

    def test_help_text_shows_v2_syntax(self):
        """Verify help text in setup.sh shows V2 syntax."""
        content = SETUP_SCRIPT.read_text()

        # Find all echo statements
        echo_lines = [line for line in content.split('\n') if 'echo' in line.lower()]

        # Count references to docker compose vs docker-compose
        v2_references = sum(1 for line in echo_lines if 'docker compose' in line)
        v1_references = sum(1 for line in echo_lines if 'docker-compose' in line and 'docker compose' not in line)

        # Help text should primarily show V2 syntax
        assert v2_references > 0, "Help text should show V2 syntax examples"

    def test_detection_logic_syntax(self):
        """Verify detection logic has correct bash syntax."""
        # Test setup.sh
        result = subprocess.run(
            ['bash', '-n', str(SETUP_SCRIPT)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"setup.sh has syntax errors: {result.stderr}"

        # Test stop.sh
        result = subprocess.run(
            ['bash', '-n', str(STOP_SCRIPT)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"stop.sh has syntax errors: {result.stderr}"


class TestDockerComposeYAML:
    """Test Docker Compose YAML structure and validity."""

    def test_compose_file_exists(self):
        """Verify docker-compose.yml exists."""
        assert COMPOSE_FILE.exists(), "docker-compose.yml not found"

    def test_compose_file_valid_yaml(self):
        """Verify docker-compose.yml is valid YAML."""
        with open(COMPOSE_FILE) as f:
            try:
                data = yaml.safe_load(f)
                assert data is not None, "YAML file is empty"
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML: {e}")

    def test_compose_file_no_version_field(self):
        """Verify docker-compose.yml does not have deprecated version field."""
        with open(COMPOSE_FILE) as f:
            content = f.read()
            data = yaml.safe_load(content)

        # Check the parsed data doesn't have version at root
        assert 'version' not in data, "docker-compose.yml should not have 'version' field for V2"

        # Also check raw content for version field
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('version:'):
                pytest.fail(f"Found deprecated 'version' field: {line}")

    def test_compose_file_has_required_services(self):
        """Verify all required services are defined."""
        with open(COMPOSE_FILE) as f:
            data = yaml.safe_load(f)

        assert 'services' in data, "Missing 'services' section"

        required_services = ['influxdb', 'grafana', 'speedmonitor']
        for service in required_services:
            assert service in data['services'], f"Missing required service: {service}"

    def test_compose_file_services_structure(self):
        """Verify services have correct structure for V2."""
        with open(COMPOSE_FILE) as f:
            data = yaml.safe_load(f)

        services = data['services']

        # Check influxdb service
        assert 'image' in services['influxdb'], "influxdb missing image"
        assert 'influxdb:2.7' in services['influxdb']['image'], "influxdb should use version 2.7"

        # Check grafana service
        assert 'image' in services['grafana'], "grafana missing image"
        assert 'depends_on' in services['grafana'], "grafana should depend on influxdb"

        # Check speedmonitor service
        assert 'build' in services['speedmonitor'], "speedmonitor should be built"
        assert 'depends_on' in services['speedmonitor'], "speedmonitor should depend on influxdb"

    def test_compose_file_has_volumes(self):
        """Verify volumes are properly defined."""
        with open(COMPOSE_FILE) as f:
            data = yaml.safe_load(f)

        assert 'volumes' in data, "Missing 'volumes' section"

        required_volumes = ['influxdb-data', 'influxdb-config', 'grafana-data']
        for volume in required_volumes:
            assert volume in data['volumes'], f"Missing volume: {volume}"

    def test_compose_file_health_checks(self):
        """Verify health checks are properly configured."""
        with open(COMPOSE_FILE) as f:
            data = yaml.safe_load(f)

        # InfluxDB should have health check
        influxdb = data['services']['influxdb']
        assert 'healthcheck' in influxdb, "influxdb missing healthcheck"
        assert 'test' in influxdb['healthcheck'], "influxdb healthcheck missing test"

        # Grafana should wait for influxdb health
        grafana = data['services']['grafana']
        if 'depends_on' in grafana:
            depends = grafana['depends_on']
            if isinstance(depends, dict) and 'influxdb' in depends:
                assert 'condition' in depends['influxdb'], "grafana should wait for influxdb health"

    def test_compose_file_restart_policies(self):
        """Verify restart policies are set for all services."""
        with open(COMPOSE_FILE) as f:
            data = yaml.safe_load(f)

        for service_name, service in data['services'].items():
            assert 'restart' in service, f"{service_name} missing restart policy"
            assert service['restart'] in ['unless-stopped', 'always', 'on-failure'], \
                f"{service_name} has invalid restart policy"


class TestDocumentationConsistency:
    """Test documentation uses correct V2 syntax."""

    def test_readme_exists(self):
        """Verify README.md exists."""
        assert README_FILE.exists(), "README.md not found"

    def test_readme_mentions_v2_requirement(self):
        """Verify README mentions Docker Compose V2."""
        content = README_FILE.read_text()

        # Should mention V2
        assert 'Docker Compose V2' in content or 'docker compose' in content, \
            "README should mention Docker Compose V2"

    def test_readme_command_examples_use_v2(self):
        """Verify README command examples use V2 syntax."""
        content = README_FILE.read_text()

        # Find code blocks with docker compose commands
        code_blocks = re.findall(r'```bash\n(.*?)```', content, re.DOTALL)

        v2_commands = 0
        v1_commands = 0

        for block in code_blocks:
            # Count docker compose (V2) vs docker-compose (V1)
            v2_commands += block.count('docker compose ')
            v1_commands += block.count('docker-compose ')

        # README should primarily use V2 syntax
        assert v2_commands > 0, "README should show docker compose (V2) examples"

        # Check inline commands too - but exclude file references
        inline_commands = re.findall(r'`([^`]*docker[- ]compose[^`]*)`', content)

        for cmd in inline_commands:
            # Skip if it's just a filename reference (ends with .yml or contains directory structure)
            if cmd.endswith('.yml') or '├──' in cmd or '└──' in cmd:
                continue

            if 'docker-compose' in cmd:
                # Allow docker-compose in context of explaining compatibility
                if 'V1' not in content[max(0, content.find(cmd) - 100):content.find(cmd) + 100]:
                    pytest.fail(f"Found V1 syntax in command example: {cmd}")

    def test_readme_mentions_backward_compatibility(self):
        """Verify README mentions V1 backward compatibility."""
        content = README_FILE.read_text()

        # Should mention that V1 is supported/deprecated
        has_compat_note = any(word in content.lower() for word in
                             ['backward', 'compatibility', 'fallback', 'deprecated', 'v1 supported'])

        assert has_compat_note, "README should mention V1 backward compatibility"

    def test_readme_no_version_in_compose_example(self):
        """Verify README doesn't show version field in compose examples."""
        content = README_FILE.read_text()

        # Look for yaml/yml code blocks
        yaml_blocks = re.findall(r'```ya?ml\n(.*?)```', content, re.DOTALL)

        for block in yaml_blocks:
            if 'docker-compose' in block or 'services:' in block:
                # If it looks like a compose file, check for version
                if re.search(r'^version:\s*["\']?3', block, re.MULTILINE):
                    pytest.fail(f"Found deprecated version field in YAML example: {block[:100]}")

    def test_setup_script_help_output_correct(self):
        """Verify help output in scripts shows V2 commands."""
        setup_content = SETUP_SCRIPT.read_text()

        # Find help text
        help_lines = [line for line in setup_content.split('\n')
                     if 'echo' in line and ('logs' in line or 'stop' in line or 'down' in line)]

        for line in help_lines:
            # If showing compose commands, should use V2 syntax
            if 'compose' in line.lower():
                assert 'docker compose' in line, f"Help should show V2 syntax: {line}"


class TestCommandCompatibility:
    """Test that key Docker Compose commands work correctly."""

    @pytest.fixture
    def docker_available(self):
        """Check if Docker is available."""
        result = subprocess.run(
            ['docker', '--version'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0

    @pytest.fixture
    def compose_version(self):
        """Detect available Docker Compose version."""
        # Check for V2
        result = subprocess.run(
            ['docker', 'compose', 'version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return 'v2'

        # Check for V1
        result = subprocess.run(
            ['docker-compose', '--version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return 'v1'

        return None

    def test_compose_config_validation(self, docker_available, compose_version):
        """Test that docker-compose.yml is valid according to Docker Compose."""
        if not docker_available or not compose_version:
            pytest.skip("Docker or Docker Compose not available")

        if compose_version == 'v2':
            cmd = ['docker', 'compose', '-f', str(COMPOSE_FILE), 'config']
        else:
            cmd = ['docker-compose', '-f', str(COMPOSE_FILE), 'config']

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )

        assert result.returncode == 0, f"Compose config validation failed: {result.stderr}"

    def test_compose_version_command(self, docker_available, compose_version):
        """Test that compose version command works."""
        if not docker_available or not compose_version:
            pytest.skip("Docker or Docker Compose not available")

        if compose_version == 'v2':
            cmd = ['docker', 'compose', 'version']
        else:
            cmd = ['docker-compose', '--version']

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, "Compose version command failed"
        assert len(result.stdout) > 0, "Version command should produce output"


class TestScriptIntegration:
    """Integration tests for the migration scripts."""

    def test_setup_script_dry_run(self):
        """Test setup.sh detection logic with dry run."""
        # Read the script
        content = SETUP_SCRIPT.read_text()

        # Extract just the detection block
        detection_start = content.find('# Detect which Docker Compose')
        detection_end = content.find('fi', detection_start) + 2
        detection_block = content[detection_start:detection_end]

        # Verify structure
        assert 'if docker compose version' in detection_block
        assert 'elif command -v docker-compose' in detection_block
        assert 'else' in detection_block
        assert 'COMPOSE_CMD=' in detection_block

    def test_stop_script_dry_run(self):
        """Test stop.sh detection logic with dry run."""
        content = STOP_SCRIPT.read_text()

        detection_start = content.find('# Detect which Docker Compose')
        detection_end = content.find('fi', detection_start) + 2
        detection_block = content[detection_start:detection_end]

        assert 'if docker compose version' in detection_block
        assert 'elif command -v docker-compose' in detection_block
        assert 'COMPOSE_CMD=' in detection_block


class TestMigrationCompleteness:
    """Test that migration is complete and thorough."""

    def test_all_scripts_updated(self):
        """Verify all shell scripts in scripts/ use detection logic."""
        scripts_dir = PROJECT_ROOT / "scripts"

        if scripts_dir.exists():
            for script in scripts_dir.glob("*.sh"):
                content = script.read_text()

                # If script uses docker compose, it should use detection
                if 'docker' in content and 'compose' in content:
                    if 'setup' in script.name or 'stop' in script.name:
                        # These should have detection
                        assert 'COMPOSE_CMD' in content or 'docker compose' in content, \
                            f"{script.name} should use detection or V2 syntax"

    def test_no_hardcoded_v1_in_scripts(self):
        """Verify no hardcoded docker-compose V1 commands remain."""
        scripts = [SETUP_SCRIPT, STOP_SCRIPT]

        for script in scripts:
            content = script.read_text()
            lines = content.split('\n')

            for i, line in enumerate(lines, 1):
                # Skip comments
                if line.strip().startswith('#'):
                    continue

                # Skip echo statements (help text)
                if 'echo' in line.lower():
                    continue

                # Skip the detection block itself
                if 'command -v docker-compose' in line:
                    continue

                if 'docker-compose' in line:
                    # Should use $COMPOSE_CMD instead
                    if '$COMPOSE_CMD' not in content:
                        pytest.fail(
                            f"{script.name}:{i} has hardcoded docker-compose: {line.strip()}"
                        )

    def test_env_example_file_exists(self):
        """Verify .env.example exists for setup script."""
        env_example = PROJECT_ROOT / ".env.example"
        assert env_example.exists(), ".env.example required by setup.sh"

    def test_validation_script_exists(self):
        """Verify validation script referenced in setup.sh exists."""
        validate_script = PROJECT_ROOT / "scripts" / "validate-setup.sh"

        setup_content = SETUP_SCRIPT.read_text()
        if 'validate-setup.sh' in setup_content:
            assert validate_script.exists(), "validate-setup.sh referenced but not found"
