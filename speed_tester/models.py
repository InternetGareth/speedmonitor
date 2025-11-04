from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SpeedTestResult:
    timestamp: datetime
    download_speed: float  # Mbps
    upload_speed: float    # Mbps
    ping: float           # milliseconds
    server_id: Optional[str] = None
    server_name: Optional[str] = None
    server_country: Optional[str] = None