> **HISTORICAL / PROVENANCE DOCUMENT**
>
> This file records earlier repository architecture and terminology. It is intentionally preserved for development history and compatibility research.
>
> It is **not** current scientific or software authority. Historical claims involving Z_114, SO(13) physical spacetime, 64-bit physical geometry, fixed 3/6/9 laws, unverified physical constants, or production hardware should not be read as current project claims.
>
> Current authority: `README.md`, `white_paper.md`, `ARCHITECTURE.md`, `docs/DOCUMENTATION_STATUS.md`, and `docs/canonical_spec_v0.4.md`.
>
> Historical content below is retained without retroactively rewriting the development record.

# Repository Architecture Manifest

This manifest details the complete source code, hardware abstraction layer (HAL) drivers, core physics engines, test suites, and operational manifests across `universal-matrix`.

---

## Core Physics & Math Engines (`src/core/`, `src/`)

* **`src/calculator.py`**: Core $SO(13)$ Lie algebra math, register bitmasks, Givens rotation matrices, and high-dimensional tensor execution engine.
* **`src/core/native_matrix.py`**: Bare-metal hardware transformation pipeline routing high-dimensional tensor operations directly to CUDA VRAM buffers (`cuda:0`) with vectorized C-level NumPy matrix execution fallbacks.
* **`src/core/pino_engine.py`**: Physics-Informed Neural Operator (PINO) energy and momentum conservation core enforcing physical parameter boundaries and preventing non-physical matrix state divergence.
* **`src/core/quantum_hybrid.py`**: Variational Quantum Eigensolver (VQE) and QAOA execution pipeline modulating high-dimensional CUDA tensor transformations with live quantum expectation values.
* **`src/core/photonic_engine.py`**: Mach-Zehnder interferometer (MZI) array engine executing light-speed matrix transformations via optical phase modulation and photonic integrated circuit (PIC) simulation.
* **`src/core/digital_twin.py`**: Real-time spatial virtual twin state synchronization engine processing physical thermal, strain, and vibration sensor matrices to compute dynamic hardware degradation indices.
* **`src/russell_periodic_mapper.py`**: Walter Russell 10-octave periodic & tensor engine translating atomic elements ($Z=1 \rightarrow 118$) to gyroscopic plane tilts ($0^\circ \rightarrow 90^\circ$) and $432\text{ Hz}$ base harmonics.
* **`src/lattice_quantum_engine.py`**: Superposition, field phase interference, and measurement wave-function collapse simulation engine.
* **`src/geodesic_simulator.py`**: Discrete kinetic orbit propagation and relativistic orbital decay tracking environment.
* **`src/light_cone_simulator.py`**: Optical vector ray tracer mapping localized refraction indices and chromatic deflection vectors.
* **`src/m_theory_router.py`**: 11D hyper-spatial super-lattice engine down-projecting tensor coordinates into 3D Cartesian tracking meshes.
* **`src/physics_verifier.py`**: Symbolic field invariant engine calculating electromagnetic energy densities and Maxwell/Lorentz invariants.
* **`src/natural_units_converter.py`**: Invariant unit translation engine mapping SI metric parameters (Joules, Hertz, meters) to Planck units, electronvolts, and $SO(13)$ discrete lattice bounds.
* **`src/field_synthesizer.py`**: Advanced RF waveguide module translating discrete node bitmasks into continuous carrier phase frequency modulations.
* **`src/gpu_batch_accelerator.py`**: PyTorch CUDA matrix batch accelerator for high-density $SO(13)$ tensor transformations.

---

## Hardware Abstraction Layer & Dual-Mode Drivers (`src/hal/`, `src/drivers/`, `src/`)

