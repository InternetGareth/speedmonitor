import logging
import schedule
import time
from .config import Config
from .speed_test_service import SpeedTestService
from .influx_client import InfluxDBService


class SpeedMonitor:
    def __init__(self, config: Config):
        self.config = config
        self.speed_test_service = SpeedTestService()
        self.influx_service = InfluxDBService(
            url=config.influxdb_url,
            token=config.influxdb_token,
            org=config.influxdb_org,
            bucket=config.influxdb_bucket
        )
        
        logging.basicConfig(
            level=getattr(logging, config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def run_test_and_store(self):
        try:
            self.logger.info("Running scheduled speed test...")
            result = self.speed_test_service.run_speed_test(self.config.server_id)
            self.influx_service.write_speed_test_result(result)
            self.logger.info("Speed test completed and stored successfully")
        except Exception as e:
            self.logger.error(f"Speed test failed: {e}")
    
    def start_monitoring(self):
        self.logger.info(f"Starting speed monitor with {self.config.test_interval_minutes} minute intervals")
        
        schedule.every(self.config.test_interval_minutes).minutes.do(self.run_test_and_store)
        
        self.run_test_and_store()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Speed monitor stopped by user")
        finally:
            self.influx_service.close()


def main():
    config = Config.from_env()
    monitor = SpeedMonitor(config)
    monitor.start_monitoring()


if __name__ == "__main__":
    main()