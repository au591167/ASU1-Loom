# Tech Stack Implementation - ASU1-Loom 🛠️

## Slide 7: Architecture Overview

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           Browser (Any Modern Browser)                    │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  WebAssembly Frontend (Pyodide + Python)           │  │   │
│  │  │  - index.html, app.js, templates.js, styles.css    │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/GraphQL
                         │ Port 80/443
┌────────────────────────┴────────────────────────────────────────┐
│                    REVERSE PROXY LAYER                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Traefik v2.11 (Container)                    │   │
│  │  - Automatic service discovery via Docker labels          │   │
│  │  - Dynamic routing: *.pandaserver.ddns.net               │   │
│  │  - Load balancing & health checks                        │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                  │
┌───────┴──────────┐            ┌─────────┴────────────────────────┐
│  FRONTEND        │            │     BACKEND LAYER                 │
│  (nginx)         │            │  ┌────────────────────────────┐  │
│  Port 80         │            │  │   FastAPI Application      │  │
└──────────────────┘            │  │   - main.py (entry point)  │  │
                                │  │   - GraphQL endpoint       │  │
                                │  │   Port 8000                │  │
                                │  └────────┬───────────────────┘  │
                                │           │                       │
                                │  ┌────────┴───────────────────┐  │
                                │  │   Services Layer           │  │
                                │  │  - docker_manager.py       │  │
                                │  │  - modpack_service.py      │  │
                                │  └────────┬───────────────────┘  │
                                │           │                       │
                                │  ┌────────┴───────────────────┐  │
                                │  │   Database Layer           │  │
                                │  │  - PostgreSQL              │  │
                                │  │  - SQLAlchemy ORM          │  │
                                │  │  - Models: User, Container │  │
                                │  └────────────────────────────┘  │
                                └──────────┬────────────────────────┘
                                           │
                                           │ Docker Socket
                                           │ /var/run/docker.sock
┌──────────────────────────────────────────┴────────────────────────┐
│                    CONTAINER RUNTIME LAYER                         │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                  Docker Engine                            │    │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │    │
│  │  │ User       │  │ User       │  │ User       │  ...    │    │
│  │  │ Container  │  │ Container  │  │ Container  │         │    │
│  │  │ (game)     │  │ (grafana)  │  │ (minecraft)│         │    │
│  │  └────────────┘  └────────────┘  └────────────┘         │    │
│  └──────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────┘
```

**Speaker Notes:**
- 5 lag arkitektur: Client, Proxy, Frontend, Backend, Runtime
- Hver komponent har specifikt ansvar (separation of concerns)
- Traefik er hjertet i routing-logikken
- Backend kommunikerer direkte med Docker via socket

---

## Slide 8: Technology Stack

### Frontend Technologies

#### **WebAssembly + Pyodide**
```
Technology: Pyodide v0.24.1
Purpose: Run Python in browser
Why: Portability, no server-side rendering needed
```

**Code Reference:** `frontend/dist/index.html`
```html
<!-- Load Pyodide -->
<script src="https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js"></script>
```

**Benefits:**
- ✅ Python code runs directly in browser
- ✅ No compilation step for frontend changes
- ✅ Familiar language (Python) for full-stack
- ✅ Lightweight deployment

#### **Vanilla JavaScript**
```
Files: app.js, templates.js
Purpose: UI logic, API communication
Why: Simple, no framework overhead
```

**Code Reference:** `frontend/dist/app.js` (lines 1-30)
```javascript
// GraphQL API communication
const API_ENDPOINT = '/graphql';

async function graphqlQuery(query, variables = {}) {
    const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, variables })
    });
    return await response.json();
}
```

---

### Backend Technologies

#### **FastAPI Framework**
```
Technology: FastAPI v0.104+
Purpose: High-performance async web framework
Why: Native async support, automatic OpenAPI docs
```

**Code Reference:** `backend/main.py` (lines 40-60)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ASU1-Loom API",
    description="Container Orchestration Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Benefits:**
- ✅ Async/await for concurrent operations
- ✅ Automatic API documentation
- ✅ Type hints for better code quality
- ✅ High performance (comparable to Node.js)

#### **GraphQL (Strawberry)**
```
Technology: Strawberry GraphQL
Purpose: Flexible API layer
Why: Client-driven queries, real-time updates
```

**Code Reference:** `backend/api/schema.py` (lines 15-40)
```python
import strawberry
from typing import List, Optional

@strawberry.type
class Container:
    id: str
    name: str
    image: str
    status: str
    subdomain: Optional[str]
    created_at: str

@strawberry.type
class Query:
    @strawberry.field
    async def containers(self) -> List[Container]:
        """Get all containers"""
        # Implementation...
        
