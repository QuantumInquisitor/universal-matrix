from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
from pydantic import BaseModel, Field


class RFSignalConfig(BaseModel):
    center_freq_hz: float = Field(432_000_000.0, ge=1_000_000.0, le=6_000_000_000.0)
    sample_rate_hz: float = Field(2_000_000.0, ge=250_000.0, le=20_000_000.0)
    tx_gain_db: float = Field(14.0, ge=0.0, le=47.0)
    waveform_type: str = "sine"
    triad_phase_offset_rad: float = 0.0


class SDRRFSynthesizer:
    """I/Q waveform generator with explicit hardware-backend opt in.

    Historical 3/6/9 terminology is retained only in the compatibility field
    name triad_phase_offset_rad. The class does not establish any biological
    or unusual physical effect of those numbers.

    Real RF transmission is impossible unless a caller provides an explicit
    transmitter callback. This prevents simulation code from silently becoming
    a hardware-emission path.
    """

    def __init__(
        self,
        config: RFSignalConfig | None = None,
        mock_mode: bool = True,
        transmitter: Callable[[np.ndarray, RFSignalConfig], dict[str, Any]] | None = None,
    ):
        self.config = config or RFSignalConfig()
        self.mock_mode = mock_mode
        self.transmitter = transmitter

    def generate_complex_iq(self, num_samples: int = 1024) -> np.ndarray:
        if num_samples <= 0:
            raise ValueError("num_samples must be positive")
        t = np.arange(num_samples, dtype=np.float64) / self.config.sample_rate_hz
        phase = (
            2.0 * np.pi * self.config.center_freq_hz * t
            + self.config.triad_phase_offset_rad
        )
        return np.exp(1j * phase)

    def generate_iq_samples(self, num_samples: int = 1024) -> list[dict[str, float]]:
        samples = self.generate_complex_iq(num_samples)
        return [
            {"i": round(float(value.real), 6), "q": round(float(value.imag), 6)}
            for value in samples
        ]

    def transmit_carrier_burst(self, num_samples: int = 1024) -> dict[str, Any]:
        samples = self.generate_complex_iq(num_samples)

        if self.mock_mode:
            return {
                "status": "SIMULATED_RF_BURST",
                "center_freq_hz": self.config.center_freq_hz,
                "sample_rate_hz": self.config.sample_rate_hz,
                "gain_db": self.config.tx_gain_db,
                "samples_count": int(samples.size),
                "hardware_device": None,
                "model_status": "simulation_only",
            }

        if self.transmitter is None:
            raise RuntimeError(
                "Real RF mode requires an explicit transmitter backend; "
                "no hardware transmission was attempted"
            )

        return self.transmitter(samples, self.config)