* **`src/hal/orchestrator.py`**: Unified multi-driver orchestrator aggregating real-time diagnostics, active hardware modes, and health metrics across all dual-mode drivers.
* **`src/hal/base_driver.py`**: Hardware Abstraction Layer abstract base interface contract enforcing standard `initialize()` and `get_status()` signatures.
* **`src/hal/factory.py`**: Dynamic driver factory resolving physical hardware drivers vs. simulated mock fixtures at runtime.
* **`src/hal/safety_driver.py`**: Real-time physical parameter boundary monitoring and dynamic emergency-stop (E-STOP) enforcement driver.
* **`src/hal/anomaly_driver.py`**: Sensor-fusion feedback loop comparing requested spatial vectors against physical telemetry, calculating Euclidean spatial drift and outputting real-time compensation transforms.
* **`src/hal/mesh_orchestrator.py`**: Multi-node Kubernetes edge-mesh orchestrator dynamically distributing high-dimensional matrix workloads across edge hardware clusters with automated failover routing.
* **`src/hal/ros2_bridge.py`**: Real-time Data Distribution Service (DDS) messaging bridge translating high-dimensional spatial transform matrices into ROS 2 `geometry_msgs/Twist` velocity commands.
* **`src/hal/swarm_consensus.py`**: Decentralized Raft/BFT consensus protocol for robotic swarms, synchronizing 13D spatial trajectory vectors across multi-agent hardware nodes with quorum validation.
* **`src/gcode_compiler.py` & `src/drivers/cnc_driver.py`**: Parametric 5-axis G-code compiler and motion driver translating $SO(13)$ matrix tensors into continuous CNC toolpaths for toroidal coil winding.
* **`src/drivers/can_driver.py`**: Dual-mode SocketCAN hardware driver communicating via physical Linux SocketCAN sockets (`can0`) or simulated frame buffers.
* **`src/drivers/cuda_driver.py`**: Dual-mode NVIDIA GPU acceleration binding via PyTorch (`cuda:0`) with automatic vectorized CPU fallback.
* **`src/drivers/evm_driver.py`**: Dual-mode EVM RPC driver managing Web3 provider connections, block state inspection, and account state verification.
* **`src/drivers/k8s_driver.py`**: Dual-mode Kubernetes cloud driver managing in-cluster authentication, namespace scoping, and pod health inspection.
* **`src/drivers/qpu_driver.py`**: Dual-mode quantum processor driver integrating remote QPU backends (IBM Quantum / AWS Braket) with Qiskit statevector fallback.
* **`src/drivers/marx_driver.py`**: Dual-mode high-voltage pulsed power discharge driver interfacing with physical GPIO triggers (`RPi.GPIO`) and high-voltage DAQs.
* **`src/drivers/photonic_driver.py`**: Low-level optical matrix transformation driver interfacing with PCIe photonic hardware SDKs and synthetic array phase-shift fallbacks.
* **`src/drivers/fpga_driver.py`**: Bare-metal FPGA bitstream compiler and JTAG flashing interface calling vendor CLI toolchains (AMD Vivado / Intel Quartus).
* **`src/drivers/spacex_driver.py`**: Live aerospace constellation telemetry driver fetching real-time Starlink orbital positions, velocities, and spaceTrack metadata.
* **`src/biometric_ingestion.py`**: High-throughput physical biometrics ingestion engine transforming HRV, GSR, and EEG frequency ratios into dynamic $SO(13)$ phase coherence states.
* **`src/sdr_rf_synthesizer.py`**: Software Defined Radio (SDR) transmission engine driving electromagnetic carrier wave emissions across transceivers (HackRF, LimeSDR, USRP).
* **`src/closed_loop_bio_driver.py`**: Adaptive feedback engine linking real-time biometrics directly to SDR RF carrier wave frequencies and visualizer pulse rates.
* **`src/sensor_network_gateway.py`**: Hardware ingestion gateway receiving telemetry from magnetometers, Hall-effect arrays, and atomic clock drift monitors.
* **`src/swarm_controller.py`**: Multi-node hardware swarm controller synchronizing SDRs, CNCs, and sensor arrays across physical edge clusters with nanosecond timekeeping.
* **`src/drift_predictor.py`**: Anomaly detection engine calculating decoherence risk scores and time-to-collapse prediction windows.
* **`src/webxr_haptic_controller.py`**: WebXR 6-DoF spatial pose processor and bio-adaptive haptic pulse generator.
* **`src/plasma_shader_pipeline.py`**: Volumetric plasma GLSL shader uniform compiler translating $SO(13)$ plane angles into WebGL shader parameters.
* **`src/toroidal_winding_engine.py`**: 5-axis G-code generator for non-Euclidean coil winding and spatial field emitter fabrication.
* **`src/laser_interferometer.py`**: Sub-nanometer optical displacement monitoring parser detecting chassis micro-deformation and thermal expansion.
* **`src/hardware_tpm_enclave.py`**: Cryptographic platform configuration register (PCR) quote verifier interfacing with remote TPM 2.0 modules.
* **`src/hardware_kill_switch.py`**: Sub-millisecond safety kernel driver monitoring thermal runaway and over-current to issue immediate emergency hardware cuts (`M112`).
* **`src/fea_stress_twin.py`**: Multi-physics FEA simulation engine calculating Von Mises stress profiles and thermal dissipation along toolpaths.
* **`src/coil_geometry_optimizer.py`**: Evolutionary AI reinforcement learning engine optimizing coil winding radiuses, turn counts, and Q-factors.
* **`src/webgpu_spatial_visualizer.py`**: WebGPU WGSL compute pipeline compiler generating real-time 3D volumetric magnetic flux maps for AR passthrough.
* **`src/onnx_edge_drift_engine.py`**: Micro-quantized INT8 ONNX runtime engine forecasting quantum decoherence events on embedded edge microcontrollers.
* **`src/acoustic_resonance_synthesizer.py`**: Ultrasonic transducer array phase generator transforming $SO(13)$ phase angles into acoustic pressure fields and levitation nodes.
* **`src/quantum_entanglement_emulator.py`**: Cross-node phase synchronization engine calculating non-local coherence factors and Bell state fidelity.
* **`src/swarm_robotics_controller.py`**: 6-DoF inverse kinematics feedforward controller translating $SO(13)$ tensors into robotic arm joint trajectories.
* **`src/pemf_driver_interface.py`**: High-voltage pulsed electromagnetic field pulse train synthesizer and gate trigger controller.
* **`src/self_healing_engine.py`**: Multi-physics self-healing engine calculating coolant flow ramps and RF frequency offsets to counteract chassis stress.
* **`src/spatial_teleoperation_gateway.py`**: Low-latency WebXR spatial gateway processing bi-directional 3D pose vectors for live spatial teleoperation.
* **`src/can_bus_driver.py`**: Industrial CAN frame compiler generating binary payloads for PLC motor drives.
* **`src/marx_gate_array.py`**: Nanosecond-precision gate timing controller for erected high-voltage Marx generator capacitor discharges.
* **`src/grid_power_manager.py`**: Micro-grid power supervisor monitoring bus voltages, current draw, and battery thermal thresholds.
* **`src/qiskit_quantum_bridge.py`**: Transpiles $SO(13)$ matrix rotation angles into OpenQASM 2.0 quantum gate circuits.
* **`src/rl_field_optimizer.py`**: Policy-gradient feedback driver (PPO/DDPG) continuously adjusting 6-DoF robotic arm poses in real time.
* **`src/fpga_bitstream_compiler.py`**: Transpiles WGSL spatial compute shader routines directly into synthesizable Verilog HDL hardware logic blocks for FPGAs.
* **`src/raft_consensus_engine.py`**: High-availability quorum driver executing RAFT state transitions and leader elections.
* **`src/photonic_tensor_coprocessor.py`**: Coherent optical waveguide simulator modeling Mach-Zehnder interferometer arrays for zero-latency matrix operations.
* **`src/zero_trust_attestation.py`**: Zero-trust platform configuration register quote verifier interfacing with remote TPM 2.0 hardware modules.
* **`src/autonomous_agent.py`**: Autonomous AI agent orchestrator evaluating cluster health telemetry to trigger RL field optimizations or FPGA re-synthesis.
* **`src/hardware_mocks.py`**: Simulated Hardware-in-the-Loop (HIL) test fixtures providing virtual CAN interfaces and Marx Gate discharge mocks.

