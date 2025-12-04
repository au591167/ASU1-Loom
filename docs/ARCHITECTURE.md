# ASU1-Loom Architecture

## Overview

ASU1-Loom is a hybrid container orchestration platform that combines modern WebAssembly-based frontend with a robust Python backend for managing Docker containers with automatic subdomain routing via Traefik.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Browser                           │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         WebAssembly Frontend (Pyodide)                    │  │
│  │  - HTML5/CSS3/JavaScript                                  │  │
│  │  - GraphQL Client                                         │  │
│  │  - Real-time UI Updates                                   │  │
│  └───────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │ GraphQL over HTTP
                            │
┌───────────────────────────┴─────────────────────────────────────┐
│                      Backend Server                              │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              FastAPI Application                         │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │   GraphQL    │  │   Docker     │  │  Database    │  │   │
│  │  │     API      │  │   Manager    │  │   Layer      │  │   │
│  │  │ (Strawberry) │  │  (SDK)       │  │ (SQLAlchemy) │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  │         │                  │                  │          │   │
│  │         └──────────────────┴──────────────────┘          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐  ┌──────────────────┐  ┌──────────────┐
│   PostgreSQL  │  │  Docker Engine   │  │   Traefik    │
│   Database    │  │                  │  │ Reverse Proxy│
│               │  │  ┌────────────┐  │  │              │
│  - Containers │  │  │ Container  │  │  │ - Routing    │
│  - Users      │  │  │ Container  │  │  │ - SSL/TLS    │
│  - Metadata   │  │  │ Container  │  │  │ - Dashboard  │
└───────────────┘  │  └────────────┘  │  └──────────────┘
                   └──────────────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │  User Containers │
                   │  - Web Apps      │
                   │  - Game Servers  │
                   │  - Databases     │
                   │  - Services      │
                   └──────────────────┘
```

## Component Details

### 1. Frontend (WebAssembly)

**Technology Stack:**
- HTML5, CSS3, JavaScript
- Pyodide (Python in browser via WASM)
- GraphQL Client

**Responsibilities:**
- User interface rendering
- GraphQL API communication
- Real-time status updates
- Form validation
- Client-side state management

**Key Features:**
- Lightweight and fast
- No server-side rendering needed
- Portable across platforms
- Low resource consumption

### 2. Backend (FastAPI + Python)

**Technology Stack:**
- FastAPI (async web framework)
- Strawberry GraphQL
- Docker SDK for Python
- SQLAlchemy ORM
- Uvicorn (ASGI server)

**Responsibilities:**
- GraphQL API endpoint
- Container lifecycle management
- Database operations
- Authentication & authorization
- Business logic

**Key Components:**

#### a. GraphQL API (`api/schema.py`)
- Query resolvers for data retrieval
- Mutation resolvers for data modification
- Type definitions
- Input validation

#### b. Docker Manager (`services/docker_manager.py`)
- Container creation
- Container start/stop/restart
- Container deletion
- Statistics collection
- Image management
- Network configuration

#### c. Database Layer (`database/`)
- Connection management
- Session handling
- Model definitions
- Migrations (Alembic)

#### d. Models (`models/`)
- Container model
- User model
- Relationships
- Validation

### 3. Database (PostgreSQL)

**Location:** External server (pandaserver.ddns.net / 4.20.69.11)

**Schema:**

```sql
-- Containers Table
containers (
    id SERIAL PRIMARY KEY,
    container_id VARCHAR(64) UNIQUE,
    name VARCHAR(255) UNIQUE NOT NULL,
    image VARCHAR(255) NOT NULL,
    tag VARCHAR(50) DEFAULT 'latest',
    subdomain VARCHAR(255) UNIQUE NOT NULL,
    internal_port INTEGER NOT NULL,
    external_port INTEGER,
    environment_vars JSON,
    volumes JSON,
    command TEXT,
    memory_limit VARCHAR(20),
    cpu_limit VARCHAR(20),
    status VARCHAR(50) DEFAULT 'created',
    restart_policy VARCHAR(50) DEFAULT 'unless-stopped',
    description TEXT,
    labels JSON,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    stopped_at TIMESTAMP WITH TIME ZONE,
    user_id INTEGER
)

