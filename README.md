# ASU1-Loom 🧵

**Hybrid Container Orchestration Platform with WebAssembly GUI and Reverse Proxy**

## Overview

Loom is a modern container orchestration platform that combines WebAssembly-based frontend with Docker backend to provide a flexible and scalable solution for managing containerized applications. The system automatically handles subdomain routing through Traefik reverse proxy, making it ideal for development environments, game servers, and multi-tenant applications.

## Features

- 🌐 **WebAssembly GUI** - Lightweight, portable interface using Pyodide
- 🐳 **Docker Integration** - Full container lifecycle management
- 🔀 **Automatic Routing** - Dynamic subdomain configuration via Traefik
- 📊 **GraphQL API** - Flexible and efficient data communication
- 💾 **PostgreSQL Backend** - Robust metadata storage with SQLAlchemy ORM
- 🚀 **Scalable Architecture** - Built for growth with Docker Swarm support
- 🎮 **Modpack Automation** - One-click Minecraft modpack deployment (NEW!)
  - CurseForge, Modrinth, and FTB integration
  - Automatic file downloading and installation
  - Support for Forge, NeoForge, and Fabric

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     WASM Frontend (Pyodide)                  │
│                  Browser-based GUI Interface                 │
└──────────────────────────┬──────────────────────────────────┘
                           │ GraphQL API
┌──────────────────────────┴──────────────────────────────────┐
│                      Backend Server                          │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │  GraphQL API   │  │   Docker     │  │   PostgreSQL    │ │
│  │   (FastAPI)    │  │   Manager    │  │   + SQLAlchemy  │ │
│  └────────────────┘  └──────────────┘  └─────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                    Traefik Reverse Proxy                     │
│              Automatic Subdomain Routing                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    Docker Containers
              (Apps, Services, Game Servers)
```

## Technology Stack

### Frontend
- WebAssembly (WASM)
- Pyodide (Python in browser)
- Modern HTML5/CSS3/JavaScript

### Backend
- Python 3.11+
- FastAPI (GraphQL endpoint)
- Docker SDK for Python
- SQLAlchemy ORM
- PostgreSQL
- Asyncio for concurrent operations

### Infrastructure
- Docker & Docker Swarm
- Traefik (Reverse Proxy)
- PostgreSQL Database

## Project Structure

```
ASU1-Loom/
├── backend/              # Python backend server
│   ├── api/             # GraphQL API endpoints
│   ├── models/          # SQLAlchemy models
│   ├── services/        # Business logic (includes modpack service)
│   ├── docker_manager/  # Docker integration
│   └── config/          # Configuration files
├── frontend/            # WASM-based GUI
│   ├── dist/           # Production files
│   │   ├── index.html  # Main interface
│   │   ├── app.js      # Application logic
│   │   ├── templates.js # Container templates
│   │   └── styles.css  # Styling
│   └── serve.py        # Development server
├── infrastructure/      # Docker & Traefik configs
│   ├── docker/         # Dockerfiles
│   ├── traefik/        # Traefik configuration
│   └── compose/        # Docker Compose files
├── database/           # Database schemas & migrations
├── docs/              # Technical documentation
├── documentation/     # Project documentation & guides
├── tests/             # Test suites
└── scripts/           # Utility scripts
```

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- PostgreSQL
- Node.js (for frontend build tools)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ASU1-Loom

# Set up backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Return to root directory
cd ..

# Set up database (optional, for production)
# python scripts/init_db.py

# Start infrastructure (optional, for production)
# docker-compose up -d
```

### Quick Start (Development)

**One-Click Launch** 🚀

The easiest way to start the development environment:

**Windows:**
```bash
# Double-click or run:
dev-start.bat
```

**Linux/Mac:**
```bash
# Make executable (first time only):
chmod +x dev-start.sh

# Run:
./dev-start.sh
```

**Or use Python directly:**
```bash
python dev-launcher.py
```

This will automatically:
- ✅ Check prerequisites
- ✅ Start backend server (port 8000)
- ✅ Start frontend server (port 3000)
- ✅ Display access URLs
- ✅ Monitor both services
- ✅ Handle graceful shutdown (Ctrl+C)

**Manual Start (Advanced):**

If you prefer to start services separately:

```bash
# Terminal 1 - Backend
cd backend
python serve.py  # or python main.py

# Terminal 2 - Frontend
cd frontend
python serve.py
```

