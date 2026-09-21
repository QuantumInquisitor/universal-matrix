from __future__ import annotations

import time
from typing import Any

from pydantic import BaseModel

from src.config import config

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
    """Fail-closed GRBL serial adapter.

    Real serial I/O requires the global two-step hardware arm, an explicit port,
    and pyserial. Otherwise the controller remains in mock mode.
    """

    def __init__(
        self,
        port: str | None = None,
        baudrate: int = 115200,
        mock_mode: bool = True,
    ):
        self.port = port
        self.baudrate = int(baudrate)
        self.mock_mode = (
            mock_mode
            or not config.USE_REAL_HARDWARE
            or serial is None
            or not port
        )
        self.serial_conn = None
        self.last_telemetry = MachinePosition()

        if not self.mock_mode:
            self._connect_serial()

    def _connect_serial(self) -> None:
        try:
            self.serial_conn = serial.Serial(
                self.port,
                self.baudrate,
                timeout=1,
                write_timeout=1,
            )
            time.sleep(2)
            self.serial_conn.reset_input_buffer()
        except (OSError, getattr(serial, "SerialException", OSError)):
            self.serial_conn = None
            self.mock_mode = True

    def send_gcode_line(self, gcode: str) -> dict[str, Any]:
        cleaned_cmd = gcode.strip()
        if not cleaned_cmd:
            return {"status": "EMPTY", "command": gcode}
        if "\n" in cleaned_cmd or "\r" in cleaned_cmd:
            raise ValueError("exactly one G-code line is permitted per call")
        if len(cleaned_cmd) > 512:
            raise ValueError("G-code line exceeds 512 characters")

        if self.mock_mode:
            return {
                "status": "OK_MOCK",
                "command": cleaned_cmd,
                "response": "ok",
                "model_status": "no_hardware_io",
            }

        if self.serial_conn is None or not self.serial_conn.is_open:
            raise RuntimeError("real CNC mode is not connected")

        self.serial_conn.write((cleaned_cmd + "\n").encode("ascii", errors="strict"))
        response = self.serial_conn.readline().decode("ascii", errors="replace").strip()
        return {
            "status": "OK" if "ok" in response.lower() else "ERROR",
            "command": cleaned_cmd,
            "response": response,
        }

    def poll_telemetry(self) -> MachinePosition:
        if self.mock_mode:
            return self.last_telemetry
        if self.serial_conn is None or not self.serial_conn.is_open:
            raise RuntimeError("real CNC mode is not connected")

        self.serial_conn.write(b"?\n")
        raw_status = self.serial_conn.readline().decode(
            "ascii",
            errors="replace",
        ).strip()

        if raw_status.startswith("<") and raw_status.endswith(">"):
            parts = raw_status[1:-1].split("|")
            state = parts[0]
            coords = None
            for part in parts[1:]:
                if part.startswith("MPos:"):
                    values = part[5:].split(",")
                    if len(values) >= 3:
                        coords = tuple(float(value) for value in values[:3])
                    break
            if coords is not None:
                x, y, z = coords
                self.last_telemetry = MachinePosition(
                    mpos_x=x,
                    mpos_y=y,
                    mpos_z=z,
                    wpos_x=x,
                    wpos_y=y,
                    wpos_z=z,
                    state=state,
                )
        return self.last_telemetry

    def close(self) -> None:
        if self.serial_conn is not None and self.serial_conn.is_open:
            self.serial_conn.close()
