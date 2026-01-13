# Getting Started with ASU1-Loom

Welcome to ASU1-Loom! This guide will help you get your container orchestration platform up and running.

## 🚀 Quick Overview

ASU1-Loom is a hybrid container orchestration platform that combines:
- **WebAssembly Frontend** - Modern, lightweight UI
- **FastAPI Backend** - Python-based GraphQL API
- **Docker Integration** - Full container lifecycle management
- **Traefik Proxy** - Automatic subdomain routing
- **PostgreSQL** - External database on pandaserver.ddns.net

## 📋 Prerequisites Checklist

Before you begin, make sure you have:

- [ ] **Docker Desktop** installed and running
- [ ] **Git** installed
- [ ] **Python 3.11+** (for local development)
- [ ] **SSH access** to pandaserver.ddns.net
- [ ] **VSCode** (recommended) with Python extension

## 🎯 Setup Steps

### Step 1: Fix VSCode Environment Warning ✅

The VSCode settings have been configured to enable environment file usage. The warning you saw is now resolved!

**What was done:**
- Created `.vscode/settings.json` with `"python.terminal.useEnvFile": true`
- This allows VSCode to automatically load variables from `.env` file

**To verify:**
1. Reload VSCode window (Ctrl+Shift+P → "Reload Window")
2. The warning should disappear

### Step 2: Set Up PostgreSQL on Your Server 🗄️

You need to install and configure PostgreSQL on pandaserver.ddns.net before the application can work.

**Follow the comprehensive guide:**
📖 **[docs/DATABASE_SETUP.md](docs/DATABASE_SETUP.md)**

**Quick summary:**
```bash
# SSH into your server
ssh user@pandaserver.ddns.net

# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib -y

# Configure for remote access
sudo nano /etc/postgresql/15/main/postgresql.conf
# Set: listen_addresses = '*'

sudo nano /etc/postgresql/15/main/pg_hba.conf
# Add: host all all 0.0.0.0/0 md5

# Restart PostgreSQL
sudo systemctl restart postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE loom_db;
CREATE USER loom_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE loom_db TO loom_user;
\q

# Allow firewall
sudo ufw allow 5432/tcp
```

### Step 3: Configure Environment Variables 🔧

1. **Copy the example environment file:**
   ```bash
   cd Project/ASU1-Loom
   cp .env.example .env
   ```

2. **Edit `.env` with your actual credentials:**
   ```bash
   # Use your favorite editor
   code .env
   # or
   nano .env
   ```

3. **Update these critical values:**
   ```env
   # Replace with your actual password from Step 2
   DATABASE_URL=postgresql+asyncpg://loom_user:YOUR_ACTUAL_PASSWORD@pandaserver.ddns.net:5432/loom_db
   
   # Generate a secure secret key
   SECRET_KEY=your-secure-random-key-here
   
   # Your email for Let's Encrypt (if using SSL)
   TRAEFIK_EMAIL=your-email@example.com
   ```

4. **Generate a secure secret key:**
   ```bash
   # On Linux/Mac
   openssl rand -hex 32
   
   # On Windows (PowerShell)
   -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
   ```

### Step 4: Test Database Connection 🔌

Before starting the application, verify you can connect to the database:

```bash
# Using psql (if installed)
psql -h pandaserver.ddns.net -U loom_user -d loom_db

# Using Python
python -c "import psycopg2; conn = psycopg2.connect('postgresql://loom_user:YOUR_PASSWORD@pandaserver.ddns.net:5432/loom_db'); print('✅ Connected!'); conn.close()"
```

**Expected result:** You should see a successful connection message.

### Step 5: Build and Start Services 🐳

