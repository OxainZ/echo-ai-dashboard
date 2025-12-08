# Deployment Guide

This guide covers various deployment options for Echo AI Dashboard, from local development to cloud production environments.

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Streamlit Cloud](#streamlit-cloud)
4. [AWS Deployment](#aws-deployment)
5. [Google Cloud Platform](#google-cloud-platform)
6. [Azure Deployment](#azure-deployment)
7. [Environment Variables](#environment-variables)
8. [Monitoring and Maintenance](#monitoring-and-maintenance)

---

## Local Development

### Prerequisites
- Python 3.11+
- pip or conda
- Git

### Setup Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/OxainZ/echo-ai-dashboard.git
   cd echo-ai-dashboard
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run Application**
   ```bash
   streamlit run UI.py
   ```

6. **Access Dashboard**
   - Open browser to http://localhost:8501
   - Default password: `echo2024`

---

## Docker Deployment

### Quick Start

```bash
# Build and run
./deploy.sh

# Or manually:
docker-compose up -d
```

### Manual Docker Commands

1. **Build Image**
   ```bash
   docker build -t echo-ai-dashboard:latest .
   ```

2. **Run Container**
   ```bash
   docker run -d \
     --name echo-dashboard \
     -p 8501:8501 \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/.streamlit:/app/.streamlit \
     --env-file .env \
     echo-ai-dashboard:latest
   ```

3. **View Logs**
   ```bash
   docker logs -f echo-dashboard
   ```

4. **Stop Container**
   ```bash
   docker stop echo-dashboard
   docker rm echo-dashboard
   ```

### Docker Compose

The `docker-compose.yml` file provides a complete setup:

```yaml
version: '3.8'

services:
  echo-ai-dashboard:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    env_file:
      - .env
    restart: unless-stopped
```

**Commands:**
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild
docker-compose up -d --build
```

---

## Streamlit Cloud

### Deployment Steps

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Connect to Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Sign in with GitHub
   - Click "New app"

3. **Configure App**
   - Repository: `OxainZ/echo-ai-dashboard`
   - Branch: `main`
   - Main file path: `UI.py`

4. **Set Secrets**
   In Streamlit Cloud dashboard, add secrets:
   ```toml
   password_hash = "your_password_hash_here"
   
   # Optional API keys
   ALPHA_VANTAGE_API_KEY = "your_key"
   QUANDL_API_KEY = "your_key"
   NEWS_API_KEY = "your_key"
   ```

5. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Access your app at the provided URL

### Custom Domain (Optional)
In Streamlit Cloud settings:
- Go to Settings > General
- Add your custom domain
- Follow DNS configuration instructions

---

## AWS Deployment

### Option 1: EC2 Instance

1. **Launch EC2 Instance**
   ```bash
   # Instance type: t3.medium or larger
   # OS: Ubuntu 22.04 LTS
   # Security group: Allow port 8501
   ```

2. **Connect and Install**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker ubuntu
   
   # Clone repository
   git clone https://github.com/OxainZ/echo-ai-dashboard.git
   cd echo-ai-dashboard
   
   # Configure and deploy
   cp .env.example .env
   # Edit .env
   docker-compose up -d
   ```

3. **Configure Domain (Optional)**
   - Set up Elastic IP
   - Configure Route 53 DNS
   - Set up SSL with Let's Encrypt

### Option 2: ECS (Elastic Container Service)

1. **Create ECR Repository**
   ```bash
   aws ecr create-repository --repository-name echo-ai-dashboard
   ```

2. **Build and Push Image**
   ```bash
   # Login to ECR
   aws ecr get-login-password --region us-east-1 | \
     docker login --username AWS --password-stdin \
     YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
   
   # Build and tag
   docker build -t echo-ai-dashboard .
   docker tag echo-ai-dashboard:latest \
     YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/echo-ai-dashboard:latest
   
   # Push
   docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/echo-ai-dashboard:latest
   ```

3. **Create ECS Task Definition**
   ```json
   {
     "family": "echo-ai-dashboard",
     "containerDefinitions": [{
       "name": "echo-dashboard",
       "image": "YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/echo-ai-dashboard:latest",
       "memory": 2048,
       "cpu": 1024,
       "portMappings": [{
         "containerPort": 8501,
         "protocol": "tcp"
       }],
       "environment": [
         {"name": "APP_ENV", "value": "production"}
       ]
     }]
   }
   ```

4. **Create ECS Service**
   - Use Fargate launch type
   - Configure load balancer
   - Set desired task count

### Option 3: App Runner

1. **Create apprunner.yaml**
   ```yaml
   version: 1.0
   runtime: python311
   build:
     commands:
       build:
         - pip install -r requirements.txt
   run:
     command: streamlit run UI.py --server.port=8501
     network:
       port: 8501
   ```

2. **Deploy via Console**
   - Go to AWS App Runner
   - Create service from source code
   - Connect GitHub repository
   - Configure build settings

---

## Google Cloud Platform

### Option 1: Cloud Run

1. **Enable APIs**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

2. **Build and Deploy**
   ```bash
   # Set project
   gcloud config set project YOUR_PROJECT_ID
   
   # Build with Cloud Build
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/echo-ai-dashboard
   
   # Deploy to Cloud Run
   gcloud run deploy echo-ai-dashboard \
     --image gcr.io/YOUR_PROJECT_ID/echo-ai-dashboard \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8501 \
     --memory 2Gi
   ```

3. **Set Environment Variables**
   ```bash
   gcloud run services update echo-ai-dashboard \
     --set-env-vars APP_ENV=production,LOG_LEVEL=INFO
   ```

### Option 2: Compute Engine

1. **Create VM Instance**
   ```bash
   gcloud compute instances create echo-dashboard \
     --image-family=ubuntu-2204-lts \
     --image-project=ubuntu-os-cloud \
     --machine-type=e2-medium \
     --zone=us-central1-a \
     --tags=http-server
   ```

2. **Install and Run**
   ```bash
   # SSH into instance
   gcloud compute ssh echo-dashboard --zone=us-central1-a
   
   # Follow EC2 installation steps above
   ```

---

## Azure Deployment

### Option 1: Container Instances

1. **Login to Azure**
   ```bash
   az login
   ```

2. **Create Resource Group**
   ```bash
   az group create --name echo-dashboard-rg --location eastus
   ```

3. **Create Container Registry**
   ```bash
   az acr create --resource-group echo-dashboard-rg \
     --name echodashboardacr --sku Basic
   ```

4. **Build and Push**
   ```bash
   az acr build --registry echodashboardacr \
     --image echo-ai-dashboard:latest .
   ```

5. **Deploy Container**
   ```bash
   az container create \
     --resource-group echo-dashboard-rg \
     --name echo-dashboard \
     --image echodashboardacr.azurecr.io/echo-ai-dashboard:latest \
     --cpu 1 --memory 2 \
     --registry-login-server echodashboardacr.azurecr.io \
     --registry-username $(az acr credential show --name echodashboardacr --query username -o tsv) \
     --registry-password $(az acr credential show --name echodashboardacr --query passwords[0].value -o tsv) \
     --dns-name-label echo-dashboard \
     --ports 8501
   ```

### Option 2: App Service

1. **Create App Service Plan**
   ```bash
   az appservice plan create --name echo-plan \
     --resource-group echo-dashboard-rg \
     --sku B1 --is-linux
   ```

2. **Create Web App**
   ```bash
   az webapp create --resource-group echo-dashboard-rg \
     --plan echo-plan --name echo-ai-dashboard \
     --deployment-container-image-name echodashboardacr.azurecr.io/echo-ai-dashboard:latest
   ```

3. **Configure Settings**
   ```bash
   az webapp config appsettings set --resource-group echo-dashboard-rg \
     --name echo-ai-dashboard \
     --settings APP_ENV=production
   ```

---

## Environment Variables

### Required Variables

```bash
# Security
PASSWORD_HASH=your_password_hash

# Optional but Recommended
ALPHA_VANTAGE_API_KEY=your_key
QUANDL_API_KEY=your_key
NEWS_API_KEY=your_key
```

### Production Recommendations

```bash
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
CACHE_TTL_SECONDS=300
```

### Generating Password Hash

```bash
python -c "import hashlib; print(hashlib.sha256('your_password'.encode()).hexdigest())"
```

---

## Monitoring and Maintenance

### Health Checks

**Docker**:
```bash
docker ps
docker logs echo-dashboard
curl http://localhost:8501/_stcore/health
```

**Cloud Platforms**:
- Set up health check endpoints
- Configure auto-restart policies
- Set up uptime monitoring

### Logging

**View Logs**:
```bash
# Docker
docker-compose logs -f

# Cloud Run
gcloud run logs tail echo-ai-dashboard

# ECS
aws logs tail /ecs/echo-ai-dashboard --follow
```

### Backup

**Data Backup**:
```bash
# Backup data directory
tar -czf backup-$(date +%Y%m%d).tar.gz data/ logs/

# Upload to S3
aws s3 cp backup-*.tar.gz s3://your-backup-bucket/
```

### Updates

**Update Application**:
```bash
git pull origin main
docker-compose up -d --build
```

### Security

1. **Use HTTPS**
   - Set up SSL certificates
   - Use reverse proxy (nginx)
   - Enable HTTPS redirects

2. **Firewall Rules**
   - Limit port 8501 to specific IPs
   - Use VPN for admin access
   - Enable cloud provider firewalls

3. **Secrets Management**
   - Use cloud secret managers (AWS Secrets Manager, GCP Secret Manager)
   - Rotate API keys regularly
   - Never commit secrets to git

---

## Troubleshooting

### Common Issues

**Port Already in Use**:
```bash
# Find process
lsof -i :8501
# Kill process
kill -9 <PID>
```

**Memory Issues**:
- Increase Docker memory limits
- Use larger instance types
- Optimize caching

**Performance Issues**:
- Enable caching
- Use CDN for static assets
- Scale horizontally

---

## Cost Estimates

### AWS
- EC2 t3.medium: ~$30/month
- ECS Fargate: ~$40/month
- App Runner: ~$35/month

### Google Cloud
- Cloud Run: ~$25/month (pay-per-use)
- Compute Engine e2-medium: ~$25/month

### Azure
- Container Instance: ~$35/month
- App Service B1: ~$50/month

### Streamlit Cloud
- Free for public apps
- $20-200/month for private apps

---

Last Updated: December 2024
