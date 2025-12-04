# ASU1-Loom Setup Guide

This guide will help you set up and run the ASU1-Loom container orchestration platform.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- **Python** 3.11+ (for local development)
- **PostgreSQL** (if running database externally)
- **Git**

## External Database Setup (pandaserver.ddns.net)

Since you're using an external PostgreSQL server, you'll need to:

1. **Connect to your server** (4.20.69.11 / pandaserver.ddns.net)

2. **Install PostgreSQL** (if not already installed):
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

3. **Create the database and user**:
```bash
sudo -u postgres psql

# In PostgreSQL prompt:
CREATE DATABASE loom_db;
CREATE USER loom_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE loom_db TO loom_user;
\q
```

4. **Configure PostgreSQL for remote connections**:

Edit `/etc/postgresql/[version]/main/postgresql.conf`:
```
listen_addresses = '*'
```

Edit `/etc/postgresql/[version]/main/pg_hba.conf`:
```
# Add this line (adjust IP range as needed)
host    loom_db    loom_user    0.0.0.0/0    md5
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

5. **Configure firewall** (if applicable):
```bash
sudo ufw allow 5432/tcp
```

## Local Setup

### 1. Clone the Repository

```bash
cd Project
cd ASU1-Loom
```

### 2. Configure Environment Variables

Copy the example environment file and update it:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Database Configuration (External Server)
DATABASE_URL=postgresql://loom_user:your_secure_password@pandaserver.ddns.net:5432/loom_db
POSTGRES_USER=loom_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=loom_db

# Docker Configuration
DOCKER_HOST=unix:///var/run/docker.sock
DOCKER_NETWORK=loom_network

# Traefik Configuration
TRAEFIK_DOMAIN=pandaserver.ddns.net
TRAEFIK_EMAIL=your-email@example.com
TRAEFIK_DASHBOARD_PORT=8080

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
API_DEBUG=true

# Security (CHANGE THESE!)
SECRET_KEY=generate-a-secure-random-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,http://pandaserver.ddns.net

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/loom.log
```

### 3. Update Docker Compose for External Database

Since you're using an external database, modify `docker-compose.yml`:

Comment out or remove the `postgres` service section, and update the `backend` service to use the external database URL from your `.env` file.

### 4. Build and Start Services

```bash
# Build the images
docker-compose build

# Start the services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 5. Initialize the Database

The database tables will be created automatically when the backend starts. You can verify by checking the logs:

```bash
docker-compose logs backend
```

### 6. Access the Application

- **Frontend**: http://localhost:3000 or http://pandaserver.ddns.net
- **Backend API**: http://localhost:8000
- **GraphQL Playground**: http://localhost:8000/graphql
- **Traefik Dashboard**: http://localhost:8080

## Development Setup

For local development without Docker:

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

### Frontend

The frontend is static HTML/CSS/JS with WebAssembly support. Simply open `frontend/dist/index.html` in a browser, or serve it with a local server:

```bash
cd frontend/dist
python -m http.server 3000
```

## Testing

```bash
# Run backend tests
cd backend
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

## Troubleshooting

### Database Connection Issues

1. **Check if PostgreSQL is running**:
```bash
sudo systemctl status postgresql
```

2. **Test connection from local machine**:
```bash
psql -h pandaserver.ddns.net -U loom_user -d loom_db
```

3. **Check firewall rules**:
```bash
sudo ufw status
```

### Docker Issues

1. **Check Docker is running**:
```bash
docker ps
```

2. **Check Docker socket permissions**:
```bash
ls -la /var/run/docker.sock
```

3. **View container logs**:
```bash
docker-compose logs [service-name]
```

### Traefik Routing Issues

1. **Check Traefik dashboard**: http://localhost:8080
2. **Verify container labels**:
```bash
docker inspect [container-name]
```

## Production Deployment

For production deployment on pandaserver.ddns.net:

1. **Enable HTTPS** with Let's Encrypt in `traefik.yml`
2. **Set strong passwords** in `.env`
3. **Disable debug mode**: `API_DEBUG=false`
4. **Configure proper CORS origins**
5. **Set up monitoring and logging**
6. **Regular backups** of the PostgreSQL database

## Next Steps

- Read the [API Documentation](API.md)
- Check the [Architecture Overview](ARCHITECTURE.md)
- Review the [Contributing Guidelines](CONTRIBUTING.md)

## Support

For issues or questions:
- Check the logs: `docker-compose logs`
- Review the documentation in `/docs`
- Contact: Erik Kjær Klint
