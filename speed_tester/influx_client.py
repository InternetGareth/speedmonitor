import logging
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from .models import SpeedTestResult


class InfluxDBService:
    def __init__(self, url: str, token: str, org: str, bucket: str):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.logger = logging.getLogger(__name__)
        
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        
    def write_speed_test_result(self, result: SpeedTestResult) -> None:
        try:
            point = (
                Point("internet_speed")
                .tag("server_id", result.server_id or "unknown")
                .tag("server_name", result.server_name or "unknown")
                .tag("server_country", result.server_country or "unknown")
                .field("download_speed", result.download_speed)
                .field("upload_speed", result.upload_speed)
                .field("ping", result.ping)
                .time(result.timestamp)
            )
            
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            self.logger.info(f"Successfully wrote speed test result to InfluxDB: {result.timestamp}")
            
        except Exception as e:
            self.logger.error(f"Failed to write to InfluxDB: {e}")
            raise
            
    def close(self) -> None:
        if self.client:
            self.client.close()
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()