# Operations Runbooks

This document contains operational procedures for managing the Arbor Energy Plan Agent in production.

## Table of Contents

1. [Incident Response](#incident-response)
2. [Service Health Checks](#service-health-checks)
3. [Common Issues and Solutions](#common-issues-and-solutions)
4. [Deployment Procedures](#deployment-procedures)
5. [Database Operations](#database-operations)
6. [Cache Operations](#cache-operations)
7. [Scaling Procedures](#scaling-procedures)
8. [Log Analysis](#log-analysis)
9. [Backup and Recovery](#backup-and-recovery)
10. [Security Procedures](#security-procedures)

---

## Incident Response

### Severity Levels

| Level | Description | Response Time | Example |
|-------|-------------|---------------|---------|
| P1 - Critical | Complete service outage | < 15 min | API completely down |
| P2 - High | Major feature broken | < 1 hour | Recommendations not generating |
| P3 - Medium | Degraded performance | < 4 hours | Slow response times |
| P4 - Low | Minor issues | < 24 hours | UI cosmetic bugs |

### Initial Response Checklist

```bash
# 1. Check service health
curl https://your-domain.com/api/v1/health

# 2. Check ECS service status
aws ecs describe-services \
    --cluster arbor-production-cluster \
    --services arbor-production-backend arbor-production-frontend

# 3. Check recent logs
aws logs tail /ecs/arbor-production/backend --since 30m

# 4. Check ALB health
aws elbv2 describe-target-health \
    --target-group-arn <target-group-arn>
```

---

## Service Health Checks

### Backend Health Check

```bash
# Basic health
curl -s https://your-domain.com/api/v1/health | jq

# Expected response:
# {
#   "status": "healthy",
#   "database": "connected",
#   "redis": "connected",
#   "timestamp": "2025-01-27T12:00:00Z"
# }
```

### Frontend Health Check

```bash
# Check frontend is serving
curl -s -o /dev/null -w "%{http_code}" https://your-domain.com

# Expected: 200
```

### Database Health Check

```bash
# Connect to RDS and check connections
psql -h <rds-endpoint> -U arbor_user -d arbor_production -c "
SELECT count(*) as active_connections
FROM pg_stat_activity
WHERE state = 'active';
"
```

### Redis Health Check

```bash
# Check Redis connectivity
redis-cli -h <elasticache-endpoint> ping

# Check memory usage
redis-cli -h <elasticache-endpoint> info memory
```

---

## Common Issues and Solutions

### Issue: API Returning 502/503 Errors

**Symptoms:** Users see error pages, health checks failing

**Diagnosis:**
```bash
# Check ECS task status
aws ecs list-tasks --cluster arbor-production-cluster --service-name arbor-production-backend

# Check task logs
aws logs get-log-events \
    --log-group-name /ecs/arbor-production/backend \
    --log-stream-name <stream-name> \
    --limit 50
```

**Resolution:**
1. Check if tasks are running
2. Review application logs for errors
3. Force new deployment if needed:
```bash
aws ecs update-service \
    --cluster arbor-production-cluster \
    --service arbor-production-backend \
    --force-new-deployment
```

### Issue: Slow Recommendation Generation

**Symptoms:** Recommendations take > 2 seconds

**Diagnosis:**
```bash
# Check CloudWatch metrics for latency
aws cloudwatch get-metric-statistics \
    --namespace AWS/ApplicationELB \
    --metric-name TargetResponseTime \
    --dimensions Name=LoadBalancer,Value=<alb-arn> \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Average

# Check database query performance
psql -c "SELECT query, calls, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

**Resolution:**
1. Check Redis cache hit rate
2. Review slow database queries
3. Consider scaling ECS tasks:
```bash
aws ecs update-service \
    --cluster arbor-production-cluster \
    --service arbor-production-backend \
    --desired-count 4
```

### Issue: Database Connection Pool Exhausted

**Symptoms:** "Connection pool exhausted" errors in logs

**Diagnosis:**
```bash
# Check active connections
psql -c "SELECT count(*) FROM pg_stat_activity;"
```

**Resolution:**
1. Restart affected ECS tasks
2. Review connection pool settings in config
3. Consider increasing RDS connections limit

### Issue: Redis Cache Not Working

**Symptoms:** High database load, slow responses

**Diagnosis:**
```bash
# Check Redis status
redis-cli -h <endpoint> info stats

# Check hit/miss ratio
redis-cli -h <endpoint> info stats | grep -E "keyspace_hits|keyspace_misses"
```

**Resolution:**
1. Warm up cache:
```bash
# Trigger cache warm-up via API
curl -X POST https://your-domain.com/api/v1/admin/cache/warm
```
2. Restart ElastiCache if needed (via AWS Console)

---

## Deployment Procedures

### Standard Deployment

```bash
# 1. Create a new release tag
git tag v1.2.3
git push origin v1.2.3

# 2. Monitor GitHub Actions deployment
# Check: https://github.com/your-org/arbor-energy-plan-agent/actions

# 3. Verify deployment
curl https://your-domain.com/api/v1/health

# 4. Monitor for errors in CloudWatch
aws logs tail /ecs/arbor-production/backend --since 10m --follow
```

### Rollback Procedure

```bash
# 1. Find previous task definition
aws ecs list-task-definitions --family-prefix arbor-production-backend --sort DESC

# 2. Update service to previous version
aws ecs update-service \
    --cluster arbor-production-cluster \
    --service arbor-production-backend \
    --task-definition arbor-production-backend:PREVIOUS_VERSION

# 3. Wait for deployment to complete
aws ecs wait services-stable \
    --cluster arbor-production-cluster \
    --services arbor-production-backend
```

### Blue-Green Deployment (Manual)

```bash
# 1. Create new task definition with updated image
aws ecs register-task-definition --cli-input-json file://new-task-def.json

# 2. Create new service with new task definition
aws ecs create-service \
    --cluster arbor-production-cluster \
    --service-name arbor-production-backend-green \
    --task-definition arbor-production-backend:NEW_VERSION \
    --desired-count 2

# 3. Test new service
curl https://green.your-domain.com/api/v1/health

# 4. Switch ALB target group
aws elbv2 modify-listener \
    --listener-arn <listener-arn> \
    --default-actions Type=forward,TargetGroupArn=<green-target-group-arn>

# 5. Delete old service after verification
aws ecs delete-service \
    --cluster arbor-production-cluster \
    --service arbor-production-backend-blue \
    --force
```

---

## Database Operations

### Running Migrations

```bash
# Run migrations via ECS task
aws ecs run-task \
    --cluster arbor-production-cluster \
    --task-definition arbor-production-migrations \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=DISABLED}" \
    --overrides '{"containerOverrides":[{"name":"backend","command":["alembic","upgrade","head"]}]}'

# Monitor migration task
aws ecs describe-tasks \
    --cluster arbor-production-cluster \
    --tasks <task-arn>
```

### Database Backup (Manual)

```bash
# Create manual snapshot
aws rds create-db-snapshot \
    --db-instance-identifier arbor-production-db \
    --db-snapshot-identifier arbor-production-manual-$(date +%Y%m%d-%H%M%S)

# List snapshots
aws rds describe-db-snapshots \
    --db-instance-identifier arbor-production-db
```

### Query Slow Queries

```bash
# Enable slow query log (if not enabled)
aws rds modify-db-parameter-group \
    --db-parameter-group-name arbor-production-params \
    --parameters "ParameterName=log_min_duration_statement,ParameterValue=1000,ApplyMethod=immediate"

# View slow queries in CloudWatch Logs
aws logs filter-log-events \
    --log-group-name /aws/rds/instance/arbor-production-db/postgresql \
    --filter-pattern "duration"
```

---

## Cache Operations

### Clear Cache

```bash
# Clear specific key pattern
redis-cli -h <endpoint> KEYS "plan:*" | xargs redis-cli -h <endpoint> DEL

# Clear all cache (use with caution)
redis-cli -h <endpoint> FLUSHALL
```

### Warm Up Cache

```bash
# Call the cache warm-up endpoint
curl -X POST https://your-domain.com/api/v1/admin/cache/warm \
    -H "Authorization: Bearer <admin-token>"

# Or run directly on backend
aws ecs execute-command \
    --cluster arbor-production-cluster \
    --task <task-id> \
    --container backend \
    --interactive \
    --command "python -c 'from app.services.cached_plan_service import warm_cache; warm_cache()'"
```

### Monitor Cache Performance

```bash
# Get cache statistics
redis-cli -h <endpoint> INFO stats

# Key metrics to watch:
# - keyspace_hits / keyspace_misses (hit ratio)
# - evicted_keys (memory pressure)
# - connected_clients
```

---

## Scaling Procedures

### Horizontal Scaling (ECS Tasks)

```bash
# Scale backend service
aws ecs update-service \
    --cluster arbor-production-cluster \
    --service arbor-production-backend \
    --desired-count 6

# Scale frontend service
aws ecs update-service \
    --cluster arbor-production-cluster \
    --service arbor-production-frontend \
    --desired-count 4
```

### Vertical Scaling (Task Resources)

1. Update task definition with new CPU/memory values
2. Register new task definition
3. Update service to use new task definition

```bash
# Example: Update CPU from 512 to 1024
aws ecs register-task-definition \
    --family arbor-production-backend \
    --cpu 1024 \
    --memory 2048 \
    # ... other parameters
```

### Database Scaling

```bash
# Scale up RDS instance (causes brief downtime)
aws rds modify-db-instance \
    --db-instance-identifier arbor-production-db \
    --db-instance-class db.t3.large \
    --apply-immediately
```

---

## Log Analysis

### Search Application Logs

```bash
# Search for errors
aws logs filter-log-events \
    --log-group-name /ecs/arbor-production/backend \
    --filter-pattern "ERROR"

# Search for specific user
aws logs filter-log-events \
    --log-group-name /ecs/arbor-production/backend \
    --filter-pattern "{ $.customer_id = \"abc123\" }"

# Search for slow requests
aws logs filter-log-events \
    --log-group-name /ecs/arbor-production/backend \
    --filter-pattern "{ $.duration > 2000 }"
```

### Export Logs for Analysis

```bash
# Export last 24 hours of logs
aws logs create-export-task \
    --log-group-name /ecs/arbor-production/backend \
    --from $(date -d '24 hours ago' +%s)000 \
    --to $(date +%s)000 \
    --destination arbor-log-exports \
    --destination-prefix logs/backend
```

---

## Backup and Recovery

### RDS Automated Backups

- Retention period: 7 days
- Backup window: 03:00-04:00 UTC
- Multi-AZ: Enabled in production

### Point-in-Time Recovery

```bash
# Restore to specific point in time
aws rds restore-db-instance-to-point-in-time \
    --source-db-instance-identifier arbor-production-db \
    --target-db-instance-identifier arbor-production-db-restored \
    --restore-time 2025-01-27T12:00:00Z

# After verification, promote restored instance
aws rds promote-read-replica \
    --db-instance-identifier arbor-production-db-restored
```

### Redis Backup

```bash
# Create manual backup
aws elasticache create-snapshot \
    --replication-group-id arbor-production-redis \
    --snapshot-name arbor-redis-manual-$(date +%Y%m%d)
```

---

## Security Procedures

### Rotate Database Credentials

```bash
# 1. Generate new password
NEW_PASSWORD=$(openssl rand -base64 32)

# 2. Update Secrets Manager
aws secretsmanager update-secret \
    --secret-id arbor/production/db \
    --secret-string "{\"username\":\"arbor_user\",\"password\":\"$NEW_PASSWORD\"}"

# 3. Update RDS password
aws rds modify-db-instance \
    --db-instance-identifier arbor-production-db \
    --master-user-password "$NEW_PASSWORD"

# 4. Restart ECS services to pick up new credentials
aws ecs update-service \
    --cluster arbor-production-cluster \
    --service arbor-production-backend \
    --force-new-deployment
```

### Review Security Groups

```bash
# List security group rules
aws ec2 describe-security-groups \
    --group-ids sg-xxx \
    --query 'SecurityGroups[*].{Name:GroupName,Rules:IpPermissions}'

# Audit for overly permissive rules
aws ec2 describe-security-groups \
    --query 'SecurityGroups[?IpPermissions[?IpRanges[?CidrIp==`0.0.0.0/0`]]]'
```

### SSL Certificate Renewal

Certificates managed by ACM auto-renew. Monitor via:

```bash
aws acm describe-certificate \
    --certificate-arn <cert-arn> \
    --query 'Certificate.{Status:Status,NotAfter:NotAfter}'
```

---

## Contact Information

- **On-Call Engineer:** Check PagerDuty rotation
- **Infrastructure Team:** infrastructure@arbor-energy.com
- **Security Team:** security@arbor-energy.com

---

*Last Updated: January 27, 2025*
