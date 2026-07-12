import re
import requests
import urllib3
import os
from dotenv import load_dotenv
#from mistralai.client import Mistral  # Reverted back to mistralai

# Disable SSL warnings (lab only)
urllib3.disable_warnings()

#Load environment variables
load_dotenv(override=True)

# OpenSearch
OPENSEARCH_URL = os.getenv("OPENSEARCH_URL","")
INDEX = os.getenv("INDEX","cwl-*")
EVENT_INDEX = os.getenv("EVENT_INDEX","k8s-cluster-events")

# OpenSearch Admin Credentials
OPENSEARCH_USER = os.getenv("OPENSEARCH_USER","admin")
OPENSEARCH_PASSWORD = os.getenv("OPENSEARCH_PASSWORD","Admin@1234")

# ==================================
# Filtering helpers
# ==================================

def extract_log_text(source):
    if isinstance(source, dict):
        if "message" in source:
            return source["message"]
        if "log" in source:
            return source["log"]
        if "error" in source:
            return str(source["error"])
    return str(source)


def is_relevant_log(text):
    if not text:
        return False

    text_lower = text.lower()
    if re.search(r"\b(http|https)\b.*\b\d{3}\b", text_lower):
        return True
    if re.search(r"\b(4|5)\d{2}\b", text_lower):
        return True
    return bool(re.search(r"\b(error|failed|failure|exception|timeout|unable|unavailable|crash|panic|denied|refused)\b", text_lower))


def extract_event_text(source):
    if isinstance(source, dict):
        for key in ("message", "reason", "log", "status", "type"):
            if key in source and source[key]:
                return str(source[key])
    return str(source)


def is_relevant_event(text):
    if not text:
        return False

    text_lower = text.lower()
    return bool(re.search(r"\b(crashloopbackoff|imagepullbackoff|pending|failed|error|fail|backoff|oomkilled|oom|unschedulable|not ready|evicted|deadlineexceeded)\b", text_lower))

# ==================================
# OpenSearch Logs
# ==================================


def get_logs():
    query = {
        "size": 50,
        "sort": [
            {
                "@timestamp": {
                    "order": "desc"
                }
            }
        ],
        "query": {
            "match_all": {}
        }
    }

    response = requests.get(
        f"{OPENSEARCH_URL}/{INDEX}/_search",
        auth=(OPENSEARCH_USER, OPENSEARCH_PASSWORD),
        json=query,
        verify=False
    )

    if response.status_code != 200:
        print("OpenSearch Error")
        print(response.text)
        return []

    data = response.json()
    logs = []

    for hit in data["hits"]["hits"]:
        source = hit["_source"]
        text = extract_log_text(source)

        if is_relevant_log(text):
            logs.append(text)

    if not logs:
        return ["No relevant error logs found."]

    return logs


# ==================================
# OpenSearch Events
# ==================================

def get_events():

    query = {
        "size": 50,
        "sort": [
            {
                "@timestamp": {
                    "order": "desc"
                }
            }
        ],
        "query": {
            "match_all": {}
        }
    }

    response = requests.get(
        f"{OPENSEARCH_URL}/{EVENT_INDEX}/_search",
        auth=(OPENSEARCH_USER, OPENSEARCH_PASSWORD),
        json=query,
        verify=False
    )

    data = response.json()

    events = []

    for hit in data["hits"]["hits"]:
        source = hit["_source"]
        text = extract_event_text(source)

        if is_relevant_event(text):
            events.append(text)

    if not events:
        return ["No relevant Kubernetes events found."]

    return events






def main():
    print("\nFetching logs from OpenSearch...\n")
    logs = get_logs()

    
    print(f"Retrieved {len(logs)} log entries")

    print("Fetching Events...")
    events = get_events()


if __name__ == "__main__":
    main()
