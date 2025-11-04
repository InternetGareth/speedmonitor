import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from speed_tester.speed_test_service import SpeedTestService
from speed_tester.models import SpeedTestResult


@pytest.fixture
def speed_test_service():
    return SpeedTestService()


@patch('speed_tester.speed_test_service.speedtest.Speedtest')
def test_run_speed_test_success(mock_speedtest_class, speed_test_service):
    mock_speedtest = Mock()
    mock_speedtest_class.return_value = mock_speedtest
    
    mock_speedtest.download.return_value = 100_000_000  # 100 Mbps in bits
    mock_speedtest.upload.return_value = 50_000_000    # 50 Mbps in bits
    
    mock_results = Mock()
    mock_results.ping = 25.5
    mock_results.server = {
        'id': '12345',
        'name': 'Test Server',
        'country': 'US'
    }
    mock_speedtest.results = mock_results
    
    result = speed_test_service.run_speed_test()
    
    assert isinstance(result, SpeedTestResult)
    assert result.download_speed == 100.0
    assert result.upload_speed == 50.0
    assert result.ping == 25.5
    assert result.server_id == "12345"
    assert result.server_name == "Test Server"
    assert result.server_country == "US"
    assert isinstance(result.timestamp, datetime)
    
    mock_speedtest.get_best_server.assert_called_once()
    mock_speedtest.download.assert_called_once()
    mock_speedtest.upload.assert_called_once()


@patch('speed_tester.speed_test_service.speedtest.Speedtest')
def test_run_speed_test_with_server_id(mock_speedtest_class, speed_test_service):
    mock_speedtest = Mock()
    mock_speedtest_class.return_value = mock_speedtest
    
    mock_speedtest.download.return_value = 100_000_000
    mock_speedtest.upload.return_value = 50_000_000
    
    mock_results = Mock()
    mock_results.ping = 25.5
    mock_results.server = {
        'id': '67890',
        'name': 'Specific Server',
        'country': 'CA'
    }
    mock_speedtest.results = mock_results
    
    result = speed_test_service.run_speed_test(server_id="67890")
    
    mock_speedtest.get_servers.assert_called_once_with(["67890"])
    mock_speedtest.get_best_server.assert_not_called()


@patch('speed_tester.speed_test_service.speedtest.Speedtest')
def test_run_speed_test_exception(mock_speedtest_class, speed_test_service):
    mock_speedtest_class.side_effect = Exception("Network error")
    
    with pytest.raises(Exception, match="Network error"):
        speed_test_service.run_speed_test()