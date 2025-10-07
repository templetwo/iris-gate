# IRIS Platform Deployment Guide

This guide covers deployment options for the IRIS Research Platform, from local development to production cloud deployments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Self-Hosted Deployment](#self-hosted-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Configuration](#configuration)
6. [Monitoring](#monitoring)
7. [Backup & Recovery](#backup--recovery)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- Docker and Docker Compose
- Kubernetes cluster (for production)
- Terraform (for cloud infrastructure)
- kubectl (Kubernetes CLI)
- Helm (package manager for Kubernetes)

### API Keys
The platform requires API keys for AI services:
- Anthropic Claude API key
- OpenAI API key
- Google AI (Gemini) API key
- xAI (Grok) API key (optional)
- DeepSeek API key (optional)

## Local Development

### Quick Start with Docker Compose

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd iris-gate/platform
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start the platform**
   ```bash
   docker-compose up -d
   ```

4. **Access the platform**
   - Web UI: http://localhost:3000
   - API Gateway: http://localhost:8000
   - Database: localhost:5432
   - Redis: localhost:6379
   - MinIO Console: http://localhost:9001

### Development Environment Details

The development environment includes:
- **PostgreSQL**: User data and session metadata
- **Redis**: Caching and session management
- **MinIO**: Object storage for research data
- **OpenSearch**: Full-text search (production only)
- **Kong**: API gateway with rate limiting
- **Monitoring**: Prometheus and Grafana

## Self-Hosted Deployment

### Hardware Requirements

**Minimum (Development/Testing)**
- 4 CPU cores
- 8 GB RAM
- 50 GB storage
- Ubuntu 20.04 LTS or similar

**Recommended (Production)**
- 8+ CPU cores
- 32+ GB RAM
- 500+ GB SSD storage
- Load balancer
- Backup storage

### Installation Steps

1. **Prepare the server**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh

   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Configure the platform**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd iris-gate/platform

   # Copy production compose file
   cp docker-compose.prod.yml docker-compose.yml

   # Set up environment
   cp .env.production .env
   # Edit .env with your configuration
   ```

3. **Deploy with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Set up SSL/TLS**
   ```bash
   # Using Let's Encrypt with Certbot
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

### Docker Swarm Deployment

For high availability, use Docker Swarm:

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-stack.yml iris-platform
```

## Cloud Deployment

### AWS Deployment with Terraform

1. **Prerequisites**
   ```bash
   # Install Terraform
   curl -fsSL https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip -o terraform.zip
   unzip terraform.zip
   sudo mv terraform /usr/local/bin/

   # Install AWS CLI
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install

   # Configure AWS credentials
   aws configure
   ```

2. **Deploy infrastructure**
   ```bash
   cd infrastructure/terraform

   # Initialize Terraform
   terraform init

   # Plan deployment
   terraform plan -var="environment=prod" -var="domain_name=iris.yourcompany.com"

   # Apply infrastructure
   terraform apply
   ```

3. **Configure kubectl**
   ```bash
   aws eks update-kubeconfig --region us-west-2 --name iris-platform
   ```

4. **Deploy application**
   ```bash
   # Create namespace
   kubectl apply -f kubernetes/namespace.yaml

   # Apply configurations
   kubectl apply -f kubernetes/configmap.yaml

   # Deploy services
   kubectl apply -f kubernetes/postgres.yaml
   kubectl apply -f kubernetes/redis.yaml
   kubectl apply -f kubernetes/research-engine.yaml
   kubectl apply -f kubernetes/user-service.yaml
   kubectl apply -f kubernetes/web-ui.yaml

   # Deploy ingress
   kubectl apply -f kubernetes/ingress.yaml
   ```

### Multi-Cloud Options

The platform can be deployed on:
- **AWS**: EKS + RDS + ElastiCache + S3
- **Google Cloud**: GKE + Cloud SQL + Memorystore + Cloud Storage
- **Azure**: AKS + PostgreSQL + Redis Cache + Blob Storage
- **DigitalOcean**: Kubernetes + Managed Database + Spaces

## Configuration

### Environment Variables

**Database Configuration**
```bash
DATABASE_URL=postgresql://user:password@host:5432/iris_platform
REDIS_URL=redis://host:6379
```

**AI Service Keys**
```bash
ANTHROPIC_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_gemini_api_key
XAI_API_KEY=your_grok_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
```

**Security Configuration**
```bash
JWT_SECRET=your_super_secret_jwt_key
JWT_REFRESH_SECRET=your_refresh_secret_key
ENCRYPTION_KEY=your_encryption_key_for_data
```

### Scaling Configuration

**Horizontal Pod Autoscaling**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: research-engine-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: research-engine
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Monitoring

### Metrics and Observability

The platform includes comprehensive monitoring:

**Prometheus Metrics**
- Application performance metrics
- Resource utilization
- AI API usage and costs
- User session analytics

**Grafana Dashboards**
- System overview
- Research session analytics
- AI model performance
- Cost analysis

**Logging**
- Centralized logging with ELK stack
- Structured JSON logs
- Error tracking and alerting

### Alerting Rules

```yaml
groups:
- name: iris-platform
  rules:
  - alert: HighCPUUsage
    expr: cpu_usage > 80
    for: 5m
    annotations:
      summary: "High CPU usage detected"

  - alert: AIAPIErrors
    expr: rate(ai_api_errors[5m]) > 0.1
    for: 2m
    annotations:
      summary: "High AI API error rate"
```

## Backup & Recovery

### Database Backups

**Automated PostgreSQL Backups**
```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME | gzip > "$BACKUP_DIR/iris_backup_$DATE.sql.gz"

# Retention: keep 30 days
find $BACKUP_DIR -name "iris_backup_*.sql.gz" -mtime +30 -delete
```

**Object Storage Backups**
```bash
# Sync MinIO data to cloud storage
aws s3 sync /data/minio/ s3://iris-backups/minio/ --delete
```

### Disaster Recovery

1. **Database Recovery**
   ```bash
   # Restore from backup
   gunzip -c iris_backup_20231201_120000.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_NAME
   ```

2. **Application Recovery**
   ```bash
   # Redeploy from git
   git pull origin main
   docker-compose down
   docker-compose up -d
   ```

## Troubleshooting

### Common Issues

**Database Connection Issues**
```bash
# Check database connectivity
kubectl exec -it postgres-pod -- psql -U iris_user -d iris_platform -c "SELECT 1;"

# Check logs
kubectl logs -f deployment/research-engine
```

**AI API Rate Limits**
```bash
# Check API usage
kubectl logs -f deployment/research-engine | grep "rate_limit"

# Scale down concurrent requests
kubectl patch deployment research-engine -p '{"spec":{"replicas":2}}'
```

**Memory Issues**
```bash
# Check memory usage
kubectl top nodes
kubectl top pods

# Increase memory limits
kubectl patch deployment research-engine -p '{"spec":{"template":{"spec":{"containers":[{"name":"research-engine","resources":{"limits":{"memory":"4Gi"}}}]}}}}'
```

### Health Checks

**Application Health**
```bash
# Check all services
curl http://localhost:8000/health

# Check individual services
curl http://localhost:3001/health  # User service
curl http://localhost:3002/health  # Research engine
curl http://localhost:3003/health  # Data platform
```

**Database Health**
```bash
# PostgreSQL
pg_isready -h localhost -p 5432

# Redis
redis-cli ping
```

### Performance Optimization

**Database Optimization**
```sql
-- Create indexes for better performance
CREATE INDEX CONCURRENTLY idx_sessions_user_org ON research_sessions (user_id, organization_id);
CREATE INDEX CONCURRENTLY idx_turns_session_chamber ON session_turns (session_id, chamber);
```

**Application Optimization**
```yaml
# Kubernetes resource limits
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

For additional support, check the [FAQ](faq.md) or open an issue in the repository.