### Configuration

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/loom

# Docker
DOCKER_HOST=unix:///var/run/docker.sock

# Traefik
TRAEFIK_DOMAIN=yourdomain.com

# API
API_PORT=8000

# Modpack APIs (Optional but recommended)
CURSEFORGE_API_KEY=your_curseforge_key_here
MODRINTH_API_KEY=your_modrinth_key_here
```

**Getting API Keys:**
- CurseForge: https://console.curseforge.com/
- Modrinth: https://modrinth.com/settings/account

## Usage

1. Access the web interface at `http://localhost:8000`
2. Create a new container through the GUI
3. Configure container settings (image, ports, environment variables)
4. The system automatically assigns a subdomain (e.g., `myapp.yourdomain.com`)
5. Traefik routes traffic to your container

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
```bash
black backend/
flake8 backend/
mypy backend/
```

## Academic Context

This project is developed as part of **EH5ASU1 - Avanceret Softwareudvikling 1** and demonstrates:

- ✅ Graphical User Interfaces (WASM-based)
- ✅ Asynchronous Programming (asyncio)
- ✅ Threading and Concurrency
- ✅ ORM (SQLAlchemy)
- ✅ GraphQL API Design
- ✅ Scalable System Architecture
- ✅ Container Orchestration
- ✅ Reverse Proxy Configuration

## Container Templates

Loom includes pre-configured templates for quick deployment:

### Development Containers
- **Node.js** - Modern JavaScript runtime
- **Python** - Python development environment
- **PHP** - PHP with Apache
- **Nginx** - Web server

### Minecraft Servers
- **Vanilla** - Official Minecraft server
- **Paper** - Optimized server with plugin support
- **Spigot** - Plugin-compatible server
- **Forge** - Mod support (classic)
- **NeoForge** - Modern mod loader
- **Fabric** - Lightweight mod loader

### Game Servers
- **Valheim** - Viking survival game
- **Terraria** - 2D adventure game

### Custom
- **Custom Container** - Specify any Docker image with optional environment variables

## Modpack Automation (NEW! 🎮)

One-click deployment of Minecraft modpacks with automatic setup:

### Supported Sources
- **CurseForge** - Largest modpack library (10,000+ packs)
- **Modrinth** - Modern, open-source focused
- **FTB** - Official Feed The Beast packs

### Features
- 🔍 Search across multiple sources
- 📦 Automatic file downloading
- 🚀 One-click server deployment
- ⚙️ Auto-configuration (EULA, server.properties)
- 📊 Real-time progress tracking

### How It Works
1. Select Minecraft template (Forge/NeoForge/Fabric)
2. Browse available modpacks
3. Choose modpack and version
4. Enter container name and subdomain
5. System automatically downloads, installs, and configures
6. Server ready in 2-5 minutes!

**See:** `documentation/MODPACK_AUTOMATION_PLAN.md` for full details

## Documentation

All project documentation is organized in the `documentation/` folder:

- **MODPACK_AUTOMATION_PLAN.md** - Complete modpack feature specification
- **MODPACK_FEATURE_SUMMARY.md** - Implementation status and next steps
- **GETTING_STARTED.md** - Quick start guide
- **TEMPLATE_SYSTEM_PLAN.md** - Template system architecture
- **DASHBOARD_GUIDE.md** - Dashboard usage guide
- And more...

## Roadmap

### Completed ✅
- [x] Core container management functionality
- [x] Modal-based container creation UI
- [x] GraphQL API foundation
- [x] Container templates system (13 templates)
- [x] Modpack service backend (Phase 1)

### In Progress 🚧
- [ ] Modpack frontend integration
- [ ] GraphQL resolver implementation
- [ ] WebSocket progress tracking

### Planned 📋
- [ ] Multi-user support
- [ ] Resource monitoring dashboard
- [ ] Backup and restore functionality
- [ ] Auto-update system for modpacks
- [ ] Custom modpack upload
- [ ] Performance optimization

## Contributing

This is an academic project, but suggestions and feedback are welcome!

## License

[To be determined]

## Author

Erik Kjær Klint  
Aarhus University  
EH5ASU1 - Avanceret Softwareudvikling 1

## Acknowledgments

- Course instructors and materials
- Docker and Traefik communities
- WebAssembly and Pyodide projects