```bash
cd Project/ASU1-Loom

# Build Docker images
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 6: Access the Application 🌐

Once all services are running:

1. **Frontend UI:** http://localhost:3000
2. **Backend API Docs:** http://localhost:8000/docs
3. **GraphQL Playground:** http://localhost:8000/graphql
4. **Traefik Dashboard:** http://localhost:8080

## 📚 Documentation Structure

Your project includes comprehensive documentation:

```
Project/ASU1-Loom/
├── README.md                    # Project overview
├── GETTING_STARTED.md          # This file - start here!
├── QUICKSTART.md               # 5-minute quick start
├── PROJECT_SUMMARY.md          # Detailed project information
├── TESTING_CHECKLIST.md        # Complete testing procedures
└── docs/
    ├── DATABASE_SETUP.md       # PostgreSQL installation guide
    ├── SETUP.md                # Detailed setup instructions
    └── ARCHITECTURE.md         # System architecture
```

## 🎓 Recommended Reading Order

1. **GETTING_STARTED.md** (you are here) - Initial setup
2. **docs/DATABASE_SETUP.md** - Set up your database
3. **QUICKSTART.md** - Quick reference guide
4. **docs/ARCHITECTURE.md** - Understand the system
5. **TESTING_CHECKLIST.md** - Test your installation

## 🔧 Common Issues and Solutions

### Issue 1: VSCode Environment Warning
**Problem:** "An environment file is configured but terminal environment injection is disabled"

**Solution:** ✅ Already fixed! The `.vscode/settings.json` file has been created with the correct settings. Just reload VSCode.

### Issue 2: Cannot Connect to Database
**Problem:** Connection refused or authentication failed

**Solutions:**
1. Verify PostgreSQL is installed and running on pandaserver
2. Check firewall allows port 5432
3. Verify credentials in `.env` file
4. See [docs/DATABASE_SETUP.md](docs/DATABASE_SETUP.md) troubleshooting section

### Issue 3: Docker Build Fails
**Problem:** Docker images fail to build

**Solutions:**
1. Ensure Docker Desktop is running
2. Check internet connection (needs to download images)
3. Try: `docker-compose build --no-cache`

### Issue 4: Port Already in Use
**Problem:** "Port 8000 is already allocated"

**Solutions:**
1. Stop other services using the port
2. Change port in `.env` file: `API_PORT=8001`
3. Update docker-compose.yml accordingly

## 🧪 Testing Your Installation

Follow the testing checklist to verify everything works:

```bash
# Quick health check
curl http://localhost:8000/docs
curl http://localhost:3000
curl http://localhost:8080

# Test GraphQL API
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ containers { id name } }"}'
```

For comprehensive testing, see: **[TESTING_CHECKLIST.md](TESTING_CHECKLIST.md)**

## 🎯 Next Steps

After completing the setup:

1. ✅ Create your first container through the UI
2. ✅ Test subdomain routing with Traefik
3. ✅ Explore the GraphQL API
4. ✅ Review the architecture documentation
5. ✅ Start developing your features!

## 📞 Need Help?

- **Database Setup:** See [docs/DATABASE_SETUP.md](docs/DATABASE_SETUP.md)
- **Architecture Questions:** See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Testing Issues:** See [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md)
- **Quick Reference:** See [QUICKSTART.md](QUICKSTART.md)

## 🎓 Academic Context

This project demonstrates concepts from **EH5ASU1 - Avanceret Softwareudvikling 1**:

- ✅ Graphical User Interfaces (WebAssembly)
- ✅ Asynchronous Programming (asyncio, FastAPI)
- ✅ Threading and Concurrency
- ✅ ORM (SQLAlchemy)
- ✅ GraphQL API Design
- ✅ Scalable System Architecture
- ✅ Container Orchestration

## 🚀 Ready to Start?

1. **First time?** → Follow Steps 1-6 above
2. **Database not set up?** → Go to [docs/DATABASE_SETUP.md](docs/DATABASE_SETUP.md)
3. **Already configured?** → Run `docker-compose up -d` and start building!

---

**Happy Container Orchestrating! 🧵✨**

*Last Updated: December 2025*
