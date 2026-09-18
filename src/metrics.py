from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Define System & Hardware Metrics
COMPUTE_EXECUTIONS = Counter("matrix_compute_executions_total", "Total matrix execution calls", ["phase"])
CLUSTER_NODE_LATENCY = Gauge("matrix_cluster_node_latency_ms", "Heartbeat latency per node in ms", ["node_id"])
RL_OPTIMIZER_REWARD = Gauge("matrix_rl_reward_score", "Latest RL field optimizer reward score")
FPGA_SYNTHESIS_TIME = Histogram("matrix_fpga_synthesis_duration_seconds", "Histogram of FPGA synthesis compilation time")

class MetricsManager:
    @staticmethod
    def record_compute(phase_name: str):
        COMPUTE_EXECUTIONS.labels(phase=phase_name).inc()

    @staticmethod
    def set_node_latency(node_id: str, latency_ms: float):
        CLUSTER_NODE_LATENCY.labels(node_id=node_id).set(latency_ms)

    @staticmethod
    def set_rl_reward(reward: float):
        RL_OPTIMIZER_REWARD.set(reward)

    @staticmethod
    def export_metrics() -> tuple:
        return generate_latest(), CONTENT_TYPE_LATEST

