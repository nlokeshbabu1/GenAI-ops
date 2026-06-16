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

        if "message" in source:
            logs.append(source["message"])
        elif "log" in source:
            logs.append(source["log"])
        else:
            logs.append(str(source))

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

        events.append(str(source))

    return events






def main():
    print("\nFetching logs from OpenSearch...\n")
    logs = get_logs()

    
    print(f"Retrieved {len(logs)} log entries")

    print("Fetching Events...")
    events = get_events()


if __name__ == "__main__":
    main()
