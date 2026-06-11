from fastapi import FastAPI, HTTPException
from aiops_openserach import get_logs, get_events
from prometheus import get_metrics
from AiOps import build_prompt, analyze
# from gpt4all import GPT4All
import boto3
import json
from botocore.exceptions import ClientError

app = FastAPI(
    title="AIOps RCA Engine",
    description="Kubernetes AIOps Root Cause Analysis API",
    version="1.0.0"
)

#main page
@app.get("/")
def read_root():
    return {
        "message": "Welcome to the AIOps RCA Engine API. Use /analyze to get insights on Kubernetes issues."
    }

    
#health check
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "AIOps RCA Engine is healthy"
    }


# ==================================
# Get Logs
# ==================================
@app.get("/logs")
def fetch_logs():
    try:
        logs = get_logs()
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================================
# Get Events
# ==================================
@app.get("/events")
def fetch_events():
    try:
        events = get_events()
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================================
# Get Metrics
# ==================================

@app.get("/metrics")
def metrics():

    return get_metrics()


# ==================================
# Analyze Endpoint
# ==================================
@app.get("/analyze")
def analyze_endpoint():

    try:
        logs = get_logs()
        events = get_events()
        metrics = get_metrics()

        prompt = build_prompt(logs, events, metrics)
        analysis = analyze(prompt)

        return {"analysis": analysis}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 


