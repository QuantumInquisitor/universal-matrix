# Universal Matrix — Operational Usage & API Guide

This document provides operational procedures for deploying the `universal-matrix` spatial compute engine, configuring runtime CLI parameters, interacting with API endpoints, executing containerized microservices, and validating industrial remedy test suites.

---

## 1. Local Installation & Environment Setup

### Prerequisites
* Python 3.11 or higher
* NVIDIA CUDA Toolkit (optional, required for GPU VRAM acceleration)
* Docker & Docker Compose (optional, for containerized deployments)

### Environment Initialization

```bash
# Clone the repository and navigate to the project root
git clone [https://github.com/QuantumInquisitor/universal-matrix.git](https://github.com/QuantumInquisitor/universal-matrix.git)
cd universal-matrix

# Create and activate a Python virtual environment
python -m venv venv

# Activate environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate environment (Linux / macOS)
# source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt

###Pre-Flight System Audit
Verify package dependencies, port 8000 availability, and active hardware acceleration drivers prior to execution:

```bash
python scripts/verify_env.py

## 2. CLI Execution Parameters & Runtime Flags

The primary pipeline entry point (`src/run_field_simulation.py`) supports dynamic CLI flags for targeted debugging, headless benchmarks, and isolated multi-layer torus rendering:

| Flag | Type | Description | Example Usage |
| :--- | :--- | :--- | :--- |
| `--layer` | Integer (`0–14`) | Focuses spatial visualization on a specific Torus layer (`0` renders all 14 layers simultaneously). | `python src/run_field_simulation.py --layer 5` |
| `--headless` | Flag | Executes simulation math and APIs without launching the interactive OpenXR/WebGL GUI. | `python src/run_field_simulation.py --headless` |
| `--no-api` | Flag | Launches field calculations and visualization loops while disabling the ASGI REST server. | `python src/run_field_simulation.py --no-api` |
| `--mode` | String | Sets engine execution profile (`harmony`, `cascade`, `simulation`). | `python src/calculator.py --mode harmony` |

## 3. Server Execution & Telemetry Streaming

### Unified Field Pipeline (ASGI REST API + Math Engine + WebXR Visualizer)
python src/run_field_simulation.py

* Interactive Viewport: http://localhost:8000
* Prometheus Metrics: http://localhost:8000/metrics

### Asynchronous REST Server Standalone
python -m uvicorn src.api:app --reload --host 127.0.0.1 --port 8000

## 4. API Operations & Endpoint Examples

### OAuth2 Bearer Token Issuance
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/token" -Method Post -Body @{
    username = "operator"
    password = "matrix_secure_password_2026"
}
$token =$response.access_token

### Real-Time Telemetry Stream (Server-Sent Events)
curl -N http://127.0.0.1:8000/api/v1/telemetry/stream

### Direct Bare-Metal Matrix Transformation
$payload = @{ matrix = @(@(1.0, 0.0), @(0.0, 1.0)) } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/matrix/transform/native" `
  -Method Post `
  -ContentType "application/json" `
  -Body $payload

  ## 5. Industrial Remedy Test Suite Execution

Run the verified test suites to validate closed-loop hardware remedies across core industrial domains:

### Complete Remedy Suite
$env:PYTHONPATH="."
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*_remedy.py"

### Individual Remedy Validations
* Robot PINO Safety Guardrails & E-STOP:
  .\venv\Scripts\python.exe -m unittest discover -s tests -p "test_pino_guardrail_remedy.py"

* Edge Cluster Mesh Failover:
  .\venv\Scripts\python.exe -m unittest discover -s tests -p "test_mesh_failover_remedy.py"

* Sub-Nanometer CNC Thermal Stability:
  .\venv\Scripts\python.exe -m unittest discover -s tests -p "test_thermal_stability_remedy.py"

* Quantum-Classical HITL Optimization:
  .\venv\Scripts\python.exe -m unittest discover -s tests -p "test_quantum_hitl_remedy.py"

  ## 6. Enterprise Container & Cloud Deployment

### Multi-Container Stack (Docker Compose)
Deploy the core microservice alongside Redis state persistence, Prometheus metrics scraping, and Grafana visualization:

# Build and launch microservice containers in detached mode
docker compose up --build -d

# Check operational status of running containers
docker compose ps

Access Endpoints & Default Credentials:
* Matrix API / Dashboard: http://localhost:8000
* Prometheus Metrics:    http://localhost:9090
* Grafana Dashboards:    http://localhost:3000 (admin / admin)

### Kubernetes Deployment (Helm v3)
# Render Kubernetes manifests locally for dry-run inspection
helm template matrix-release ./charts/universal-matrix

# Deploy to active Kubernetes cluster
helm install matrix-release ./charts/universal-matrix

# Inspect active pod health and ingress routes
kubectl get pods -l app=universal-matrix