---

## Business, Governance & Utility Services (`src/`, `sdk/`, `scripts/`)

* **`src/auth_gateway.py`**: Enterprise JWT authentication manager, hardware session key validator, and multi-tenant access controller.
* **`src/license_usage_metering.py`**: Usage tracking ledger recording machine-hours and $SO(13)$ compute operations with SHA-256 audit proofs for commercial billing.
* **`src/evm_contract_bridge.py`**: Enterprise licensing proof engine compiling compute unit telemetry into EVM-compatible smart contract payloads.
* **`src/dao_governance.py`**: EVM-compatible governance voting engine verifying minimum WEI staking power thresholds and generating SHA-256 state hashes.
* **`src/cluster_sync.py`**: Multi-region cluster sync manager and real-time node quorum health evaluator.
* **`src/metrics.py` & `src/metrics_exporter.py`**: Promethean metrics managers exposing native system counters and gauges (`/metrics`).
* **`src/topology_calibrator.py`**: Real-time field phase drift analysis and resonance frequency auto-tuning engine.
* **`src/config.py`**: Environment configuration manager parsing driver modes, CAN channels, CUDA device IDs, and Web3 RPC nodes.
* **`src/data_logger.py`**: Telemetry logger tracking environmental flux streams and internal clock-drift variance.
* **`sdk/python/universal_matrix_sdk.py`**: Native Python SDK client with built-in HTTP request abstractions.
* **`sdk/js/universalMatrixSdk.js`**: Node.js and browser-compatible JavaScript SDK client leveraging the Fetch API.
* **`scripts/deploy_licensing.js`**: Asynchronous Hardhat deployment automation for compiling and publishing smart contracts to EVM networks.

