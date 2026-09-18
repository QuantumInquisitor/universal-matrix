from src.hal.base_driver import BaseHardwareDriver
from src.config import config

class CNCMotionDriver(BaseHardwareDriver):
    def __init__(self):
        self.mode = "REAL" if config.USE_REAL_HARDWARE else "MOCK"
        self.serial_port = None
        self.initialize()

    def initialize(self) -> bool:
        if self.mode == "REAL":
            try:
                import serial
                # Connect to physical GRBL / LinuxCNC serial controller
                self.serial_port = serial.Serial(port="/dev/ttyUSB0", baudrate=115200, timeout=1)
                return True
            except (ImportError, Exception):
                self.mode = "MOCK_FALLBACK"
                return False
        else:
            return True

    def execute_gcode_command(self, gcode_line: str) -> dict:
        if self.mode == "REAL" and self.serial_port:
            self.serial_port.write(f"{gcode_line}\n".encode())
            response = self.serial_port.readline().decode().strip()
            return {
                "status": "EXECUTED_REAL_GCODE",
                "command": gcode_line,
                "cnc_response": response
            }
        else:
            return {
                "status": "EXECUTED_MOCK_GCODE",
                "mode": self.mode,
                "command": gcode_line,
                "axis_position": {"X": 10.5, "Y": 20.0, "Z": -1.2}
            }

    def get_status(self) -> dict:
        return {
            "driver": "CNCMotionDriver",
            "active_mode": self.mode
        }

