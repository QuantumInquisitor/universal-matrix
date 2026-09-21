> **SUPERSEDED / HISTORICAL MATERIAL**
>
> This file predates the canonical v0.4 reconstruction. It may contain obsolete
> claims involving Z_114, SO(13) physical spacetime, 64-bit physical geometry,
> exact physical-constant derivations, 3/6/9 physical laws, quantum/GR
> equivalence, or enterprise/hardware validation. For the current project use
> `README.md`, `ARCHITECTURE.md`, `docs/canonical_spec_v0.4.md`, and
> `docs/white_paper.md`.
>
> Historical content below is retained for provenance only.

﻿

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