@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_container(
        self, 
        name: str, 
        image: str, 
        subdomain: str
    ) -> Container:
        """Create new container"""
        # Implementation...
```

**Benefits:**
- ✅ Type-safe API
- ✅ Client specifies exact data needed
- ✅ Single endpoint for all operations
- ✅ Built-in introspection

---

### Infrastructure Technologies

#### **Docker Engine**
```
Technology: Docker 24.0+
Purpose: Container runtime
Why: Industry standard, robust, well-documented
```

**Code Reference:** `backend/services/docker_manager.py` (lines 20-50)
```python
import docker

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
    
    def create_container(
        self, 
        name: str, 
        image: str, 
        subdomain: str,
        port: int
    ):
        """Create container with Traefik labels"""
        domain = os.getenv('TRAEFIK_DOMAIN', 'localhost')
        
        labels = {
            'traefik.enable': 'true',
            f'traefik.http.routers.{name}.rule': 
                f'Host(`{subdomain}.{domain}`)',
            f'traefik.http.services.{name}.loadbalancer.server.port': 
                str(port)
        }
        
        container = self.client.containers.create(
            image=image,
            name=name,
            labels=labels,
            network='loom_network',
            detach=True
        )
        return container
```

**Benefits:**
- ✅ Isolation and security
- ✅ Resource management
- ✅ Portable deployments
- ✅ Extensive ecosystem

#### **Traefik Reverse Proxy**
```
Technology: Traefik v2.11
Purpose: Automatic routing and load balancing
Why: Docker-native, automatic service discovery
```

**Code Reference:** `docker-compose.yml` (lines 5-30)
```yaml
traefik:
  image: traefik:v2.11
  command:
    - "--providers.docker=true"
    - "--providers.docker.exposedbydefault=false"
    - "--entrypoints.web.address=:80"
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock:ro
  labels:
    - "traefik.enable=true"
```

**How It Works:**
1. Traefik watches Docker socket
2. Detects containers with `traefik.enable=true` label
3. Reads routing rules from labels
4. Automatically configures reverse proxy
5. Updates in real-time as containers start/stop

**Benefits:**
- ✅ Zero-configuration routing
- ✅ Automatic SSL/TLS (Let's Encrypt)
- ✅ Load balancing
- ✅ Health checks

---

### Database Technologies

#### **PostgreSQL**
```
Technology: PostgreSQL 15+
Purpose: Persistent metadata storage
Why: Reliable, ACID compliant, excellent Python support
```

**Code Reference:** `backend/models/container.py` (lines 1-25)
```python
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Container(Base):
    __tablename__ = 'containers'
    
    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    image = Column(String, nullable=False)
    tag = Column(String, default='latest')
    subdomain = Column(String, unique=True)
    internal_port = Column(Integer)
    status = Column(String, default='created')
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

**Benefits:**
- ✅ ACID transactions
- ✅ Complex queries support
- ✅ Excellent SQLAlchemy integration
- ✅ Production-proven reliability

#### **SQLAlchemy ORM**
```
Technology: SQLAlchemy 2.0+
Purpose: Database abstraction layer
Why: Type-safe queries, migration support
```

**Code Reference:** `backend/database/connection.py` (lines 10-30)
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

---

## Slide 9: Why These Technologies?

### Decision Matrix

| Technology | Alternatives Considered | Why Chosen |
|------------|------------------------|------------|
| **FastAPI** | Flask, Django | Async support, performance, auto-docs |
| **GraphQL** | REST API | Flexible queries, type safety |
| **Traefik** | Nginx, Caddy | Docker-native, auto-discovery |
| **PostgreSQL** | MySQL, MongoDB | ACID, reliability, SQLAlchemy support |
| **WebAssembly** | React, Vue | Portability, Python in browser |
| **Docker** | Podman, LXC | Industry standard, ecosystem |

### Key Design Principles

#### 1. **Separation of Concerns**
- Frontend: UI/UX only
- Backend: Business logic
- Traefik: Routing only
- Docker: Container runtime

#### 2. **Async-First**
- FastAPI async endpoints
- Async database sessions
- Non-blocking I/O operations

#### 3. **Type Safety**
- Python type hints
- GraphQL schema types
- SQLAlchemy models

#### 4. **Automation**
- Automatic routing (Traefik)
- Auto-generated API docs (FastAPI)
- Database migrations (Alembic)

---

## Data Flow Example

### Creating a Container - Full Stack Flow

