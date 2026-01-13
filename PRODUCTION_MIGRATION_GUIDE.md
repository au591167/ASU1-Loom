# ASU1-Loom Production Migration Guide

## Overview
This guide migrates ASU1-Loom from mock mode to full production with real Docker functionality on Ubuntu Linux server.

## Prerequisites
- Ubuntu Server 22.04+ with sudo access
- Domain name (optional but recommended)
- SSH access to server
- Git repository access

---

## Phase 1: Server Preparation

### Step 1.1: Update System
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git htop ufw
```

### Step 1.2: Configure Firewall
```bash
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000  # Backend API
sudo ufw allow 3000  # Frontend
sudo ufw --force enable
```

### Step 1.3: Create Application User
```bash
sudo useradd -m -s /bin/bash loom
sudo usermod -aG docker loom
sudo mkdir -p /opt/loom
sudo chown loom:loom /opt/loom
```

---

## Phase 2: Docker Ecosystem Setup

### Step 2.1: Install Docker
```bash
# Remove old versions
sudo apt remove -y docker docker-engine docker.io containerd runc

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl enable docker
sudo systemctl start docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 2.2: Install Traefik
```bash
# Create Traefik directory
sudo mkdir -p /opt/traefik
cd /opt/traefik

# Create traefik.yml
cat > traefik.yml << 'EOF'
api:
  dashboard: true
  insecure: true  # Remove in production

entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
  file:
    directory: "/etc/traefik/dynamic"
    watch: true

certificatesResolvers:
  letsencrypt:
    acme:
      email: your-email@example.com
      storage: /etc/traefik/acme.json
      httpChallenge:
        entryPoint: web
EOF

# Create dynamic directory
sudo mkdir -p /etc/traefik/dynamic
sudo chown -R loom:loom /opt/traefik /etc/traefik
```

### Step 2.3: Install PostgreSQL
```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE loom_db;"
sudo -u postgres psql -c "CREATE USER loom_user WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE loom_db TO loom_user;"

# Configure PostgreSQL for remote access (optional)
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" /etc/postgresql/14/main/postgresql.conf
echo "host    loom_db         loom_user       172.0.0.0/8            md5" | sudo tee -a /etc/postgresql/14/main/pg_hba.conf
sudo systemctl restart postgresql
```

---

## Phase 3: Application Deployment

### Step 3.1: Clone Repository
```bash
cd /opt/loom
sudo chown loom:loom /opt/loom
sudo -u loom git clone https://github.com/your-username/ASU1-Loom.git .
sudo -u loom git checkout master
```

### Step 3.2: Create Environment Configuration
```bash
cd /opt/loom
sudo -u loom cp .env.example .env  # If you have an example file

# Edit .env file
sudo -u loom tee .env > /dev/null << 'EOF'
# Database
DATABASE_URL=postgresql://loom_user:your_secure_password@localhost:5432/loom_db

# Docker
DOCKER_HOST=unix:///var/run/docker.sock
DOCKER_NETWORK=loom_network

# Traefik
TRAEFIK_DOMAIN=your-domain.com
TRAEFIK_EMAIL=your-email@your-domain.com

# Application
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_PORT=3000
ENVIRONMENT=production
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-very-secure-secret-key-here
EOF
```

### Step 3.3: Create Docker Network
```bash
docker network create loom_network
```

### Step 3.4: Initialize Database
```bash
cd /opt/loom
sudo -u loom python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Initialize database
cd backend
python3 -c "
from database.connection import init_db
import asyncio
asyncio.run(init_db())
print('Database initialized successfully')
"
```

---

## Phase 4: Production Configuration

### Step 4.1: Update Docker Compose for Production
```bash
cd /opt/loom
sudo -u loom tee docker-compose.prod.yml > /dev/null << 'EOF'
version: '3.8'

services:
  traefik:
    image: traefik:v2.10
    container_name: loom-traefik
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"  # Dashboard
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /opt/traefik/traefik.yml:/traefik.yml:ro
      - /etc/traefik:/etc/traefik:ro
    networks:
      - loom_network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.traefik.rule=Host(`traefik.your-domain.com`)"
      - "traefik.http.routers.traefik.service=api@internal"
      - "traefik.http.routers.traefik.middlewares=auth"
      - "traefik.http.middlewares.auth.basicauth.users=admin:$$2y$$10$$..."  # Generate with htpasswd

  postgres:
    image: postgres:15
    container_name: loom-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: loom_db
      POSTGRES_USER: loom_user
      POSTGRES_PASSWORD: your_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - loom_network
    labels:
      - "traefik.enable=false"

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: loom-backend
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql://loom_user:your_secure_password@postgres:5432/loom_db
      - DOCKER_HOST=unix:///var/run/docker.sock
      - ENVIRONMENT=production
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - loom_network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.backend.rule=Host(`api.your-domain.com`)"
      - "traefik.http.routers.backend.entrypoints=websecure"
      - "traefik.http.routers.backend.tls.certresolver=letsencrypt"
      - "traefik.http.services.backend.loadbalancer.server.port=8000"
    depends_on:
      - postgres

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: loom-frontend
    restart: unless-stopped
    networks:
      - loom_network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`your-domain.com`)"
      - "traefik.http.routers.frontend.entrypoints=websecure"
      - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
      - "traefik.http.services.frontend.loadbalancer.server.port=80"

volumes:
  postgres_data:

networks:
  loom_network:
    external: true
EOF
```

