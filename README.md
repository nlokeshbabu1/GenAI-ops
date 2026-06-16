# GenAI-ops

A Generative AI-powered Kubernetes and AWS Operations platform that performs automated Root Cause Analysis (RCA) on production incidents using telemetry data from logs, metrics, and events.

## Overview

GenAI-ops integrates with:
- **OpenSearch** - Application logs and Kubernetes events collection
- **Prometheus** - Infrastructure and application metrics
- **AWS Bedrock** - Generative AI analysis engine (Mistral model)
- **AWS SNS** - Incident notification delivery

The system automatically collects telemetry from your Kubernetes/EKS environment and uses AI to perform comprehensive incident analysis, root cause identification, and remediation recommendations.

## Features

- **Intelligent Log Analysis** - Parses application and system logs for errors and anomalies
- **Kubernetes Event Correlation** - Analyzes pod, deployment, and node events
- **Metrics Analysis** - Evaluates CPU, memory, network, and request latency metrics
- **AI-Powered RCA** - Uses AWS Bedrock to generate production-grade incident analysis
- **Automated Recommendations** - Provides immediate, short-term, and long-term remediation steps
- **Notification Integration** - Sends analysis results via AWS SNS

## Prerequisites

- Python 3.8 or higher
- AWS Account with access to:
  - AWS Bedrock (Mistral model enabled)
  - AWS SNS
  - IAM permissions for both services
- OpenSearch cluster (AWS managed or self-hosted)
- Prometheus instance with Kubernetes metrics
- Kubernetes cluster (EKS recommended)

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/nlokeshbabu1/GenAI-ops.git
cd GenAI-ops
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root directory and add the following configuration:

```bash
# AWS Configuration
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# OpenSearch Configuration
OPENSEARCH_HOST=my-domain.ap-south-1.es.amazonaws.com
OPENSEARCH_PORT=443
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=your_password_here
OPENSEARCH_INDEX=logs
OPENSEARCH_EVENTS_INDEX=kubernetes-events

# Prometheus Configuration
PROM_URL=http://your-prometheus-server.com:9090
PROMETHEUS_HOST=your-prometheus-server.com
PROMETHEUS_PORT=9090

# AWS SNS Configuration
SNS_TOPIC_ARN=arn:aws:sns:ap-south-1:account-id:your-topic-name
SNS_REGION=ap-south-1

# Bedrock Configuration
BEDROCK_MODEL_ID=mistral.ministral-3-8b-instruct
BEDROCK_REGION=ap-south-1
```

## Configuration Guide

### A. AWS Configuration

```bash
AWS_REGION=ap-south-1  # Your AWS region
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
```

**To get AWS credentials:**
- Go to AWS Console → IAM → Users → Your User → Security Credentials
- Create Access Key and copy the values

### B. OpenSearch Configuration

```bash
OPENSEARCH_HOST=my-domain.ap-south-1.es.amazonaws.com
OPENSEARCH_PORT=443
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=your_password_here
OPENSEARCH_INDEX=logs
OPENSEARCH_EVENTS_INDEX=kubernetes-events
```

**To find your OpenSearch domain:**
- AWS Console → OpenSearch Service → Domains → Select your domain
- Copy the Endpoint and use it as OPENSEARCH_HOST

### C. Prometheus Configuration

```bash
PROM_URL=http://your-prometheus-server.com:9090
PROMETHEUS_HOST=your-prometheus-server.com
PROMETHEUS_PORT=9090
```

**To verify Prometheus is running:**
```bash
curl http://your-prometheus-url:9090/api/v1/query?query=up
```

### D. AWS SNS Configuration

```bash
SNS_TOPIC_ARN=arn:aws:sns:ap-south-1:account-id:your-topic-name
SNS_REGION=ap-south-1
```

**To create an SNS topic:**
- AWS Console → SNS → Topics → Create Topic
- Copy the Topic ARN

### E. Bedrock Configuration

```bash
BEDROCK_MODEL_ID=mistral.ministral-3-8b-instruct
#BEDROCK_REGION=ap-south-1
```

**To enable Bedrock:**
- AWS Console → Bedrock → Model Access
- Enable access to Mistral model

## Usage

### Running the Analysis

```bash
python AiOps.py
```

This will:
1. Fetch logs from OpenSearch
2. Retrieve Kubernetes events
3. Collect Prometheus metrics
4. Generate an AI-powered incident analysis
5. Send the RCA report via SNS

### Running the Web Application

```bash
python app.py
```

Then open `http://localhost:5000` in your browser.

## Project Structure

```
GenAI-ops/
├── AiOps.py                 # Main orchestration script
├── aiops_openserach.py      # OpenSearch data fetcher
├── prometheus.py            # Prometheus metrics collector
├── app.py                   # Web application
├── query.py                 # Query utilities
├── build_index.py           # Index building utilities
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (do not commit)
├── .gitignore              # Git ignore file
├── LICENSE                 # Apache License 2.0
└── README.md               # This file
```

## Dependencies

All required Python packages are listed in `requirements.txt`:

- **boto3** - AWS SDK for Python
- **botocore** - Low-level AWS API
- **opensearch-py** - OpenSearch Python client
- **prometheus-client** - Prometheus metrics library
- **requests** - HTTP library
- **python-dotenv** - Environment variable management
- **flask** - Web framework

## Analysis Output

The AI analysis includes:

- **Executive Summary** - High-level incident overview
- **Detected Issues** - Identified problems in logs, metrics, and events
- **Root Cause** - Primary cause and contributing factors
- **Evidence** - Supporting data and correlations
- **Impact Assessment** - User, service, and infrastructure impact
- **Recommended Fix** - Immediate, short-term, and long-term remediation steps
- **Validation Commands** - kubectl, Prometheus, and OpenSearch commands
- **Prevention** - Monitoring and alerting improvements
- **Severity Level** - Critical, High, Medium, or Low
- **Confidence Score** - Analysis confidence percentage

## Troubleshooting

### OpenSearch Connection Error

```
Error fetching logs: Connection error
```

**Solutions:**
- Check OPENSEARCH_HOST and OPENSEARCH_PORT in `.env`
- Verify OpenSearch cluster is running
- Check security group allows connections
- Verify username and password

### Prometheus Connection Error

```
Error connecting to Prometheus
```

**Solutions:**
- Verify PROM_URL is correct in `.env`
- Check Prometheus service is running: `curl http://prometheus-url:9090/-/healthy`
- Check firewall rules allow connections

### AWS Bedrock Error

```
Bedrock Invocation Error
```

**Solutions:**
- Verify AWS credentials in `.env`
- Check Bedrock model access is enabled in AWS Console
- Ensure IAM user has bedrock:InvokeModel permission
- Verify AWS_REGION is correct

### SNS Topic Error

```
Error publishing to SNS
```

**Solutions:**
- Verify SNS_TOPIC_ARN is correct
- Check SNS topic exists in AWS Console
- Verify IAM user has sns:Publish permission

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Support

For issues and questions, please open an issue on GitHub.
