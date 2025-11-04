import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from speed_tester.influx_client import InfluxDBService
from speed_tester.models import SpeedTestResult


@pytest.fixture
def speed_test_result():
    return SpeedTestResult(
        timestamp=datetime(2023, 1, 1, 12, 0, 0),
        download_speed=100.5,
        upload_speed=50.2,
        ping=25.7,
        server_id="12345",
        server_name="Test Server",
        server_country="US"
    )


@patch('speed_tester.influx_client.InfluxDBClient')
def test_influx_service_initialization(mock_client_class):
    mock_client = Mock()
    mock_write_api = Mock()
    mock_client.write_api.return_value = mock_write_api
    mock_client_class.return_value = mock_client
    
    service = InfluxDBService(
        url="http://localhost:8086",
        token="test-token",
        org="test-org",
        bucket="test-bucket"
    )
    
    assert service.url == "http://localhost:8086"
    assert service.token == "test-token"
    assert service.org == "test-org"
    assert service.bucket == "test-bucket"
    mock_client_class.assert_called_once_with(
        url="http://localhost:8086",
        token="test-token",
        org="test-org"
    )


@patch('speed_tester.influx_client.InfluxDBClient')
@patch('speed_tester.influx_client.Point')
def test_write_speed_test_result_success(mock_point_class, mock_client_class, speed_test_result):
    mock_client = Mock()
    mock_write_api = Mock()
    mock_client.write_api.return_value = mock_write_api
    mock_client_class.return_value = mock_client
    
    mock_point = Mock()
    mock_point.tag.return_value = mock_point
    mock_point.field.return_value = mock_point
    mock_point.time.return_value = mock_point
    mock_point_class.return_value = mock_point
    
    service = InfluxDBService(
        url="http://localhost:8086",
        token="test-token",
        org="test-org",
        bucket="test-bucket"
    )
    
    service.write_speed_test_result(speed_test_result)
    
    mock_point_class.assert_called_once_with("internet_speed")
    
    expected_tag_calls = [
        (("server_id", "12345"),),
        (("server_name", "Test Server"),),
        (("server_country", "US"),)
    ]
    assert mock_point.tag.call_args_list == expected_tag_calls
    
    expected_field_calls = [
        (("download_speed", 100.5),),
        (("upload_speed", 50.2),),
        (("ping", 25.7),)
    ]
    assert mock_point.field.call_args_list == expected_field_calls
    
    mock_point.time.assert_called_once_with(speed_test_result.timestamp)
    mock_write_api.write.assert_called_once_with(
        bucket="test-bucket",
        org="test-org",
        record=mock_point
    )


@patch('speed_tester.influx_client.InfluxDBClient')
def test_write_speed_test_result_exception(mock_client_class, speed_test_result):
    mock_client = Mock()
    mock_write_api = Mock()
    mock_write_api.write.side_effect = Exception("Connection error")
    mock_client.write_api.return_value = mock_write_api
    mock_client_class.return_value = mock_client
    
    service = InfluxDBService(
        url="http://localhost:8086",
        token="test-token",
        org="test-org",
        bucket="test-bucket"
    )
    
    with pytest.raises(Exception, match="Connection error"):
        service.write_speed_test_result(speed_test_result)


@patch('speed_tester.influx_client.InfluxDBClient')
def test_context_manager(mock_client_class):
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    
    with InfluxDBService(
        url="http://localhost:8086",
        token="test-token",
        org="test-org",
        bucket="test-bucket"
    ) as service:
        assert service is not None
    
    mock_client.close.assert_called_once()