### Step 4.2: Update Application Settings for Production
```bash
cd /opt/loom/backend/config
sudo -u loom tee settings.py > /dev/null << 'EOF'
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Application
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    environment: str = "development"
    log_level: str = "INFO"
    log_file: str = "/opt/loom/logs/loom.log"

    # Database
    database_url: str = "sqlite:///./loom.db"

    # Docker
    docker_host: str = "unix:///var/run/docker.sock"
    docker_network: str = "loom_network"

    # Traefik
    traefik_domain: str = "localhost"
    traefik_email: str = "admin@localhost"

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Security
    secret_key: str = "your-secret-key-change-in-production"

    class Config:
        env_file = "/opt/loom/.env"
        case_sensitive = False

settings = Settings()
EOF
```

---

## Phase 5: Production Testing

### Step 5.1: Start Services
```bash
cd /opt/loom
sudo -u loom docker-compose -f docker-compose.prod.yml up -d
```

### Step 5.2: Test Database Connection
```bash
cd /opt/loom
sudo -u loom python3 -c "
import asyncio
from backend.database.connection import get_db
from backend.models.container import Container

db = next(get_db())
containers = db.query(Container).all()
print(f'Database connected. Found {len(containers)} containers.')
"
```

### Step 5.3: Test Docker Integration
```bash
# Test container creation
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { createContainer(input: { name: \"test-container\", image: \"nginx\", tag: \"latest\", subdomain: \"test\", internalPort: 80 }) { id name status } }"
  }'
```

### Step 5.4: Test Metrics Functionality
```bash
# Get container stats (should now work with real Docker)
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ containerStats(id: \"1\") { cpuUsage memoryUsage memoryLimit networkRx networkTx } }"
  }'
```

---

## Phase 6: Production Optimization

### Step 6.1: SSL Certificate Setup
```bash
# Wait for Let's Encrypt certificates to be generated
sudo watch -n 10 "ls -la /etc/traefik/acme.json"
```

### Step 6.2: Monitoring Setup
```bash
# Install monitoring tools
sudo apt install -y prometheus-node-exporter

# Create log rotation
sudo tee /etc/logrotate.d/loom > /dev/null << 'EOF'
/opt/loom/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 loom loom
    postrotate
        docker-compose -f /opt/loom/docker-compose.prod.yml restart backend
    endscript
}
EOF
```

### Step 6.3: Backup Configuration
```bash
# Create backup script
sudo tee /opt/loom/backup.sh > /dev/null << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/loom/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
docker exec loom-postgres pg_dump -U loom_user loom_db > $BACKUP_DIR/db_$DATE.sql

# Backup volumes
docker run --rm -v loom_postgres_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/volumes_$DATE.tar.gz -C /data .

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

sudo chmod +x /opt/loom/backup.sh
```

### Step 6.4: Systemd Service (Optional)
```bash
sudo tee /etc/systemd/system/loom.service > /dev/null << 'EOF'
[Unit]
Description=ASU1-Loom Container Orchestration Platform
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
User=loom
WorkingDirectory=/opt/loom
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable loom
```

---

## Phase 7: Final Verification

### Step 7.1: Complete System Test
```bash
# Test all major functionality
echo "Testing ASU1-Loom Production System..."

# 1. Health check
curl -f http://localhost:8000/health

# 2. System info
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ systemInfo { dockerVersion totalContainers } }"}'

# 3. Container lifecycle
CONTAINER_ID=$(curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { createContainer(input: { name: \"prod-test\", image: \"nginx\", tag: \"latest\", subdomain: \"test\", internalPort: 80 }) { id } }"}' | jq -r '.data.createContainer.id')

# Start container
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"mutation { startContainer(id: \\\"$CONTAINER_ID\\\") { status } }\"}"

# Get stats
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"{ containerStats(id: \\\"$CONTAINER_ID\\\") { cpuUsage memoryUsage } }\"}"

# Stop and delete
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"mutation { stopContainer(id: \\\"$CONTAINER_ID\\\") { status } }\"}"

curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"mutation { deleteContainer(id: \\\"$CONTAINER_ID\\\") { success } }\"}"

echo "All tests completed successfully!"
```

### Step 7.2: Access Production System
- **Frontend:** `https://your-domain.com`
- **API:** `https://api.your-domain.com/graphql`
- **Traefik Dashboard:** `https://traefik.your-domain.com`

---

## Troubleshooting

### Common Issues:

1. **Docker permission denied:**
   ```bash
   sudo usermod -aG docker loom
   sudo systemctl restart docker
   ```

2. **PostgreSQL connection failed:**
   ```bash
   sudo -u postgres psql -c "ALTER USER loom_user PASSWORD 'new_password';"
   # Update .env file with new password
   ```

3. **SSL certificates not generating:**
   ```bash
   sudo tail -f /opt/traefik/logs/traefik.log
   # Check DNS configuration
   ```

4. **Metrics not working:**
   ```bash
   # Ensure Docker socket is mounted correctly
   docker exec loom-backend docker stats --no-stream
   ```

---

## Maintenance Commands

```bash
# View logs
cd /opt/loom && docker-compose -f docker-compose.prod.yml logs -f

# Restart services
cd /opt/loom && docker-compose -f docker-compose.prod.yml restart

# Update application
cd /opt/loom && git pull && docker-compose -f docker-compose.prod.yml up -d --build

# Backup
/opt/loom/backup.sh

# Monitor resources
docker stats
htop
```

---

## Security Checklist

- [ ] Changed default passwords
- [ ] SSL certificates configured
- [ ] Firewall rules applied
- [ ] Docker socket access restricted
- [ ] Database backups scheduled
- [ ] Log rotation configured
- [ ] System updates scheduled
- [ ] Monitoring alerts configured

**Migration complete! Your ASU1-Loom system is now running in full production mode with real Docker functionality.**
