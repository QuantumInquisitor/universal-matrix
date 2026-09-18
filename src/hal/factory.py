from src.config import config

class HALFactory:
    @staticmethod
    def get_driver_mode() -> str:
        return "REAL_WORLD_BARE_METAL" if config.USE_REAL_HARDWARE else "SIMULATED_MOCK_HIL"

