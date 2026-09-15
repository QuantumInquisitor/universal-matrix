from prometheus_client import Counter, Gauge, Histogram

# Field Coherence & Matrix Telemetry Metrics
FIELD_COHERENCE_GAUGE = Gauge("toroidal_field_coherence_index", "Current mean phase coherence index (0.0 to 1.0)")
ACTIVE_NODES_GAUGE = Gauge("toroidal_active_nodes_total", "Total active nodes across micro and macro lattices")
WS_CONNECTIONS_GAUGE = Gauge("websocket_active_connections_total", "Active WebSocket telemetry stream connections")
MATRIX_CALC_LATENCY = Histogram("so13_tensor_calculation_seconds", "Latency of SO(13) matrix transformations")
RESONANCE_EVAL_COUNTER = Counter("resonance_evaluations_total", "Total toroidal field resonance evaluations performed")
