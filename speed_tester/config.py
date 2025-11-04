import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    influxdb_url: str
    influxdb_token: str
    influxdb_org: str
    influxdb_bucket: str
    test_interval_minutes: int = 60
    server_id: Optional[str] = None
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            influxdb_url=os.getenv("INFLUXDB_URL", "http://localhost:8086"),
            influxdb_token=os.getenv("INFLUXDB_TOKEN", ""),
            influxdb_org=os.getenv("INFLUXDB_ORG", "speedmonitor"),
            influxdb_bucket=os.getenv("INFLUXDB_BUCKET", "speedtest"),
            test_interval_minutes=int(os.getenv("TEST_INTERVAL_MINUTES", "60")),
            server_id=os.getenv("SPEEDTEST_SERVER_ID"),
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )