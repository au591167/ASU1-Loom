# Backend Implementation - ASU1-Loom 🔧

## Slide 10: Backend Architecture

### Backend Component Overview

```
backend/
├── main.py                 # Application entry point
├── api/
│   └── schema.py          # GraphQL schema & resolvers
├── services/
│   ├── docker_manager.py  # Docker operations
│   └── modpack_service.py # Modpack automation
├── models/
│   ├── container.py       # Database models
│   └── user.py
├── database/
│   └── connection.py      # DB connection & sessions
└── config/
    └── settings.py        # Configuration management
```

**Speaker Notes:**
- Clean separation of concerns
- Services layer for business logic
- Models for data structure
- API layer for external communication

---

## Slide 11: FastAPI + GraphQL Setup

### Application Entry Point

**📍 File:** `backend/main.py` (lines 1-80)

```python
"""
ASU1-Loom Backend Server
Main entry point for the FastAPI application with GraphQL endpoint
"""

import asyncio
import sys
import platform
from contextlib import asynccontextmanager

# Fix for Windows ProactorEventLoop incompatibility
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import strawberry
from strawberry.fastapi import GraphQLRouter
from loguru import logger

from config.settings import settings
from database.connection import engine, init_db
from api.schema import Query, Mutation


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting ASU1-Loom Backend Server...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API Host: {settings.API_HOST}:{settings.API_PORT}")

    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

    logger.info("ASU1-Loom Backend Server started successfully")

    yield

    # Shutdown
    logger.info("Shutting down ASU1-Loom Backend Server...")
    engine.dispose()
    logger.info("Cleanup completed")


# Create FastAPI application
app = FastAPI(
    title="ASU1-Loom API",
    description="Hybrid Container Orchestration Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create GraphQL schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

# Create GraphQL router
graphql_app = GraphQLRouter(schema)

# Mount GraphQL endpoint
app.include_router(graphql_app, prefix="/graphql")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "loom-backend",
        "version": "1.0.0",
    }
```

**Key Points:**
1. **Lifespan Management:** Async context manager for startup/shutdown
2. **CORS Configuration:** Allows frontend communication
3. **GraphQL Integration:** Single endpoint for all API operations
4. **Health Checks:** Monitoring endpoint for load balancers

**Speaker Notes:**
- FastAPI's lifespan events håndterer initialization
- CORS er kritisk for browser-based frontend
- GraphQL router mounted på /graphql
- Health endpoint bruges af Traefik

---

## Slide 12: GraphQL Schema & Resolvers

### Type Definitions

**📍 File:** `backend/api/schema.py` (lines 1-100)

