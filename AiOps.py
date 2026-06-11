from aiops_openserach import get_logs, get_events
from prometheus import get_metrics
import boto3
import json
# from gpt4all import GPT4All
from botocore.exceptions import ClientError

# # Initialize GPT4All model
# model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf", n_ctx=2048)

# #sns

sns = boto3.client('sns')

# #sns arn

TOPIC_ARN = TOPIC_ARN = 'arn:aws:sns:ap-south-1:961014542927:test'

# Initialize Bedrock client
model = boto3.client(
    "bedrock-runtime",
    region_name="ap-south-1"
)

# Fetch data
logs = get_logs()
events = get_events()
metrics = get_metrics()


# ==================================
# Build AI Context
# ==================================

def build_prompt(logs, events, metrics):

    return f"""
You are a Principal Kubernetes SRE, Platform Engineer, and AI Ops Expert.

Analyze the telemetry from an Amazon EKS environment.

=================================================
APPLICATION LOGS
=================================================

{logs}

=================================================
KUBERNETES EVENTS
=================================================

{events}

=================================================
PROMETHEUS METRICS
=================================================

{metrics}

=================================================

Perform a complete production-grade incident analysis.

Analyze and correlate:

1. Application Health
   - Check application errors
   - Check exceptions
   - Check timeout messages
   - Check database connectivity issues
   - Check dependency failures

2. HTTP Traffic Analysis
   - Identify HTTP status codes
   - Analyze 4xx errors
   - Analyze 5xx errors
   - Identify 502, 503, 504 patterns
   - Determine impact to users

3. Kubernetes Workload Health
   - Pod Status
   - Deployment Status
   - Replica Availability
   - Restart Counts
   - CrashLoopBackOff
   - OOMKilled
   - FailedScheduling
   - ImagePullBackOff

4. Node Health
   - Node Ready status
   - CPU pressure
   - Memory pressure
   - Disk pressure
   - Network issues

5. Performance Analysis
   - CPU utilization
   - Memory utilization
   - Network latency
   - Request latency
   - Error rate

6. Event Correlation
   - Correlate Kubernetes events with logs
   - Correlate metrics with events
   - Correlate failures with user impact

7. Root Cause Analysis
   - Identify primary root cause
   - Identify contributing factors
   - Provide confidence level

8. Impact Assessment
   - User impact
   - Service impact
   - Infrastructure impact

9. Remediation Steps
   - Immediate actions
   - Short-term fixes
   - Long-term fixes

10. Validation Commands
   - Provide exact kubectl commands
   - Provide Prometheus queries if required
   - Provide OpenSearch queries if required

11. Prevention Recommendations
   - Monitoring improvements
   - Alerting improvements
   - Resource recommendations
   - Scaling recommendations

Output Format:

Executive Summary:
...

Detected Issues:
...

Root Cause:
...

Evidence:
...

Impact:
...

Recommended Fix:
...

Validation Commands:
...

Prevention:
...

Severity:
Critical / High / Medium / Low

Confidence Score:
0-100%
"""

# def analyze(prompt):

#     with model.chat_session():

#         result = model.generate(
#             prompt,
#             max_tokens=1024,
#             temp=0
#         )

#     return result

def analyze(prompt):
    #step-1 model id
    model_id = "mistral.ministral-3-8b-instruct"

    #invoke the model
    try:
        response = model.invoke_model(
            modelId=model_id,
            body=json.dumps({
                "messages": [{"role": "user", "content": prompt}],
                # "prompt": prompt,
                "max_tokens": 2048,
                "temperature": 0.0, #example 0.0 means deterministic output - best for analysis tasks
                "top_p": 0.9 # example 0.9 means consider top 90% probable tokens - good balance of relevance and diversity
            }),
            contentType="application/json",
            accept="application/json"
        )

        response_body = json.loads(response["body"].read()) #example response body {"outputs": [{"text": "Generated analysis here", "tokens": 200, "time": 1.5}]}
        return response_body["choices"][0]["message"]["content"] #we will the only output 

    except ClientError as e:
        print("Bedrock Invocation Error:", e)
        return "Error during analysis"


def main():
    print("\nFetching logs from OpenSearch...\n")
    logs = get_logs()

    
    print(f"Retrieved {len(logs)} log entries")

    print("Fetching Events from Opensearch...")
    events = get_events()

    print("Fetching Metrics from Prometheus...")
    metrics = get_metrics()


    print("Building AI Context...")
    prompt = build_prompt(logs, events, metrics)
    print(f"Length of AI Prompt: {len(prompt)} characters")

    print("Running AI Analysis...")
    result = analyze(prompt)
    print(f"Length of AI Result: {len(result)} characters")

    print("\n========== AI OPS RCA ==========\n")
    print(result)

    print("\nSending RCA to SNS Topic...\n")
    sns.publish(
        TopicArn=TOPIC_ARN,
        Message=result,
        Subject="RCA for the Kubernetes Application"
    )
    

if __name__ == "__main__":
    main()