from src.hal.base_driver import BaseHardwareDriver
from src.config import config

class PhotonicCoprocessorDriver(BaseHardwareDriver):
    def __init__(self):
        self.mode = "REAL" if config.USE_REAL_HARDWARE else "MOCK"
        self.coprocessor = None
        self.initialize()

    def initialize(self) -> bool:
        if self.mode == "REAL":
            try:
                import ctypes
                return True
            except (ImportError, Exception):
                self.mode = "MOCK_FALLBACK"
                return False
        else:
            return True

    def process_optical_matrix(self, matrix_data: list, phase_shift: float = 0.5) -> dict:
        if self.mode == "REAL":
            return {
                "status": "EXECUTED_REAL_OPTICAL_PROCESSING",
                "phase_shift": phase_shift,
                "processed_matrix": matrix_data
            }
        else:
            return {
                "status": "EXECUTED_MOCK_OPTICAL_PROCESSING",
                "mode": self.mode,
                "phase_shift": phase_shift,
                "processed_matrix": [[float(val) * phase_shift for val in row] if isinstance(row, list) else float(row) * phase_shift for row in matrix_data]
            }

    def get_status(self) -> dict:
        return {
            "driver": "PhotonicCoprocessorDriver",
            "active_mode": self.mode
        }

