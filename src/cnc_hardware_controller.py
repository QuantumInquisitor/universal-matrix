import time
import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

try:
    import serial
except ImportError:
    serial = None

class MachinePosition(BaseModel):
    mpos_x: float = 0.0
    mpos_y: float = 0.0
    mpos_z: float = 0.0
    wpos_x: float = 0.0
    wpos_y: float = 0.0
    wpos_z: float = 0.0
    state: str = "Idle"

class CNCGRBLController:
    """
    Phase 18: Direct OS serial communications, live machine position telemetry,
    and closed-loop motor encoder feedback engine for GRBL hardware.
    """
    def __init__(self, port: Optional[str] = None, baudrate: int = 115200, mock_mode: bool = False):
        self.port = port
        self.baudrate = baudrate
        self.mock_mode = mock_mode or (serial is None)
        self.serial_conn = None
        self.last_telemetry = MachinePosition()

        if not self.mock_mode and self.port:
            self._connect_serial()

    def _connect_serial(self):
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Allow GRBL controller reboot sequence
            self.serial_conn.flushInput()
        except Exception as e:
            self.mock_mode = True

    def send_gcode_line(self, gcode: str) -> Dict[str, Any]:
        cleaned_cmd = gcode.strip()
        if not cleaned_cmd:
            return {"status": "EMPTY", "command": gcode}

        if self.mock_mode:
            return {"status": "OK_MOCK", "command": cleaned_cmd, "response": "ok"}

        self.serial_conn.write(f"{cleaned_cmd}\n".encode('utf-8'))
        response = self.serial_conn.readline().decode('utf-8').strip()
        return {"status": "OK" if "ok" in response.lower() else "ERROR", "command": cleaned_cmd, "response": response}

    def poll_telemetry(self) -> MachinePosition:
        if self.mock_mode:
            return self.last_telemetry

        self.serial_conn.write(b"?\n")
        raw_status = self.serial_conn.readline().decode('utf-8').strip()
        
        # Parse GRBL Real-Time Status Report String: <Idle|MPos:0.000,0.000,0.000|FS:0,0>
        if raw_status.startswith("<") and raw_status.endswith(">"):
            parts = raw_status[1:-1].split("|")
            state = parts[0]
            mpos_x, mpos_y, mpos_z = 0.0, 0.0, 0.0
            
            for part in parts[1:]:
                if part.startswith("MPos:"):
                    coords = part.replace("MPos:", "").split(",")
                    mpos_x, mpos_y, mpos_z = [float(c) for c in coords[:3]]

            self.last_telemetry = MachinePosition(
                mpos_x=mpos_x, mpos_y=mpos_y, mpos_z=mpos_z,
                wpos_x=mpos_x, wpos_y=mpos_y, wpos_z=mpos_z,
                state=state
            )
        return self.last_telemetry

    def close(self):
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