-- Users Table
users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
)
```

### 4. Docker Engine

**Responsibilities:**
- Container runtime
- Image management
- Network management
- Volume management
- Resource allocation

**Integration:**
- Accessed via Docker SDK
- Unix socket communication
- Container labels for Traefik

### 5. Traefik Reverse Proxy

**Responsibilities:**
- Automatic subdomain routing
- SSL/TLS termination (optional)
- Load balancing
- Service discovery
- Dashboard

**Configuration:**
- Static config: `traefik.yml`
- Dynamic config: Docker labels
- Automatic certificate management (Let's Encrypt)

**Routing Example:**
```
myapp.pandaserver.ddns.net → Container "myapp" on port 80
```

## Data Flow

### Creating a Container

1. **User Input** → Frontend form
2. **GraphQL Mutation** → Backend API
3. **Validation** → Input validation
4. **Docker Operation** → Pull image, create container
5. **Database Record** → Store metadata
6. **Traefik Configuration** → Automatic via labels
7. **Response** → Success/failure to frontend
8. **UI Update** → Display new container

### Starting a Container

1. **User Action** → Click "Start" button
2. **GraphQL Mutation** → `startContainer(id)`
3. **Docker Command** → `container.start()`
4. **Database Update** → Update status, started_at
5. **Response** → Updated container info
6. **UI Update** → Show "running" status

## Asynchronous Operations

The system uses Python's `asyncio` for concurrent operations:

```python
# Example: Concurrent container operations
async def create_and_start_container(data):
    # Create container (async)
    container = await docker_manager.create_container(**data)
    
    # Save to database (async)
    db_container = await save_to_database(container)
    
    # Start container (async)
    await docker_manager.start_container(container.id)
    
    return db_container
```

## Security Considerations

1. **Authentication**: JWT-based (planned)
2. **Authorization**: Role-based access control
3. **Input Validation**: GraphQL schema + Pydantic
4. **Docker Socket**: Restricted access
5. **Database**: Parameterized queries (SQLAlchemy)
6. **CORS**: Configured origins only
7. **Secrets**: Environment variables

## Scalability

### Horizontal Scaling
- Multiple backend instances behind load balancer
- Shared PostgreSQL database
- Docker Swarm for container orchestration

### Vertical Scaling
- Increase backend resources
- Database optimization
- Connection pooling

## Monitoring & Logging

1. **Application Logs**: Loguru
2. **Container Stats**: Docker API
3. **System Metrics**: Docker info
4. **Traefik Logs**: Access logs
5. **Database Logs**: PostgreSQL logs

## Technology Choices Rationale

### Why FastAPI?
- Modern async framework
- Automatic API documentation
- High performance
- Type hints support
- Easy GraphQL integration

### Why GraphQL?
- Flexible data fetching
- Single endpoint
- Type safety
- Real-time capabilities
- Better than REST for complex queries

### Why WebAssembly?
- High performance
- Portable
- Secure sandbox
- Python in browser (Pyodide)
- Low overhead

### Why Traefik?
- Automatic service discovery
- Docker integration
- Dynamic configuration
- Let's Encrypt support
- Modern and actively maintained

### Why PostgreSQL?
- Robust and reliable
- JSON support
- Full-text search
- Excellent performance
- Wide adoption

## Future Enhancements

1. **Multi-user Support**: Complete authentication system
2. **Container Templates**: Pre-configured setups
3. **Resource Monitoring**: Real-time graphs
4. **Backup/Restore**: Container state management
5. **CI/CD Integration**: Automated deployments
6. **Kubernetes Support**: Alternative to Docker Swarm
7. **WebSocket Support**: Real-time updates
8. **Container Logs**: Live log streaming
9. **Health Checks**: Automatic monitoring
10. **Cost Tracking**: Resource usage analytics

## Academic Context

This architecture demonstrates key concepts from **EH5ASU1 - Avanceret Softwareudvikling 1**:

- ✅ **GUI**: WebAssembly-based interface
- ✅ **Async Programming**: FastAPI + asyncio
- ✅ **Threading**: Concurrent operations
- ✅ **ORM**: SQLAlchemy
- ✅ **GraphQL**: Modern API design
- ✅ **Scalable Architecture**: Microservices-ready
- ✅ **Container Orchestration**: Docker management
- ✅ **Reverse Proxy**: Traefik integration
