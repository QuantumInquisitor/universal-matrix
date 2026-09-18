import time
from src.config import config

class SafetyInterlockDriver:
    def __init__(self):
        self.mode = "REAL" if config.USE_REAL_HARDWARE else "MOCK"
        self.is_e_stop_active = False
        self.max_velocity_limit = 1000.0  # Physical units/sec

    def validate_spatial_vector(self, velocity: float) -> dict:
        if abs(velocity) > self.max_velocity_limit:
            self.is_e_stop_active = True
            return {
                "status": "E_STOP_TRIGGERED",
                "reason": f"Velocity {velocity} exceeded safety limit {self.max_velocity_limit}",
                "hardware_locked": True
            }
        return {
            "status": "NOMINAL",
            "is_e_stop_active": self.is_e_stop_active,
            "hardware_locked": False
        }
