# ASU1-Loom Quick Start Guide

Get up and running with ASU1-Loom in minutes!

## Prerequisites

- Docker & Docker Compose installed
- PostgreSQL database on pandaserver.ddns.net (4.20.69.11)
- Git

## Quick Setup (5 minutes)

### 1. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# IMPORTANT: Update these values:
# - DATABASE_URL=postgresql://loom_user:YOUR_PASSWORD@pandaserver.ddns.net:5432/loom_db
# - SECRET_KEY=generate-a-secure-random-key
# - TRAEFIK_EMAIL=your-email@example.com
```

### 2. Start the Platform

```bash
# Option A: Using the setup script (Linux/Mac)
chmod +x scripts/setup.sh
./scripts/setup.sh

# Option B: Manual start
docker-compose up -d
```

### 3. Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **GraphQL**: http://localhost:8000/graphql
- **Traefik Dashboard**: http://localhost:8080

## Create Your First Container

1. Go to http://localhost:3000
2. Click "Create New" in the navigation
3. Fill in the form:
   - **Name**: `my-first-app`
   - **Image**: `nginx`
   - **Tag**: `latest`
   - **Subdomain**: `myapp`
   - **Internal Port**: `80`
4. Click "Create Container"
5. Access your app at: `http://myapp.pandaserver.ddns.net`

## Common Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View running containers
docker ps

# Access backend shell
docker-compose exec backend bash

# View database
docker-compose exec postgres psql -U loom_user -d loom_db
```

## Troubleshooting

### Can't connect to database?
```bash
# Test connection
psql -h pandaserver.ddns.net -U loom_user -d loom_db

# Check if PostgreSQL is running on server
ssh user@pandaserver.ddns.net
sudo systemctl status postgresql
```

### Docker permission denied?
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Log out and back in
```

### Port already in use?
```bash
# Find what's using the port
netstat -tulpn | grep :8000

# Change port in .env file
API_PORT=8001
```

## Next Steps

- Read the [Setup Guide](docs/SETUP.md) for detailed configuration
- Check the [Architecture](docs/ARCHITECTURE.md) to understand the system
- Explore the GraphQL API at http://localhost:8000/graphql
- Create container templates for common applications

## Example Containers to Try

### 1. Simple Web Server (nginx)
```
Name: web-server
Image: nginx
Tag: latest
Subdomain: web
Internal Port: 80
```

### 2. Node.js Application
```
Name: node-app
Image: node
Tag: 18-alpine
Subdomain: nodeapp
Internal Port: 3000
Environment: {"NODE_ENV": "production"}
```

### 3. Python API
```
Name: python-api
Image: python
Tag: 3.11-slim
Subdomain: pyapi
Internal Port: 8000
```

### 4. Database (PostgreSQL)
```
Name: postgres-db
Image: postgres
Tag: 15-alpine
Subdomain: db
Internal Port: 5432
Environment: {"POSTGRES_PASSWORD": "secret"}
```

## Support

For issues or questions:
- Check logs: `docker-compose logs`
- Review documentation in `/docs`
- Check GitHub issues (if repository is public)

---

**Happy Container Orchestrating! 🧵🐳**
