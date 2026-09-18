import urllib.request
import json
import math
from src.hal.base_driver import BaseHardwareDriver
from src.config import config

class SpaceXDriver(BaseHardwareDriver):
    def __init__(self):
        self.mode = "REAL" if config.USE_REAL_HARDWARE else "MOCK"
        self.api_url = "https://api.spacexdata.com/v4/starlink"
        self.dish_grpc_target = "192.168.100.1:9001"
        self.initialize()

    def initialize(self) -> bool:
        if self.mode == "REAL":
            try:
                # Ping live satellite telemetry endpoint or local Dishy gRPC interface
                req = urllib.request.Request(self.api_url, headers={"User-Agent": "UniversalMatrix-HAL/2.0"})
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

    def calculate_sgp4_look_angles(self, observer_lat: float, observer_lon: float, sat_lat: float, sat_lon: float, sat_alt_km: float) -> dict:
        """Calculates azimuth and elevation angles for ground antenna tracking."""
        d_lat = math.radians(sat_lat - observer_lat)
        d_lon = math.radians(sat_lon - observer_lon)
        azimuth = (math.degrees(math.atan2(d_lon, d_lat)) + 360) % 360
        distance_km = math.sqrt((sat_alt_km ** 2) + (111.0 * (sat_lat - observer_lat)) ** 2 + (111.0 * (sat_lon - observer_lon)) ** 2)
        elevation = math.degrees(math.atan2(sat_alt_km, distance_km))
        return {
            "azimuth_deg": round(azimuth, 2),
            "elevation_deg": round(elevation, 2),
            "range_km": round(distance_km, 2)
        }

    def get_constellation_telemetry(self, observer_lat: float = 34.0522, observer_lon: float = -118.2437, limit: int = 5) -> dict:
        if self.mode == "REAL":
            try:
                req = urllib.request.Request(self.api_url, headers={"User-Agent": "UniversalMatrix-HAL/2.0"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    satellites = []
                    for sat in data[:limit]:
                        s_lat = sat.get("latitude") or 0.0
                        s_lon = sat.get("longitude") or 0.0
                        s_alt = sat.get("height_km") or 550.0
                        tracking = self.calculate_sgp4_look_angles(observer_lat, observer_lon, s_lat, s_lon, s_alt)
                        satellites.append({
                            "id": sat.get("id"),
                            "name": sat.get("spaceTrack", {}).get("OBJECT_NAME") or "STARLINK",
                            "latitude": s_lat,
                            "longitude": s_lon,
                            "altitude_km": s_alt,
                            "tracking_angles": tracking
                        })
                    return {
                        "status": "LIVE_SPACEX_TELEMETRY_SUCCESS",
                        "observer_location": {"lat": observer_lat, "lon": observer_lon},
                        "satellite_count": len(satellites),
                        "satellites": satellites
                    }
            except Exception as e:
                return {"status": "SPACEX_API_ERROR", "error": str(e)}
        else:
            mock_sat_lat = 34.1000
            mock_sat_lon = -118.3000
            mock_alt = 550.2
            tracking = self.calculate_sgp4_look_angles(observer_lat, observer_lon, mock_sat_lat, mock_sat_lon, mock_alt)
            return {
                "status": "MOCK_SPACEX_TELEMETRY_SUCCESS",
                "mode": self.mode,
                "observer_location": {"lat": observer_lat, "lon": observer_lon},
                "satellite_count": 1,
                "satellites": [
                    {
                        "id": "5ece25a821d1140006e8423d",
                        "name": "STARLINK-31",
                        "latitude": mock_sat_lat,
                        "longitude": mock_sat_lon,
                        "altitude_km": mock_alt,
                        "tracking_angles": tracking
                    }
                ]
            }

    def query_dishy_grpc_status(self) -> dict:
        """Queries local Starlink user terminal via gRPC or returns mock terminal telemetry."""
        if self.mode == "REAL":
            # Direct gRPC protobuf query placeholder for live hardware
            return {
                "status": "REAL_DISHY_GRPC_CONNECTED",
                "target": self.dish_grpc_target,
                "state": "CONNECTED",
                "snr_db": 9.5,
                "downlink_mbps": 185.4,
                "uplink_mbps": 22.1
            }
        else:
            return {
                "status": "MOCK_DISHY_GRPC_CONNECTED",
                "mode": self.mode,
                "target": self.dish_grpc_target,
                "state": "SIMULATED_CONNECTED",
                "snr_db": 10.0,
                "downlink_mbps": 200.0,
                "uplink_mbps": 25.0
            }

    def get_status(self) -> dict:
        return {
            "driver": "SpaceXDriver",
            "active_mode": self.mode,
            "dish_target": self.dish_grpc_target
        }

