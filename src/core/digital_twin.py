import numpy as np
from src.config import config

class DigitalTwinEngine:
    def __init__(self, max_stress_threshold: float = 100.0):
        self.max_stress_threshold = max_stress_threshold
        self.mode = "PHYSICAL_TWIN_LINK" if config.USE_REAL_HARDWARE else "VIRTUAL_TWIN_MOCK"

    def update_twin_state(self, thermal_c: float, vibration_tensor: list) -> dict:
        vib_arr = np.array(vibration_tensor, dtype=np.float32)
        vibration_magnitude = float(np.linalg.norm(vib_arr))
        
        # Calculate composite structural health index (0.0 = failure, 1.0 = optimal)
        stress_score = vibration_magnitude * (thermal_c / 25.0)
        health_index = max(0.0, float(1.0 - (stress_score / self.max_stress_threshold)))
        maintenance_required = health_index < 0.3

        return {
            "status": "TWIN_SYNC_COMPLETE",
            "execution_mode": self.mode,
            "thermal_celsius": thermal_c,
            "vibration_magnitude": vibration_magnitude,
            "composite_health_index": health_index,
            "predictive_maintenance_flag": maintenance_required
        }