```python
import strawberry
from typing import List, Optional
from datetime import datetime
from loguru import logger

from services.docker_manager import DockerManager
from database.connection import get_db
from models.container import Container as ContainerModel


@strawberry.type
class Container:
    """GraphQL type for Container"""
    id: str
    name: str
    image: str
    tag: str
    subdomain: Optional[str]
    internal_port: int
    status: str
    created_at: str
    updated_at: Optional[str]


@strawberry.type
class ContainerStats:
    """Container resource statistics"""
    cpu_usage: float
    memory_usage: float
    network_rx: int
    network_tx: int


@strawberry.type
class Query:
    """GraphQL Query operations"""
    
    @strawberry.field
    async def containers(self) -> List[Container]:
        """Get all containers from database"""
        async with get_db() as session:
            result = await session.execute(
                select(ContainerModel)
            )
            containers = result.scalars().all()
            
            return [
                Container(
                    id=c.id,
                    name=c.name,
                    image=c.image,
                    tag=c.tag,
                    subdomain=c.subdomain,
                    internal_port=c.internal_port,
                    status=c.status,
                    created_at=c.created_at.isoformat(),
                    updated_at=c.updated_at.isoformat() if c.updated_at else None
                )
                for c in containers
            ]
    
    @strawberry.field
    async def container(self, id: str) -> Optional[Container]:
        """Get single container by ID"""
        async with get_db() as session:
            result = await session.execute(
                select(ContainerModel).where(ContainerModel.id == id)
            )
            container = result.scalar_one_or_none()
            
            if not container:
                return None
            
            return Container(
                id=container.id,
                name=container.name,
                image=container.image,
                tag=container.tag,
                subdomain=container.subdomain,
                internal_port=container.internal_port,
                status=container.status,
                created_at=container.created_at.isoformat(),
                updated_at=container.updated_at.isoformat() if container.updated_at else None
            )


@strawberry.type
class Mutation:
    """GraphQL Mutation operations"""
    
    @strawberry.mutation
    async def create_container(
        self,
        name: str,
        image: str,
        tag: str = "latest",
        subdomain: Optional[str] = None,
        internal_port: int = 80,
        environment: Optional[List[str]] = None
    ) -> Container:
        """Create a new container"""
        
        docker_manager = DockerManager()
        
        # Create container via Docker
        container_id = await docker_manager.create_container(
            name=name,
            image=image,
            tag=tag,
            subdomain=subdomain,
            port=internal_port,
            environment=environment or []
        )
        
        # Save to database
        async with get_db() as session:
            db_container = ContainerModel(
                id=container_id,
                name=name,
                image=image,
                tag=tag,
                subdomain=subdomain,
                internal_port=internal_port,
                status="created",
                created_at=datetime.utcnow()
            )
            session.add(db_container)
            await session.commit()
            await session.refresh(db_container)
            
            return Container(
                id=db_container.id,
                name=db_container.name,
                image=db_container.image,
                tag=db_container.tag,
                subdomain=db_container.subdomain,
                internal_port=db_container.internal_port,
                status=db_container.status,
                created_at=db_container.created_at.isoformat(),
                updated_at=None
            )
    
    @strawberry.mutation
    async def start_container(self, id: str) -> Container:
        """Start a container"""
        docker_manager = DockerManager()
        await docker_manager.start_container(id)
        
        # Update database
        async with get_db() as session:
            result = await session.execute(
                select(ContainerModel).where(ContainerModel.id == id)
            )
            container = result.scalar_one()
            container.status = "running"
            container.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(container)
            
            return Container(
                id=container.id,
                name=container.name,
                image=container.image,
                tag=container.tag,
                subdomain=container.subdomain,
                internal_port=container.internal_port,
                status=container.status,
                created_at=container.created_at.isoformat(),
                updated_at=container.updated_at.isoformat()
            )
```

**Key Concepts:**

1. **Type Safety:** Strawberry decorators provide type checking
2. **Async Operations:** All resolvers are async for non-blocking I/O
3. **Database Sessions:** Async context managers for proper cleanup
4. **Error Handling:** GraphQL automatically handles exceptions

**Speaker Notes:**
- GraphQL types mirror database models
- Resolvers er async for performance
- Database sessions håndteres korrekt med context managers
- Type safety både i Python og GraphQL schema

---

## Slide 13: Docker Integration

### Docker Manager Service

**📍 File:** `backend/services/docker_manager.py` (lines 1-150)

