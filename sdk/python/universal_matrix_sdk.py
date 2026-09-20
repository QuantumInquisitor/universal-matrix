import requests

class UniversalMatrixClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")

    def get_health(self) -> dict:
        response = requests.get(f"{self.base_url}/")
        return response.json()

    def evaluate_agent(self, nodes: list) -> dict:
        response = requests.post(f"{self.base_url}/api/v1/agent/evaluate", json={"nodes": nodes})
        return response.json()

    def simulate_photonic(self, input_vector: list, phase_shifts: list) -> dict:
        payload = {"input_vector": input_vector, "phase_shifts": phase_shifts}
        response = requests.post(f"{self.base_url}/api/v1/hardware/photonic/multiply", json=payload)
        return response.json()

