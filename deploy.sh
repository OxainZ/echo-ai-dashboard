#!/bin/bash
# Deployment script for Echo AI Dashboard

set -e

echo "🚀 Echo AI Dashboard Deployment Script"
echo "======================================="

# Configuration
APP_NAME="echo-ai-dashboard"
DOCKER_IMAGE="$APP_NAME:latest"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please edit it with your configuration."
        echo "   After editing, run this script again."
        exit 0
    else
        echo "❌ .env.example not found. Please create configuration manually."
        exit 1
    fi
fi

echo "📦 Building Docker image..."
docker build -t $DOCKER_IMAGE .

echo "🧪 Testing Docker image..."
docker run --rm $DOCKER_IMAGE python -c "import streamlit; import pandas; import numpy; print('✅ Dependencies OK')"

echo "🛑 Stopping existing containers..."
docker-compose down

echo "🚀 Starting application..."
docker-compose up -d

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Dashboard URL: http://localhost:8501"
echo ""
echo "Useful commands:"
echo "  View logs:     docker-compose logs -f"
echo "  Stop app:      docker-compose down"
echo "  Restart app:   docker-compose restart"
echo "  View status:   docker-compose ps"
echo ""
