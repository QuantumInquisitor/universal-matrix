from __future__ import annotations

import os
import shutil
import subprocess

from src.config import config
from src.hal.base_driver import BaseHardwareDriver


class FPGADriver(BaseHardwareDriver):
    """FPGA toolchain availability adapter.

    The current implementation checks vendor-tool availability and can generate
    a simulated compilation manifest. It does not yet invoke synthesis,
    bitstream generation, device programming, or hardware flashing.
    """

    def __init__(self, toolchain_path: str | None = None, probe_timeout: float = 10.0):
        self.mode = "REAL_AVAILABLE" if config.USE_REAL_HARDWARE else "MOCK"
        self.toolchain_path = toolchain_path or os.getenv(
            "UNIVERSAL_MATRIX_FPGA_TOOLCHAIN",
            "vivado",
        )
        self.probe_timeout = float(probe_timeout)
        self.initialize()

    def initialize(self) -> bool:
        if self.mode != "REAL_AVAILABLE":
            return True

        resolved = shutil.which(self.toolchain_path)
        if resolved is None:
            self.mode = "MOCK_FALLBACK"
            return False

        try:
            result = subprocess.run(
                [resolved, "-version"],
                capture_output=True,
                text=True,
                timeout=self.probe_timeout,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            self.mode = "MOCK_FALLBACK"
            return False

        if result.returncode == 0:
            self.toolchain_path = resolved
            return True

        self.mode = "MOCK_FALLBACK"
        return False

    def compile_and_flash_hdl(self, hdl_source: str) -> dict:
        """Return a compatibility manifest without claiming an actual flash."""
        if not isinstance(hdl_source, str) or not hdl_source.strip():
            raise ValueError("hdl_source must be a non-empty string")

        if self.mode == "REAL_AVAILABLE":
            return {
                "status": "TOOLCHAIN_AVAILABLE_NO_FLASH_PERFORMED",
                "toolchain": self.toolchain_path,
                "hdl_length": len(hdl_source),
                "model_status": "synthesis_and_programming_not_implemented",
            }

        return {
            "status": "SIMULATED_FPGA_MANIFEST",
            "mode": self.mode,
            "hdl_length": len(hdl_source),
            "simulated_bitstream": "0xAA55FF00",
            "model_status": "simulation_only",
        }

    def get_status(self) -> dict:
        return {
            "driver": "FPGADriver",
            "active_mode": self.mode,
            "toolchain": self.toolchain_path,
        }
