import pytest
from datetime import datetime
from speed_tester.models import SpeedTestResult


def test_speed_test_result_creation():
    timestamp = datetime.now()
    result = SpeedTestResult(
        timestamp=timestamp,
        download_speed=100.5,
        upload_speed=50.2,
        ping=25.7,
        server_id="12345",
        server_name="Test Server",
        server_country="US"
    )
    
    assert result.timestamp == timestamp
    assert result.download_speed == 100.5
    assert result.upload_speed == 50.2
    assert result.ping == 25.7
    assert result.server_id == "12345"
    assert result.server_name == "Test Server"
    assert result.server_country == "US"


def test_speed_test_result_optional_fields():
    timestamp = datetime.now()
    result = SpeedTestResult(
        timestamp=timestamp,
        download_speed=100.5,
        upload_speed=50.2,
        ping=25.7
    )
    
    assert result.timestamp == timestamp
    assert result.download_speed == 100.5
    assert result.upload_speed == 50.2
    assert result.ping == 25.7
    assert result.server_id is None
    assert result.server_name is None
    assert result.server_country is None