```python
import docker
import os
from typing import List, Dict, Optional
from loguru import logger


class DockerManager:
    """
    Service for managing Docker containers
    Handles container lifecycle and Traefik label generation
    """
    
    def __init__(self):
        """Initialize Docker client"""
        try:
            self.client = docker.from_env()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise
    
    def _generate_traefik_labels(
        self, 
        name: str, 
        subdomain: str, 
        port: int
    ) -> Dict[str, str]:
        """
        Generate Traefik labels for automatic routing
        
        Args:
            name: Container name
            subdomain: Subdomain for routing (e.g., 'game')
            port: Internal container port
            
        Returns:
            Dictionary of Traefik labels
        """
        # Get domain from environment (set in docker-compose.yml)
        domain = os.getenv('TRAEFIK_DOMAIN', 'localhost')
        full_domain = f"{subdomain}.{domain}"
        
        labels = {
            # Enable Traefik for this container
            'traefik.enable': 'true',
            
            # Router configuration
            f'traefik.http.routers.{name}.rule': f'Host(`{full_domain}`)',
            f'traefik.http.routers.{name}.entrypoints': 'web',
            
            # Service configuration
            f'traefik.http.services.{name}.loadbalancer.server.port': str(port),
        }
        
        logger.info(f"Generated Traefik labels for {name}: {full_domain}")
        return labels
    
    async def create_container(
        self,
        name: str,
        image: str,
        tag: str = "latest",
        subdomain: Optional[str] = None,
        port: int = 80,
        environment: List[str] = None
    ) -> str:
        """
        Create a new Docker container with Traefik labels
        
        Args:
            name: Container name
            image: Docker image name
            tag: Image tag (default: latest)
            subdomain: Subdomain for routing
            port: Internal port to expose
            environment: List of environment variables (KEY=VALUE format)
            
        Returns:
            Container ID
        """
        try:
            full_image = f"{image}:{tag}"
            logger.info(f"Creating container: {name} from {full_image}")
            
            # Generate Traefik labels if subdomain provided
            labels = {}
            if subdomain:
                labels = self._generate_traefik_labels(name, subdomain, port)
            
            # Parse environment variables
            env_dict = {}
            if environment:
                for env_var in environment:
                    if '=' in env_var:
                        key, value = env_var.split('=', 1)
                        env_dict[key] = value
            
            # Get network name from environment
            network = os.getenv('DOCKER_NETWORK', 'loom_network')
            
            # Create container
            container = self.client.containers.create(
                image=full_image,
                name=name,
                labels=labels,
                environment=env_dict,
                network=network,
                detach=True,
                # Resource limits (optional)
                mem_limit='512m',
                cpu_quota=50000,  # 50% of one CPU
            )
            
            logger.info(f"Container created successfully: {container.id[:12]}")
            return container.id
            
        except docker.errors.ImageNotFound:
            logger.error(f"Image not found: {full_image}")
            # Pull image and retry
            logger.info(f"Pulling image: {full_image}")
            self.client.images.pull(image, tag=tag)
            return await self.create_container(
                name, image, tag, subdomain, port, environment
            )
        except Exception as e:
            logger.error(f"Failed to create container: {e}")
            raise
    
    async def start_container(self, container_id: str) -> None:
        """Start a container"""
        try:
            container = self.client.containers.get(container_id)
            container.start()
            logger.info(f"Container started: {container_id[:12]}")
        except Exception as e:
            logger.error(f"Failed to start container: {e}")
            raise
    
    async def stop_container(self, container_id: str) -> None:
        """Stop a container"""
        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=10)
            logger.info(f"Container stopped: {container_id[:12]}")
        except Exception as e:
            logger.error(f"Failed to stop container: {e}")
            raise
    
    async def delete_container(self, container_id: str) -> None:
        """Delete a container"""
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=True)
            logger.info(f"Container deleted: {container_id[:12]}")
        except Exception as e:
            logger.error(f"Failed to delete container: {e}")
            raise
    
    async def get_container_stats(self, container_id: str) -> Dict:
        """Get container resource statistics"""
        try:
            container = self.client.containers.get(container_id)
            stats = container.stats(stream=False)
            
            # Calculate CPU percentage
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                          stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * 100.0
            
            # Calculate memory usage
            memory_usage = stats['memory_stats']['usage']
            memory_limit = stats['memory_stats']['limit']
            memory_percent = (memory_usage / memory_limit) * 100.0
            
            return {
                'cpu_usage': round(cpu_percent, 2),
                'memory_usage': round(memory_percent, 2),
                'network_rx': stats['networks']['eth0']['rx_bytes'],
                'network_tx': stats['networks']['eth0']['tx_bytes'],
            }
        except Exception as e:
            logger.error(f"Failed to get container stats: {e}")
            raise
```

**Key Implementation Details:**

1. **Traefik Label Generation:**
   - Reads `TRAEFIK_DOMAIN` from environment
   - Generates routing rules automatically
   - Configures load balancer port

2. **Error Handling:**
   - Automatic image pulling if not found
   - Graceful error logging
   - Exception propagation to GraphQL layer

3. **Resource Management:**
   - Memory limits (512MB default)
   - CPU quotas (50% of one core)
   - Network isolation

4. **Docker Socket Access:**
   - Direct communication with Docker daemon
   - Mounted via `/var/run/docker.sock`
   - Only backend container has access

**Speaker Notes:**
- Dette er hjertet i container management
- Traefik labels genereres automatisk baseret på subdomain
- Environment variable fra docker-compose bruges til domain
- Resource limits forhindrer en container i at overtage serveren

---

## Code Walkthrough Example

### Creating a Container - Step by Step

