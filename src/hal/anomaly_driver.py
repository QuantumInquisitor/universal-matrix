import numpy as np
from src.config import config

class SpatialAnomalyDriver:
    def __init__(self, drift_tolerance: float = 0.05):
        self.mode = "REAL" if config.USE_REAL_HARDWARE else "MOCK"
        self.drift_tolerance = drift_tolerance

    def evaluate_and_correct(self, target_vector: list, feedback_vector: list) -> dict:
        target = np.array(target_vector, dtype=np.float32)
        feedback = np.array(feedback_vector, dtype=np.float32)

        drift_delta = target - feedback
        drift_magnitude = float(np.linalg.norm(drift_delta))

        drift_detected = drift_magnitude > self.drift_tolerance
        corrected_vector = (target + drift_delta).tolist() if drift_detected else target_vector

        return {
            "status": "ANOMALY_CORRECTED" if drift_detected else "NOMINAL_ALIGNMENT",
            "drift_magnitude": drift_magnitude,
            "drift_detected": drift_detected,
            "corrected_vector": corrected_vector
        }
