import urllib.request
import json
from src.hal.base_driver import BaseHardwareDriver
from src.config import config

class SpaceXDriver(BaseHardwareDriver):
    def __init__(self):
        self.mode = "REAL" if config.USE_REAL_HARDWARE else "MOCK"
        self.api_url = "https://api.spacexdata.com/v4/starlink"
        self.initialize()

    def initialize(self) -> bool:
        if self.mode == "REAL":
            try:
                # Ping live telemetry endpoint
                req = urllib.request.Request(self.api_url, headers={"User-Agent": "UniversalMatrix-HAL/1.0"})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    if resp.status == 200:
                        return True
                self.mode = "MOCK_FALLBACK"
                return False
            except Exception:
                self.mode = "MOCK_FALLBACK"
                return False
        else:
            return True

    def get_constellation_telemetry(self, limit: int = 5) -> dict:
        if self.mode == "REAL":
            try:
                req = urllib.request.Request(self.api_url, headers={"User-Agent": "UniversalMatrix-HAL/1.0"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    satellites = []
                    for sat in data[:limit]:
                        satellites.append({
                            "id": sat.get("id"),
                            "spaceTrack": sat.get("spaceTrack", {}).get("OBJECT_NAME"),
                            "latitude": sat.get("latitude"),
                            "longitude": sat.get("longitude"),
                            "height_km": sat.get("height_km"),
                            "velocity_kms": sat.get("velocity_kms")
                        })
                    return {
                        "status": "LIVE_SPACEX_TELEMETRY_SUCCESS",
                        "satellite_count": len(satellites),
                        "satellites": satellites
                    }
            except Exception as e:
                return {"status": "SPACEX_API_ERROR", "error": str(e)}
        else:
            return {
                "status": "MOCK_SPACEX_TELEMETRY_SUCCESS",
                "mode": self.mode,
                "satellite_count": limit,
                "satellites": [
                    {
                        "id": "5ece25a821d1140006e8423d",
                        "spaceTrack": "STARLINK-31",
                        "latitude": 34.0522,
                        "longitude": -118.2437,
                        "height_km": 550.2,
                        "velocity_kms": 7.59
                    }
                ]
            }

    def get_status(self) -> dict:
        return {
            "driver": "SpaceXDriver",
            "active_mode": self.mode
        }

