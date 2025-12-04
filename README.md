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
│   ├── services/        # Business logic
│   ├── docker_manager/  # Docker integration
│   └── config/          # Configuration files
├── frontend/            # WASM-based GUI
│   ├── src/            # Source files
│   ├── assets/         # Static assets
│   └── build/          # Compiled WASM modules
├── infrastructure/      # Docker & Traefik configs
│   ├── docker/         # Dockerfiles
│   ├── traefik/        # Traefik configuration
│   └── compose/        # Docker Compose files
├── database/           # Database schemas & migrations
├── docs/              # Documentation
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

# Set up database
python scripts/init_db.py

# Start infrastructure
docker-compose up -d

# Run backend server
python main.py
```

### Configuration

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/loom
DOCKER_HOST=unix:///var/run/docker.sock
TRAEFIK_DOMAIN=yourdomain.com
API_PORT=8000
```

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

## Roadmap

- [ ] Core container management functionality
- [ ] WASM GUI implementation
- [ ] GraphQL API development
- [ ] Traefik integration
- [ ] Multi-user support
- [ ] Resource monitoring
- [ ] Container templates library
- [ ] Backup and restore functionality
- [ ] Security hardening
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
