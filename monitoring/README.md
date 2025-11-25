# Monitoring & Alerting

This directory contains monitoring and alerting configurations for the Arbor Energy Plan Agent.

## Contents

| File | Description |
|------|-------------|
| `cloudwatch-config.json` | CloudWatch Agent configuration for log and metric collection |
| `alerts.tf` | Terraform configuration for CloudWatch alarms |
| `dashboard.json` | CloudWatch Dashboard definition |

## Application Endpoints

The application exposes these monitoring endpoints:

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/health` | Basic health check |
| `GET /api/v1/health/detailed` | Detailed health with DB and cache status |
| `GET /api/v1/metrics` | Application metrics (uptime, counts, response times) |
| `GET /api/v1/metrics/ready` | Kubernetes-style readiness probe |
| `GET /api/v1/metrics/live` | Kubernetes-style liveness probe |

## Setup Instructions

### 1. CloudWatch Agent

Install and configure the CloudWatch Agent on EC2 or ECS:

```bash
# Download agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure with our config
sudo cp monitoring/cloudwatch-config.json /opt/aws/amazon-cloudwatch-agent/etc/config.json

# Start agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json \
    -s
```

### 2. CloudWatch Alarms

Deploy alarms using Terraform:

```bash
cd monitoring

# Initialize Terraform
terraform init

# Plan changes
terraform plan -var="sns_topic_arn=arn:aws:sns:us-east-1:123456789:alerts"

# Apply
terraform apply -var="sns_topic_arn=arn:aws:sns:us-east-1:123456789:alerts"
```

### 3. CloudWatch Dashboard

Import the dashboard via AWS Console or CLI:

```bash
aws cloudwatch put-dashboard \
    --dashboard-name "Arbor-Energy-Agent" \
    --dashboard-body file://monitoring/dashboard.json
```

## Alarms

| Alarm | Threshold | Description |
|-------|-----------|-------------|
| API Response Time | > 2s | Response time exceeds target |
| High Error Rate | > 10 5xx/5min | High server error rate |
| High CPU | > 80% | ECS CPU utilization |
| High Memory | > 80% | ECS memory utilization |
| DB Connections | > 80% | RDS connection count |
| Redis Memory | > 75% | Cache memory usage |
| Health Failures | < 1 healthy | No healthy targets |
| Request Spike | > 10k/min | Unusual traffic spike |

## Alert Destinations

Configure SNS to send alerts to:

1. **Email**: ops-team@arbor-energy.com
2. **Slack**: #arbor-alerts channel
3. **PagerDuty**: For critical alarms (P1)

### SNS Topic Setup

```bash
# Create topic
aws sns create-topic --name arbor-alerts

# Subscribe email
aws sns subscribe \
    --topic-arn arn:aws:sns:us-east-1:123456789:arbor-alerts \
    --protocol email \
    --notification-endpoint ops@arbor-energy.com
```

## Log Queries

Useful CloudWatch Logs Insights queries:

### Error Analysis
```
fields @timestamp, @message
| filter @message like /error|ERROR/
| sort @timestamp desc
| limit 100
```

### Slow Requests
```
fields @timestamp, path, response_time_ms
| filter response_time_ms > 1000
| sort response_time_ms desc
| limit 50
```

### Request Volume by Endpoint
```
fields @timestamp, path
| stats count() as requests by path
| sort requests desc
```

### Error Rate
```
fields @timestamp
| filter status >= 500
| stats count() as errors by bin(5m)
```

## Runbook

### High Response Time

1. Check `/api/v1/metrics` for database and cache response times
2. Review slow query logs in RDS
3. Check Redis cache hit rate
4. Scale ECS service if CPU/memory constrained

### High Error Rate

1. Check application logs for stack traces
2. Verify database connectivity
3. Check for recent deployments
4. Review rate limiting metrics

### No Healthy Targets

1. Check ECS task status
2. Review container logs
3. Verify health check endpoint responding
4. Check security groups and network ACLs

---

*Last Updated: January 27, 2025*
