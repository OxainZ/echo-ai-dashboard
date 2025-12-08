# Deployment Guide - Echo AI Trading Intelligence Platform

This guide covers deployment options for the Echo AI Dashboard, from local development to production cloud deployments.

## 📋 Table of Contents

- [Local Deployment](#local-deployment)
- [Docker Deployment](#docker-deployment)
- [Streamlit Cloud](#streamlit-cloud-deployment)
- [AWS Deployment](#aws-deployment)
- [Google Cloud Platform](#google-cloud-platform-deployment)
- [Azure Deployment](#azure-deployment)
- [Environment Configuration](#environment-configuration)
- [Security Considerations](#security-considerations)
- [Monitoring and Maintenance](#monitoring-and-maintenance)

## 🏠 Local Deployment

### Development Setup

Perfect for local development and testing.

```bash
# Clone repository
git clone https://github.com/OxainZ/echo-ai-dashboard.git
cd echo-ai-dashboard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run application
streamlit run UI.py
```

**Access**: http://localhost:8501

### Production-like Local Setup

```bash
# Use production settings
export ENVIRONMENT=production
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run with nohup for background execution
nohup streamlit run UI.py > streamlit.log 2>&1 &
```

## 🐳 Docker Deployment

### Quick Start with Docker

```bash
# Build image
docker build -t echo-ai-dashboard:latest .

# Run container
docker run -d \
  --name echo-dashboard \
  -p 8501:8501 \
  -v $(pwd)/echo:/app/echo \
  -v $(pwd)/.streamlit:/app/.streamlit \
  --env-file .env \
  echo-ai-dashboard:latest
```

### Docker Compose (Recommended)

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Custom Docker Compose Configuration

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  echo-dashboard:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: echo-ai-prod
    ports:
      - "80:8501"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    env_file:
      - .env.production
    volumes:
      - ./echo:/app/echo:ro
      - ./models:/app/models
      - ./logs:/app/logs
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - echo-network
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G

networks:
  echo-network:
    driver: bridge
```

Run with:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## ☁️ Streamlit Cloud Deployment

### Prerequisites

- GitHub repository
- Streamlit Cloud account (free tier available)

### Deployment Steps

1. **Push code to GitHub**
   ```bash
   git push origin main
   ```

2. **Connect to Streamlit Cloud**
   - Go to https://share.streamlit.io/
   - Click "New app"
   - Select repository: `OxainZ/echo-ai-dashboard`
   - Set main file: `UI.py`
   - Click "Deploy"

3. **Configure Secrets**

   In Streamlit Cloud dashboard, add secrets:

   ```toml
   # .streamlit/secrets.toml (in Streamlit Cloud)
   password_hash = "your_password_hash_here"
   
   [api_keys]
   alpha_vantage = "your_key"
   finnhub = "your_key"
   ```

4. **Configure Advanced Settings**
   - Python version: 3.11
   - Custom domain (optional)
   - Resource allocation

### Streamlit Cloud Limitations

- 1GB RAM on free tier
- Limited compute resources
- Public deployment only on free tier
- Consider Streamlit Enterprise for production

## 🌐 AWS Deployment

### Option 1: EC2 with Docker

1. **Launch EC2 Instance**
   ```bash
   # Recommended: t3.medium or larger
   # OS: Ubuntu 22.04 LTS
   ```

2. **Install Docker**
   ```bash
   # SSH into instance
   ssh -i your-key.pem ubuntu@your-ec2-ip

   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker ubuntu

   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **Deploy Application**
   ```bash
   # Clone repository
   git clone https://github.com/OxainZ/echo-ai-dashboard.git
   cd echo-ai-dashboard

   # Configure environment
   cp .env.example .env
   nano .env  # Edit with your settings

   # Start application
   docker-compose up -d
   ```

4. **Configure Security Group**
   - Allow inbound TCP 8501
   - Allow SSH (22) from your IP only
   - Consider using ALB for HTTPS

### Option 2: ECS (Elastic Container Service)

1. **Create ECR Repository**
   ```bash
   aws ecr create-repository --repository-name echo-ai-dashboard
   ```

2. **Build and Push Image**
   ```bash
   # Authenticate Docker to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account-id.dkr.ecr.us-east-1.amazonaws.com

   # Build and tag image
   docker build -t echo-ai-dashboard .
   docker tag echo-ai-dashboard:latest your-account-id.dkr.ecr.us-east-1.amazonaws.com/echo-ai-dashboard:latest

   # Push to ECR
   docker push your-account-id.dkr.ecr.us-east-1.amazonaws.com/echo-ai-dashboard:latest
   ```

3. **Create ECS Task Definition**
   ```json
   {
     "family": "echo-ai-dashboard",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "1024",
     "memory": "2048",
     "containerDefinitions": [
       {
         "name": "echo-dashboard",
         "image": "your-account-id.dkr.ecr.us-east-1.amazonaws.com/echo-ai-dashboard:latest",
         "portMappings": [
           {
             "containerPort": 8501,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {"name": "ENVIRONMENT", "value": "production"}
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/echo-ai-dashboard",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

4. **Create ECS Service**
   - Use Application Load Balancer
   - Enable auto-scaling
   - Configure health checks

### Option 3: Elastic Beanstalk

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize Application**
   ```bash
   eb init -p docker echo-ai-dashboard --region us-east-1
   ```

3. **Create Environment**
   ```bash
   eb create echo-ai-prod \
     --instance-type t3.medium \
     --envvars ENVIRONMENT=production
   ```

4. **Deploy**
   ```bash
   eb deploy
   ```

## 🔵 Google Cloud Platform Deployment

### Option 1: Cloud Run (Serverless)

1. **Build and Push to Container Registry**
   ```bash
   # Authenticate
   gcloud auth configure-docker

   # Build image
   docker build -t gcr.io/your-project-id/echo-ai-dashboard .

   # Push to GCR
   docker push gcr.io/your-project-id/echo-ai-dashboard
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy echo-ai-dashboard \
     --image gcr.io/your-project-id/echo-ai-dashboard \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8501 \
     --memory 2Gi \
     --cpu 2 \
     --set-env-vars ENVIRONMENT=production
   ```

### Option 2: Compute Engine

Similar to AWS EC2 deployment:

```bash
# Create instance
gcloud compute instances create echo-ai-instance \
  --machine-type=n1-standard-2 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB

# SSH and deploy
gcloud compute ssh echo-ai-instance
# Follow Docker deployment steps
```

### Option 3: GKE (Kubernetes)

For large-scale deployments:

```bash
# Create cluster
gcloud container clusters create echo-ai-cluster \
  --num-nodes=3 \
  --machine-type=n1-standard-2

# Deploy application
kubectl apply -f kubernetes/
```

## 🔷 Azure Deployment

### Option 1: Container Instances

```bash
# Create resource group
az group create --name echo-ai-rg --location eastus

# Create container
az container create \
  --resource-group echo-ai-rg \
  --name echo-ai-dashboard \
  --image your-registry/echo-ai-dashboard:latest \
  --dns-name-label echo-ai \
  --ports 8501 \
  --cpu 2 \
  --memory 4 \
  --environment-variables ENVIRONMENT=production
```

### Option 2: App Service

```bash
# Create App Service plan
az appservice plan create \
  --name echo-ai-plan \
  --resource-group echo-ai-rg \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --name echo-ai-dashboard \
  --resource-group echo-ai-rg \
  --plan echo-ai-plan \
  --deployment-container-image-name your-registry/echo-ai-dashboard:latest
```

## ⚙️ Environment Configuration

### Production Environment Variables

```bash
# Application
ENVIRONMENT=production
APP_NAME=Echo AI Trading Dashboard
LOG_LEVEL=INFO

# Security
PASSWORD_HASH=your_hashed_password
SECRET_KEY=your_secret_key_here

# Database (if applicable)
DATABASE_URL=postgresql://user:pass@host:5432/db

# API Keys
ALPHA_VANTAGE_API_KEY=your_key
FINNHUB_API_KEY=your_key

# Feature Flags
ENABLE_AI_PREDICTIONS=true
ENABLE_BACKTESTING=true
ENABLE_CACHING=true

# Performance
CACHE_EXPIRY_SECONDS=300
MAX_WORKERS=4
```

### Secrets Management

#### AWS Secrets Manager

```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Usage
secrets = get_secret('echo-ai/production')
password_hash = secrets['password_hash']
```

#### GCP Secret Manager

```python
from google.cloud import secretmanager

def get_secret(project_id, secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode('UTF-8')
```

## 🔒 Security Considerations

### SSL/TLS Configuration

Use a reverse proxy (nginx) for HTTPS:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Firewall Rules

```bash
# AWS Security Group
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxx \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# GCP Firewall
gcloud compute firewall-rules create allow-https \
  --allow tcp:443 \
  --source-ranges 0.0.0.0/0
```

### Rate Limiting

Use nginx or cloud provider rate limiting:

```nginx
limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s;

server {
    location / {
        limit_req zone=mylimit burst=20;
        proxy_pass http://localhost:8501;
    }
}
```

## 📊 Monitoring and Maintenance

### Health Checks

```python
# Add to Streamlit app
import streamlit as st
import requests

def health_check():
    """Endpoint for health monitoring"""
    return {"status": "healthy", "version": "1.0.0"}

# Monitor with:
curl http://your-domain.com/_stcore/health
```

### Logging

Configure centralized logging:

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/echo-ai.log',
    maxBytes=10000000,
    backupCount=5
)
logging.basicConfig(
    handlers=[handler],
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Monitoring Tools

- **AWS CloudWatch**: Built-in monitoring
- **GCP Cloud Monitoring**: Integrated metrics
- **Datadog**: Multi-cloud monitoring
- **Prometheus + Grafana**: Self-hosted monitoring

### Backup Strategy

```bash
# Backup configuration and models
tar -czf echo-ai-backup-$(date +%Y%m%d).tar.gz \
  echo/config.yaml \
  models/ \
  .env

# Upload to S3
aws s3 cp echo-ai-backup-*.tar.gz s3://your-backup-bucket/
```

### Update Strategy

```bash
# Zero-downtime deployment
docker-compose pull
docker-compose up -d --no-deps --build echo-dashboard

# Or with blue-green deployment
docker-compose -f docker-compose.blue.yml up -d
# Test
docker-compose -f docker-compose.green.yml down
```

## 🚦 Production Checklist

- [ ] Environment variables configured
- [ ] Secrets properly managed
- [ ] SSL/TLS certificate installed
- [ ] Firewall rules configured
- [ ] Health checks enabled
- [ ] Logging configured
- [ ] Monitoring set up
- [ ] Backup strategy implemented
- [ ] Auto-scaling configured (if applicable)
- [ ] Rate limiting enabled
- [ ] Load balancer configured (if applicable)
- [ ] DNS configured
- [ ] Documentation updated

## 📞 Support

For deployment issues:
- Check logs: `docker-compose logs`
- Review health checks
- Verify environment variables
- Consult cloud provider documentation

---

**Last Updated**: December 2024  
**Maintainer**: Echo AI Team
