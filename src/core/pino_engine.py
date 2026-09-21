"""Legacy-compatible numerical guardrail.

The historical class name is retained for API compatibility. The current
implementation is not a Physics-Informed Neural Operator: it contains no trained
neural operator, PDE residual loss, spectral operator layers, or learned model.
It is a simple numeric threshold guardrail.
"""

import numpy as np


class PhysicsInformedOperator:
    def __init__(self, threshold: float = 500.0, *args, **kwargs):
        _ = args
        if "energy_threshold" in kwargs:
            threshold = kwargs["energy_threshold"]
        self.threshold = float(threshold)

    def enforce_conservation_laws(self, move):
        arr = np.asarray(move, dtype=float)
        aggregate = float(np.sum(arr))
        is_valid = aggregate < self.threshold
        return {
            "is_physically_valid": is_valid,
            "status": "PASS" if is_valid else "THRESHOLD_EXCEEDED",
            "total_energy": aggregate,  # deprecated historical key
            "aggregate_value": aggregate,
            "threshold": self.threshold,
            "model_status": "heuristic_guardrail_not_pino_or_conservation_proof",
        }