**1. Frontend sends GraphQL mutation:**
```graphql
mutation {
  createContainer(
    name: "game-2048",
    image: "alexwhen/docker-2048",
    subdomain: "game",
    internal_port: 80
  ) {
    id
    status
    subdomain
  }
}
```

**2. GraphQL resolver (schema.py) receives request:**
```python
@strawberry.mutation
async def create_container(self, name: str, image: str, ...) -> Container:
    docker_manager = DockerManager()
    container_id = await docker_manager.create_container(...)
```

**3. Docker Manager generates labels:**
```python
def _generate_traefik_labels(self, name, subdomain, port):
    domain = os.getenv('TRAEFIK_DOMAIN', 'localhost')  # 'pandaserver.ddns.net'
    full_domain = f"{subdomain}.{domain}"  # 'game.pandaserver.ddns.net'
    
    labels = {
        'traefik.enable': 'true',
        f'traefik.http.routers.{name}.rule': f'Host(`{full_domain}`)',
        f'traefik.http.services.{name}.loadbalancer.server.port': str(port),
    }
```

**4. Docker creates container:**
```python
container = self.client.containers.create(
    image='alexwhen/docker-2048:latest',
    name='game-2048',
    labels=labels,  # Traefik labels attached
    network='loom_network',
    detach=True
)
```

**5. Traefik detects new container:**
- Watches Docker socket for events
- Reads labels from container
- Configures route: `game.pandaserver.ddns.net` → `container:80`

**6. Database saves metadata:**
```python
db_container = ContainerModel(
    id=container_id,
    name='game-2048',
    image='alexwhen/docker-2048',
    subdomain='game',
    status='created'
)
session.add(db_container)
await session.commit()
```

**7. Response sent to frontend:**
```json
{
  "data": {
    "createContainer": {
      "id": "abc123...",
      "status": "created",
      "subdomain": "game"
    }
  }
}
```

**Speaker Notes:**
- Hele processen er async - ingen blocking
- Fejl på ethvert trin propageres tilbage til frontend
- Database og Docker holdes synkroniseret
- Traefik opdager automatisk uden vores indblanding

---

## PowerPoint Tips for This Section

### Slide Design:
- **Slide 10:** Component diagram with file structure
- **Slide 11:** Code snippet with syntax highlighting
- **Slide 12:** Split screen - GraphQL schema + resolver
- **Slide 13:** Docker Manager code with annotations

### Animations:
- Code appears line-by-line during explanation
- Highlight key lines (labels generation, async calls)
- Flow diagram for container creation

### Code Formatting:
- Use monospace font (Consolas, Courier New)
- Syntax highlighting (copy from VS Code)
- Line numbers for reference
- Comments in different color

### Timing:
- Slide 10: 30 seconds (overview)
- Slide 11: 60 seconds (FastAPI setup)
- Slide 12: 60 seconds (GraphQL)
- Slide 13: 60 seconds (Docker Manager)
- **Total: 3-4 minutes**

---

## Key Messages

1. **Clean Architecture:** "Separation of concerns - hver fil har ét ansvar"
2. **Async Everything:** "Non-blocking I/O for bedre performance"
3. **Type Safety:** "Python type hints + GraphQL schema = fewer bugs"
4. **Automation:** "Traefik labels genereres automatisk - ingen manuel config"

---

## Potential Questions & Answers

**Q: "Hvorfor async i stedet for sync?"**
A: "Async tillader serveren at håndtere multiple requests samtidig uden blocking. Når vi venter på Docker API eller database, kan andre requests behandles."

**Q: "Hvad hvis Docker socket ikke er tilgængelig?"**
A: "Docker client initialization fejler ved startup, og serveren starter ikke. Dette er by design - systemet kan ikke fungere uden Docker."

**Q: "Hvordan håndterer du container name conflicts?"**
A: "Docker returnerer en fejl hvis navnet allerede eksisterer. GraphQL propagerer denne fejl til frontend, som viser en brugervenlig besked."

**Q: "Kan brugere få adgang til andre containers?"**
A: "Nej, containers er isolerede via Docker networks. Kun Traefik kan route til dem baseret på subdomain."

---

## Transition to Next Section

**Say:**
> "Nu har vi set backend implementeringen - hvordan vi håndterer containers og API. Lad os se på frontend siden - hvordan brugeren interagerer med systemet..."

**Next:** Slide 14 - Frontend Implementation
