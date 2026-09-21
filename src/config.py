from __future__ import annotations

import os


def _env_true(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


class SystemConfig:
    """Fail-closed runtime configuration.

    Real hardware requires both:
      UNIVERSAL_MATRIX_SYSTEM_MODE=REAL
      UNIVERSAL_MATRIX_ALLOW_HARDWARE=1

    The older SYSTEM_MODE variable remains a compatibility fallback.
    """

    SYSTEM_MODE = os.getenv(
        "UNIVERSAL_MATRIX_SYSTEM_MODE",
        os.getenv("SYSTEM_MODE", "MOCK"),
    ).upper()
    if SYSTEM_MODE not in {"MOCK", "REAL"}:
        raise RuntimeError("SYSTEM_MODE must be MOCK or REAL")

    HARDWARE_ARMED = _env_true("UNIVERSAL_MATRIX_ALLOW_HARDWARE")
    USE_REAL_HARDWARE = SYSTEM_MODE == "REAL" and HARDWARE_ARMED

    CAN_CHANNEL = os.getenv("CAN_CHANNEL", "can0")
    CUDA_DEVICE_ID = int(os.getenv("CUDA_DEVICE_ID", "0"))
    EVM_RPC_URL = os.getenv("EVM_RPC_URL", "https://rpc.sepolia.org")


config = SystemConfig()
