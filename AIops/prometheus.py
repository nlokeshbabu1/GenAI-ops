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
# Metric utilities
# ==================================

def compute_percentage_change(current, baseline):
    if current is None or baseline is None or baseline == 0:
        return None
    return ((current - baseline) / baseline) * 100


def build_metric_anomaly(name, current, baseline, change):
    if change is None:
        return None

    return (
        f"{name} spike detected: current={current:.3f}, baseline={baseline:.3f}, "
        f"increase={change:.1f}%"
    )


# ==================================
# Get Metrics
# ==================================

def get_metrics():

    metrics = {}

    # CPU current and baseline
    cpu_current = query_prometheus(
        "sum(rate(container_cpu_usage_seconds_total[1m]))"
    )
    cpu_baseline = query_prometheus(
        "avg_over_time(sum(rate(container_cpu_usage_seconds_total[1m]))[15m])"
    )

    # Memory current and baseline
    memory_current = query_prometheus(
        "sum(container_memory_working_set_bytes)"
    )
    memory_baseline = query_prometheus(
        "avg_over_time(sum(container_memory_working_set_bytes)[15m])"
    )

    # Latency current and baseline
    latency_current = query_prometheus(
        "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))"
    )
    latency_baseline = query_prometheus(
        "avg_over_time(histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))[15m])"
    )

    metrics["cpu_current"] = extract_metric_value(cpu_current)
    metrics["cpu_baseline"] = extract_metric_value(cpu_baseline)
    metrics["memory_current"] = extract_metric_value(memory_current)
    metrics["memory_baseline"] = extract_metric_value(memory_baseline)
    metrics["latency_current"] = extract_metric_value(latency_current)
    metrics["latency_baseline"] = extract_metric_value(latency_baseline)

    anomalies = []

    cpu_change = compute_percentage_change(metrics["cpu_current"], metrics["cpu_baseline"])
    memory_change = compute_percentage_change(metrics["memory_current"], metrics["memory_baseline"])
    latency_change = compute_percentage_change(metrics["latency_current"], metrics["latency_baseline"])

    metrics["cpu_change_pct"] = cpu_change
    metrics["memory_change_pct"] = memory_change
    metrics["latency_change_pct"] = latency_change

    # thresholds for sudden increases
    if cpu_change is not None and cpu_change > 20:
        anomalies.append(build_metric_anomaly("CPU usage", metrics["cpu_current"], metrics["cpu_baseline"], cpu_change))
    if memory_change is not None and memory_change > 20:
        anomalies.append(build_metric_anomaly("Memory usage", metrics["memory_current"], metrics["memory_baseline"], memory_change))
    if latency_change is not None and latency_change > 20:
        anomalies.append(build_metric_anomaly("95th percentile latency", metrics["latency_current"], metrics["latency_baseline"], latency_change))

    metrics["anomalies"] = [a for a in anomalies if a is not None]

    return metrics


def main():
    print("Fetching Metrics...")
    metrics = get_metrics()
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
