import logging
import speedtest
from datetime import datetime
from typing import Optional
from .models import SpeedTestResult


class SpeedTestService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def run_speed_test(self, server_id: Optional[str] = None) -> SpeedTestResult:
        try:
            self.logger.info("Starting speed test...")
            
            st = speedtest.Speedtest()
            
            if server_id:
                st.get_servers([server_id])
            else:
                st.get_best_server()
            
            self.logger.info("Running download test...")
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            
            self.logger.info("Running upload test...")
            upload_speed = st.upload() / 1_000_000  # Convert to Mbps
            
            results = st.results
            ping = results.ping
            
            server_info = results.server
            
            result = SpeedTestResult(
                timestamp=datetime.now(),
                download_speed=round(download_speed, 2),
                upload_speed=round(upload_speed, 2),
                ping=round(ping, 2),
                server_id=str(server_info.get('id', '')),
                server_name=server_info.get('name', ''),
                server_country=server_info.get('country', '')
            )
            
            self.logger.info(f"Speed test completed: {result.download_speed} Mbps down, "
                           f"{result.upload_speed} Mbps up, {result.ping} ms ping")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Speed test failed: {e}")
            raise