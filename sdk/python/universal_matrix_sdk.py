from __future__ import annotations

from collections.abc import Iterable

import requests


class UniversalMatrixClient:
    """Small synchronous client for the current research API.

    Network operations always use finite timeouts and raise on HTTP errors.
    Legacy methods remain available for compatibility but target the legacy API.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        api_key: str | None = None,
        timeout: tuple[float, float] = (3.0, 15.0),
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "UniversalMatrixClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _get(self, path: str) -> dict:
        response = self.session.get(
            f"{self.base_url}{path}",
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def _post(self, path: str, payload: dict) -> dict:
        response = self.session.post(
            f"{self.base_url}{path}",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def get_health(self) -> dict:
        return self._get("/health")

    def evaluate_matrix(self, values: Iterable[float]) -> dict:
        return self._post(
            "/api/v1/matrix/evaluate",
            {"tensor_input": list(values)},
        )

    def compile_gcode(self, trajectory_nodes: list[dict[str, float]]) -> dict:
        return self._post(
            "/api/v1/gcode/compile",
            {"trajectory_nodes": trajectory_nodes},
        )

    # Legacy compatibility API methods. These routes are not part of the
    # smaller src.api_server research surface.
    def evaluate_agent(self, nodes: list) -> dict:
        return self._post("/api/v1/agent/evaluate", {"nodes": nodes})

    def simulate_photonic(self, input_vector: list, phase_shifts: list) -> dict:
        return self._post(
            "/api/v1/hardware/photonic/multiply",
            {"input_vector": input_vector, "phase_shifts": phase_shifts},
        )
