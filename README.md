

## Phase 15: Real-Time Physical Biometrics Ingestion & Telemetry

* **Biometric Ingestion Gateway (src/biometric_ingestion.py):** Ingests real-time HRV RR-intervals, Galvanic Skin Response (GSR), and EEG power spectrums ($\delta, \theta, \alpha, \beta, \gamma$).
* **REST & WebSocket Ingestion Routes:** Ingest live biometric telemetry at /api/v1/biometrics/ingest and /ws/biometrics/ingest.

### Biometric Ingestion CLI Example (PowerShell)

`powershell
curl -X POST "[http://127.0.0.1:8000/api/v1/biometrics/ingest](http://127.0.0.1:8000/api/v1/biometrics/ingest)" 
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" 
  -H "Content-Type: application/json" 
  -d '{
    "hrv_rr_interval_ms": 850.0,
    "gsr_microsiemens": 4.2,
    "eeg_alpha_power": 15.5,
    "eeg_theta_power": 22.1,
    "eeg_beta_power": 8.3
  }'
