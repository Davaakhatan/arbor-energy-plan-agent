# Deployment Guide

This guide covers deploying the Arbor Energy Plan Recommendation Agent to production.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Environment Setup](#environment-setup)
4. [Docker Deployment](#docker-deployment)
5. [AWS Deployment](#aws-deployment)
6. [SSL Configuration](#ssl-configuration)
7. [Database Setup](#database-setup)
8. [Monitoring](#monitoring)
9. [Scaling](#scaling)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Docker 24+ and Docker Compose v2
- Domain name with DNS configured
- SSL certificates (or use Let's Encrypt)
- AWS account (for cloud deployment)

---

## Quick Start

### 1. Clone and Configure

```bash
git clone https://github.com/Davaakhatan/arbor-energy-plan-agent.git
cd arbor-energy-plan-agent

# Copy and configure environment
cp .env.production.example .env.production
nano .env.production  # Edit with your values
```

### 2. Generate Secrets

```bash
# Generate secure passwords
openssl rand -hex 32  # For SECRET_KEY
openssl rand -hex 16  # For POSTGRES_PASSWORD
openssl rand -hex 16  # For REDIS_PASSWORD
```

### 3. Deploy

```bash
# Build and start services
docker compose -f docker-compose.prod.yml --env-file .env.production up -d

# Run database migrations
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Seed initial data
docker compose -f docker-compose.prod.yml exec backend python -m app.scripts.seed_data
```

---

## Environment Setup

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_USER` | Database username | `arbor_prod` |
| `POSTGRES_PASSWORD` | Database password | Secure random string |
| `POSTGRES_DB` | Database name | `arbor_energy_prod` |
| `REDIS_PASSWORD` | Redis password | Secure random string |
| `SECRET_KEY` | JWT signing key | `openssl rand -hex 32` |
| `CORS_ORIGINS` | Allowed origins | `["https://your-domain.com"]` |
| `NEXT_PUBLIC_API_URL` | API URL for frontend | `https://your-domain.com` |

### Security Best Practices

1. Never commit `.env.production` to version control
2. Use secrets management (AWS Secrets Manager, Vault)
3. Rotate passwords regularly
4. Use strong passwords (32+ characters)

---

## Docker Deployment

### Build Production Images

```bash
# Build all images
docker compose -f docker-compose.prod.yml build

# Build specific service
docker compose -f docker-compose.prod.yml build backend
```

### Start Services

```bash
# Start all services
docker compose -f docker-compose.prod.yml --env-file .env.production up -d

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Check service health
docker compose -f docker-compose.prod.yml ps
```

### Update Deployment

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# Run migrations if needed
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

---

## AWS Deployment

### Option 1: ECS with Fargate

```bash
# Install AWS CLI and configure
aws configure

# Create ECR repositories
aws ecr create-repository --repository-name arbor-backend
aws ecr create-repository --repository-name arbor-frontend

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push images
docker tag arbor-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/arbor-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/arbor-backend:latest
```

### Option 2: EC2 with Docker

1. Launch EC2 instance (t3.medium recommended)
2. Install Docker and Docker Compose
3. Clone repository and configure
4. Run docker-compose.prod.yml

### Recommended AWS Services

| Service | Purpose |
|---------|---------|
| ECS/Fargate | Container orchestration |
| RDS PostgreSQL | Managed database |
| ElastiCache Redis | Managed caching |
| ALB | Load balancing |
| Route 53 | DNS management |
| ACM | SSL certificates |
| CloudWatch | Monitoring and logs |

---

## SSL Configuration

### Option 1: Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt-get install certbot

# Generate certificates
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates to nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem

# Set up auto-renewal
sudo crontab -e
# Add: 0 0 1 * * certbot renew --quiet
```

### Option 2: AWS ACM (for ALB)

1. Request certificate in ACM
2. Validate domain ownership
3. Attach certificate to ALB

---

## Database Setup

### Initial Setup

```bash
# Run migrations
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Seed data
docker compose -f docker-compose.prod.yml exec backend python -m app.scripts.seed_data
```

### Backups

```bash
# Create backup
docker compose -f docker-compose.prod.yml exec postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup_$(date +%Y%m%d).sql

# Restore backup
docker compose -f docker-compose.prod.yml exec -T postgres psql -U $POSTGRES_USER $POSTGRES_DB < backup.sql
```

### AWS RDS Setup

1. Create RDS PostgreSQL instance
2. Enable Multi-AZ for high availability
3. Configure security groups
4. Update connection strings in environment

---

## Monitoring

### Health Checks

```bash
# Check backend health
curl https://your-domain.com/api/v1/health

# Check nginx health
curl http://your-domain.com/health
```

### Logs

```bash
# View all logs
docker compose -f docker-compose.prod.yml logs -f

# View specific service
docker compose -f docker-compose.prod.yml logs -f backend

# View nginx access logs
docker compose -f docker-compose.prod.yml exec nginx tail -f /var/log/nginx/access.log
```

### CloudWatch Integration

Add to your environment:

```env
AWS_CLOUDWATCH_LOG_GROUP=/arbor/production
AWS_CLOUDWATCH_LOG_STREAM=backend
```

### Recommended Monitoring Stack

- **Application**: Sentry for error tracking
- **Infrastructure**: CloudWatch or Datadog
- **Uptime**: Pingdom or UptimeRobot
- **APM**: New Relic or Datadog APM

---

## Scaling

### Horizontal Scaling

Update `docker-compose.prod.yml`:

```yaml
backend:
  deploy:
    replicas: 4  # Increase replicas
```

### Vertical Scaling

Adjust resource limits:

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 1G
```

### Database Scaling

- Enable read replicas for RDS
- Increase instance size as needed
- Consider connection pooling (PgBouncer)

### Cache Scaling

- Use ElastiCache cluster mode
- Increase Redis instance size
- Consider cache sharding

---

## Troubleshooting

### Common Issues

#### Services Not Starting

```bash
# Check logs
docker compose -f docker-compose.prod.yml logs backend

# Check resource usage
docker stats

# Verify environment variables
docker compose -f docker-compose.prod.yml config
```

#### Database Connection Issues

```bash
# Test database connectivity
docker compose -f docker-compose.prod.yml exec backend python -c "
from app.core.database import engine
print(engine.url)
"

# Check PostgreSQL logs
docker compose -f docker-compose.prod.yml logs postgres
```

#### SSL/HTTPS Issues

```bash
# Verify certificates
openssl s_client -connect your-domain.com:443

# Check nginx configuration
docker compose -f docker-compose.prod.yml exec nginx nginx -t
```

#### Performance Issues

1. Check response times in nginx logs
2. Monitor Redis cache hit rates
3. Review slow query logs in PostgreSQL
4. Check container resource usage with `docker stats`

### Recovery Procedures

#### Rollback Deployment

```bash
# Tag current deployment
docker tag arbor-backend:latest arbor-backend:rollback

# Deploy previous version
git checkout <previous-commit>
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

#### Database Recovery

```bash
# Stop application
docker compose -f docker-compose.prod.yml stop backend

# Restore from backup
docker compose -f docker-compose.prod.yml exec -T postgres psql -U $POSTGRES_USER $POSTGRES_DB < backup.sql

# Restart application
docker compose -f docker-compose.prod.yml start backend
```

---

## Security Checklist

- [ ] All passwords are strong (32+ characters)
- [ ] Environment files are not in version control
- [ ] SSL/TLS is enabled and forced
- [ ] Security headers are configured in nginx
- [ ] Rate limiting is enabled
- [ ] Database is not publicly accessible
- [ ] Redis requires authentication
- [ ] Regular backups are configured
- [ ] Monitoring and alerting are set up

---

## Contact

For deployment issues:
- Email: devops@arbor-energy.com
- On-call: Check internal runbook

---

*Last Updated: January 27, 2025*