---

## API Layer & WebXR Viewports (`src/`, `public/`)

* **`src/api.py`**: FastAPI/ASGI REST server providing high-concurrency matrix endpoints, JWT authentication, RBAC authorization, and live SSE streaming (`/api/v1/telemetry/stream`).
* **`src/spatial_viewport.py`**: WebGPU compute shader host and WebXR spatial coordinate translation engine rendering real-time 3D spatial field projections at 90+ FPS.
* **`public/index.html`**: Interactive Three.js WebXR 3D spatial interface and client-side WebGPU WGSL compute shader pipeline.
* **`src/static/dashboard.html`**: Live Chart.js single-page telemetry dashboard tracking clock-drift variance and step counts in real time.
* **`src/run_field_simulation.py`**: Pipeline launcher coordinating API background processes, quantum/optical verification, and visualizer loops.

---

## Verified Real-World Industrial Remedies (`tests/`)

* **`tests/test_pino_guardrail_remedy.py`**: Verifies Physics-Informed Neural Operator conservation bounds and emergency stop hardware interlock tripping on ML anomaly detection.
* **`tests/test_mesh_failover_remedy.py`**: Verifies Kubernetes edge cluster workload dispatching and zero-downtime failover re-routing during node dropouts.
* **`tests/test_thermal_stability_remedy.py`**: Verifies laser interferometry spatial drift calculation and closed-loop $SO(13)$ offset matrix compensations for sub-nanometer CNC stability.
* **`tests/test_quantum_hitl_remedy.py`**: Verifies hybrid VQE quantum expectation value integration driving CUDA tensor transformations.

---

## Infrastructure, Deployment & Observability

* **`Dockerfile`**: Production container build specification for Python 3.11 with system-level rendering libraries and Uvicorn entry point.
* **`docker-compose.yml`**: Multi-container composition spec launching Matrix Engine, Redis, Prometheus, and Grafana containers.
* **`charts/universal-matrix/`**: Helm v3 chart directory containing parameterizable Kubernetes deployment templates (`deployment.yaml`, `service.yaml`, `values.yaml`).
* **`.github/workflows/ci-cd.yml`**: GitHub Actions CI/CD automation executing unit tests, Docker container builds, and Helm chart linting on push.
* **`prometheus.yml`**: Time-series metrics scraping configuration targeting the matrix microservice `/metrics` route.
* **`grafana/provisioning/`**: Automated Grafana provisioning scripts for Prometheus datasources and telemetry dashboards.
* **`nginx/`**: NGINX gateway configuration handling SSL/TLS termination, HTTP-to-HTTPS redirects, WSS upgrades, and SSE proxying.
* **`hardhat.config.js`**: Hardhat environment configuration defining EVM network RPC endpoints and compiler settings.
* **`scripts/verify_env.py`**: Pre-flight environment auditor checking dependencies, port 8000 availability, and hardware drivers.
* **`scripts/load_test.py`**: Synthetic SSE stream load generator for benchmarking API throughput under concurrent subscriber traffic.