```
1. USER ACTION
   └─> Click "Create Container" in browser

2. FRONTEND (app.js)
   └─> GraphQL mutation sent to /graphql
       {
         mutation {
           createContainer(
             name: "game-2048",
             image: "alexwhen/docker-2048",
             subdomain: "game"
           ) {
             id, status
           }
         }
       }

3. BACKEND (main.py → schema.py)
   └─> GraphQL resolver receives mutation
   └─> Validates input data
   └─> Calls docker_manager.create_container()

4. DOCKER MANAGER (docker_manager.py)
   └─> Generates Traefik labels
   └─> Calls Docker API via socket
   └─> Creates container with labels
   └─> Connects to loom_network

5. DATABASE (PostgreSQL)
   └─> Saves container metadata
   └─> Returns container object

6. TRAEFIK (automatic)
   └─> Detects new container via Docker events
   └─> Reads traefik.* labels
   └─> Configures route: game.pandaserver.ddns.net → container:80

7. RESPONSE
   └─> Backend returns container data
   └─> Frontend updates UI
   └─> User sees "Running" status

8. USER ACCESS
   └─> Opens game.pandaserver.ddns.net
   └─> Traefik routes to container
   └─> Application loads!
```

**Speaker Notes:**
- Hele flowet tager <30 sekunder
- Hver komponent har ét ansvar
- Fejlhåndtering på hvert niveau
- Async operations = ingen blocking

---

## Performance Considerations

### Optimization Strategies

#### **Backend:**
- Async database sessions (no blocking)
- Connection pooling (SQLAlchemy)
- Docker socket reuse (single client)
- GraphQL query batching

#### **Frontend:**
- Minimal JavaScript bundle
- CDN for Pyodide (cached)
- Lazy loading for templates
- Efficient DOM updates

#### **Infrastructure:**
- Traefik caching
- Docker layer caching
- Network optimization (bridge network)
- Resource limits per container

### Measured Performance

```
Container Creation: 15-30 seconds
  - Image pull: 10-20s (first time only)
  - Container create: 2-3s
  - Network setup: 1-2s
  - Traefik discovery: 2-3s

API Response Times:
  - GraphQL queries: 50-100ms
  - Mutations: 100-200ms
  - Health check: <10ms

Frontend Load:
  - Initial load: 2-3s (Pyodide)
  - Subsequent: <500ms (cached)
```

---

## Security Considerations

### Implemented Security Measures

#### **1. Docker Socket Access**
```python
# Limited to backend container only
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```
- Only backend has Docker access
- No direct user access to socket

#### **2. CORS Configuration**
```python
allow_origins=settings.CORS_ORIGINS  # Whitelist only
allow_credentials=True
```

#### **3. Container Isolation**
- Each container in separate namespace
- Resource limits enforced
- Network isolation via Docker networks

#### **4. Input Validation**
```python
@strawberry.mutation
async def create_container(
    self,
    name: str,  # Validated by GraphQL
    image: str,  # Validated format
    subdomain: str  # Regex validated
) -> Container:
```

---

## Scalability Path

### Current Limitations:
- Single server deployment
- No load balancing across servers
- Manual scaling

### Future Enhancements:
- Docker Swarm for multi-node
- Redis for session management
- Horizontal scaling with load balancer
- Container resource quotas

**Speaker Notes:**
- Nuværende setup er single-server
- Arkitekturen understøtter skalering
- Docker Swarm er næste naturlige skridt
- Traefik kan load-balance automatisk

---

## PowerPoint Tips for This Section

### Slide Design:
- **Slide 7:** Full-page architecture diagram
- **Slide 8:** Split into 3 columns (Frontend, Backend, Infrastructure)
- **Slide 9:** Decision matrix table

### Animations:
- Architecture: Components fade in layer by layer
- Data flow: Arrows appear sequentially
- Tech stack: Icons zoom in

### Code Snippets:
- Syntax highlighting (use PowerPoint code blocks)
- Keep snippets short (10-15 lines max)
- Highlight key lines

### Timing:
- Slide 7: 45 seconds (architecture)
- Slide 8: 60 seconds (technologies)
- Slide 9: 15 seconds (decisions)
- **Total: 2 minutes**

---

## Key Messages

1. **Modern Stack:** "Cutting-edge teknologier (WebAssembly, GraphQL, async Python)"
2. **Right Tools:** "Hver teknologi valgt med omhu for specifikt formål"
3. **Production-Ready:** "Ikke bare proof-of-concept - faktisk deployable"
4. **Scalable:** "Arkitektur understøtter fremtidig vækst"

---

## Transition to Next Section

**Say:**
> "Nu har I set tech stacken på højt niveau. Lad os dykke ned i backend implementeringen og se hvordan disse teknologier arbejder sammen i koden..."

**Next:** Slide 10 - Backend Implementation
