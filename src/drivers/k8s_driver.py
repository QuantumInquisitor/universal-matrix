from src.hal.base_driver import BaseHardwareDriver
from src.config import config

class KubernetesDriver(BaseHardwareDriver):
    def __init__(self):
        self.mode = "REAL" if config.USE_REAL_HARDWARE else "MOCK"
        self.client = None
        self.initialize()

    def initialize(self) -> bool:
        if self.mode == "REAL":
            try:
                from kubernetes import client, config as k8s_config
                try:
                    k8s_config.load_incluster_config()
                except k8s_config.ConfigException:
                    k8s_config.load_kube_config()
                self.client = client.CoreV1Api()
                return True
            except Exception:
                self.mode = "MOCK_FALLBACK"
                return False
        else:
            return True

    def get_cluster_pod_status(self, namespace: str = "default") -> dict:
        if self.mode == "REAL" and self.client:
            try:
                pods = self.client.list_namespaced_pod(namespace)
                pod_list = [pod.metadata.name for pod in pods.items]
                return {
                    "status": "K8S_REAL_CLUSTER_QUERY_SUCCESS",
                    "namespace": namespace,
                    "pod_count": len(pod_list),
                    "pods": pod_list
                }
            except Exception as e:
                return {"status": "K8S_QUERY_ERROR", "error": str(e)}
        else:
            return {
                "status": "K8S_MOCK_QUERY_SUCCESS",
                "mode": self.mode,
                "namespace": namespace,
                "pod_count": 3,
                "pods": ["universal-matrix-api-7d9f-1", "universal-matrix-api-7d9f-2", "universal-matrix-worker-0"]
            }

    def get_status(self) -> dict:
        return {
            "driver": "KubernetesDriver",
            "active_mode": self.mode,
            "target_namespace": "default"
        }

