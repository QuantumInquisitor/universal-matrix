from src.hal.base_driver import BaseHardwareDriver
from src.config import config
import src.hardware_mocks as hardware_mocks

class CANDriver(BaseHardwareDriver):
    def __init__(self):
        self.mode = "REAL" if config.USE_REAL_HARDWARE else "MOCK"
        self.bus = None
        self.initialize()

    def initialize(self) -> bool:
        if self.mode == "REAL":
            try:
                import can
                self.bus = can.interface.Bus(channel=config.CAN_CHANNEL, bustype="socketcan")
                return True
            except (ImportError, OSError):
                # Graceful fallback to MOCK if physical SocketCAN interface is missing
                self.mode = "MOCK_FALLBACK"
                return False
        else:
            return True

    def send_telemetry_frame(self, arbitration_id: int, data: list) -> dict:
        if self.mode == "REAL" and self.bus:
            import can
            msg = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=False)
            self.bus.send(msg)
            return {"status": "SENT_REAL_CAN_FRAME", "channel": config.CAN_CHANNEL, "id": arbitration_id}
        else:
            return {
                "status": "SENT_MOCK_CAN_FRAME",
                "mode": self.mode,
                "arbitration_id": arbitration_id,
                "payload": data
            }

    def get_status(self) -> dict:
        return {
            "driver": "CANDriver",
            "active_mode": self.mode,
            "target_channel": config.CAN_CHANNEL
        }

