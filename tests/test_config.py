import pytest
from unittest.mock import patch
from speed_tester.config import Config


def test_config_from_env_defaults():
    with patch.dict('os.environ', {}, clear=True):
        config = Config.from_env()
        
        assert config.influxdb_url == "http://localhost:8086"
        assert config.influxdb_token == ""
        assert config.influxdb_org == "speedmonitor"
        assert config.influxdb_bucket == "speedtest"
        assert config.test_interval_minutes == 60
        assert config.server_id is None
        assert config.log_level == "INFO"


def test_config_from_env_custom():
    env_vars = {
        'INFLUXDB_URL': 'http://custom:8086',
        'INFLUXDB_TOKEN': 'custom-token',
        'INFLUXDB_ORG': 'custom-org',
        'INFLUXDB_BUCKET': 'custom-bucket',
        'TEST_INTERVAL_MINUTES': '30',
        'SPEEDTEST_SERVER_ID': '12345',
        'LOG_LEVEL': 'DEBUG'
    }
    
    with patch.dict('os.environ', env_vars, clear=True):
        config = Config.from_env()
        
        assert config.influxdb_url == "http://custom:8086"
        assert config.influxdb_token == "custom-token"
        assert config.influxdb_org == "custom-org"
        assert config.influxdb_bucket == "custom-bucket"
        assert config.test_interval_minutes == 30
        assert config.server_id == "12345"
        assert config.log_level == "DEBUG"


def test_config_creation():
    config = Config(
        influxdb_url="http://test:8086",
        influxdb_token="test-token",
        influxdb_org="test-org",
        influxdb_bucket="test-bucket",
        test_interval_minutes=120,
        server_id="67890",
        log_level="WARNING"
    )
    
    assert config.influxdb_url == "http://test:8086"
    assert config.influxdb_token == "test-token"
    assert config.influxdb_org == "test-org"
    assert config.influxdb_bucket == "test-bucket"
    assert config.test_interval_minutes == 120
    assert config.server_id == "67890"
    assert config.log_level == "WARNING"