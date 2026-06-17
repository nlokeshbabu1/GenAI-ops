import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

#Prometheus
PROM_URL = os.getenv("PROM_URL","http://localhost:9090")

# ==================================
# Prometheus Metrics
# ==================================

def query_prometheus(query):
    try:

        response = requests.get(
            f"{PROM_URL}/api/v1/query",
            params={"query": query}
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        print("Prometheus Query Error:", e)
        return None


# ==================================
# Extract Metric Value
# ==================================

def extract_metric_value(result):
    if not result or "data" not in result or "result" not in result["data"]:
        return None

    try:
        return float(result["data"]["result"][0]["value"][1])
    except (IndexError, KeyError, ValueError) as e:
        print("Metric Extraction Error:", e)
        return None


# ==================================
# Get Metrics
# ==================================

def get_metrics():

    metrics = {}

    # CPU
    cpu_usage_cores = query_prometheus(
        "sum(rate(container_cpu_usage_seconds_total[5m]))"
    )

    # Memory
    memory_usage_bytes = query_prometheus(
        "sum(container_memory_working_set_bytes)"
    )

    # Restart Count
    container_restarts = query_prometheus(
        "sum(kube_pod_container_status_restarts_total)"
    )

    #latency
    latency_seconds = query_prometheus(
        "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))"
    )

    metrics["cpu_usage_cores"] = extract_metric_value(cpu_usage_cores)
    metrics["memory_usage_bytes"] = extract_metric_value(memory_usage_bytes)
    metrics["container_restarts"] = extract_metric_value(container_restarts)
    metrics["latency_seconds"] = extract_metric_value(latency_seconds)

    return metrics


def main():
    print("Fetching Metrics...")
    metrics = get_metrics()
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
