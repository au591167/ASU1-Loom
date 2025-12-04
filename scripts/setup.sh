#!/bin/bash
# ASU1-Loom Setup Script

echo "🧵 ASU1-Loom Setup Script"
echo "=========================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before continuing!"
    echo "   Especially update:"
    echo "   - DATABASE_URL (with your PostgreSQL credentials)"
    echo "   - SECRET_KEY (generate a secure random key)"
    echo "   - TRAEFIK_EMAIL (your email for Let's Encrypt)"
    echo ""
    read -p "Press Enter after you've updated the .env file..."
fi

echo "✅ .env file exists"
echo ""

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p infrastructure/traefik/dynamic
echo "✅ Directories created"
echo ""

# Build Docker images
echo "🔨 Building Docker images..."
docker-compose build
echo "✅ Images built"
echo ""

# Start services
echo "🚀 Starting services..."
docker-compose up -d
echo "✅ Services started"
echo ""

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker-compose ps
echo ""

echo "✅ Setup complete!"
echo ""
echo "🌐 Access the application:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - GraphQL Playground: http://localhost:8000/graphql"
echo "   - Traefik Dashboard: http://localhost:8080"
echo ""
echo "📝 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
