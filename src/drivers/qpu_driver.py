from __future__ import annotations

from collections.abc import Callable
from typing import Any

from src.config import config
from src.hal.base_driver import BaseHardwareDriver


class QPUDriver(BaseHardwareDriver):
    """Explicit quantum backend adapter.

    Importing qiskit is not sufficient evidence of a live QPU connection.
    Real execution requires an explicit executor callback supplied by the
    application after it authenticates and selects a provider/backend.
    """

    def __init__(
        self,
        executor: Callable[[int, int], dict[str, Any]] | None = None,
        backend_name: str = "local_statevector_simulator",
    ):
        self.executor = executor
        self.backend = backend_name
        self.mode = (
            "EXTERNAL_QPU_EXECUTOR"
            if config.USE_REAL_HARDWARE and executor is not None
            else "SIMULATION_ONLY"
        )

    def initialize(self) -> bool:
        return self.executor is not None or self.mode == "SIMULATION_ONLY"

    def execute_quantum_circuit(
        self,
        num_qubits: int = 2,
        shots: int = 1024,
    ) -> dict[str, Any]:
        if num_qubits <= 0:
            raise ValueError("num_qubits must be positive")
        if shots <= 0:
            raise ValueError("shots must be positive")

        if self.executor is not None:
            result = self.executor(num_qubits, shots)
            return {
                "status": "EXTERNAL_QPU_EXECUTOR_RESULT",
                "backend": self.backend,
                "num_qubits": num_qubits,
                "shots": shots,
                "result": result,
                "model_status": "provider_execution_supplied_by_caller",
            }

        # Deterministic compatibility simulation. This is not a quantum-device
        # result and makes no Bell/advantage claim.
        half = shots // 2
        return {
            "status": "SIMULATED_QUANTUM_COUNTS",
            "mode": self.mode,
            "backend": self.backend,
            "num_qubits": num_qubits,
            "shots": shots,
            "counts": {"00": half, "11": shots - half},
            "model_status": "simulation_only_no_qpu_job_submitted",
        }

    def get_status(self) -> dict[str, Any]:
        return {
            "driver": "QPUDriver",
            "active_mode": self.mode,
            "target_backend": self.backend,
            "external_executor_configured": self.executor is not None,
        }
