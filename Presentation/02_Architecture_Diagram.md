# Architecture Diagrams - ASU1-Loom 🏗️

## System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    User's Web Browser                           │ │
│  │  ┌──────────────────────────────────────────────────────────┐  │ │
│  │  │         WebAssembly Frontend (Pyodide)                    │  │ │
│  │  │  • index.html - Main page structure                       │  │ │
│  │  │  • app.js - Application logic & API calls                 │  │ │
│  │  │  • templates.js - UI component templates                  │  │ │
│  │  │  • styles.css - Styling and layout                        │  │ │
│  │  └──────────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            │ HTTP/HTTPS
                            │ GraphQL Queries/Mutations
                            │
┌───────────────────────────┴─────────────────────────────────────────┐
│                    REVERSE PROXY LAYER                               │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │              Traefik v2.11 (Reverse Proxy)                     │ │
│  │                                                                 │ │
│  │  Responsibilities:                                             │ │
│  │  • Automatic service discovery via Docker labels               │ │
│  │  • Dynamic routing: *.pandaserver.ddns.net                    │ │
│  │  • Load balancing across containers                           │ │
│  │  • Health checks and failover                                 │ │
│  │  • SSL/TLS termination (future)                               │ │
│  │                                                                 │ │
│  │  Routing Rules:                                                │ │
│  │  • pandaserver.ddns.net → Frontend (nginx)                    │ │
│  │  • pandaserver.ddns.net/graphql → Backend API                 │ │
│  │  • game.pandaserver.ddns.net → User Container (game-2048)     │ │
│  │  • grafana.pandaserver.ddns.net → User Container (grafana)    │ │
│  └────────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
┌───────┴──────────┐                 ┌─────────┴────────────────────────┐
│  FRONTEND        │                 │      BACKEND LAYER                │
│  CONTAINER       │                 │                                   │
│                  │                 │  ┌─────────────────────────────┐ │
│  ┌────────────┐  │                 │  │   FastAPI Application       │ │
│  │   Nginx    │  │                 │  │   (main.py)                 │ │
│  │   Alpine   │  │                 │  │                             │ │
│  │            │  │                 │  │  • GraphQL endpoint         │ │
│  │  Serves:   │  │                 │  │  • Health checks            │ │
│  │  - HTML    │  │                 │  │  • CORS middleware          │ │
│  │  - JS      │  │                 │  │  • Logging                  │ │
│  │  - CSS     │  │                 │  │                             │ │
│  │  - WASM    │  │                 │  │  Port: 8000                 │ │
│  │            │  │                 │  └──────────┬──────────────────┘ │
│  │  Port: 80  │  │                 │             │                    │
│  └────────────┘  │                 │  ┌──────────┴──────────────────┐ │
└──────────────────┘                 │  │   Services Layer            │ │
                                     │  │                             │ │
                                     │  │  • docker_manager.py        │ │
                                     │  │    - Container lifecycle    │ │
                                     │  │    - Traefik label gen      │ │
                                     │  │    - Resource management    │ │
                                     │  │                             │ │
                                     │  │  • modpack_service.py       │ │
                                     │  │    - CurseForge API         │ │
                                     │  │    - Modrinth API           │ │
                                     │  │    - FTB integration        │ │
                                     │  └──────────┬──────────────────┘ │
                                     │             │                    │
                                     │  ┌──────────┴──────────────────┐ │
                                     │  │   Database Layer            │ │
                                     │  │                             │ │
                                     │  │  • PostgreSQL 15+           │ │
                                     │  │  • SQLAlchemy ORM           │ │
                                     │  │  • Async sessions           │ │
                                     │  │                             │ │
                                     │  │  Models:                    │ │
                                     │  │  - User                     │ │
                                     │  │  - Container                │ │
                                     │  │                             │ │
                                     │  │  Port: 5432                 │ │
                                     │  └─────────────────────────────┘ │
                                     └──────────┬────────────────────────┘
                                                │
                                                │ Docker Socket
                                                │ /var/run/docker.sock
┌───────────────────────────────────────────────┴──────────────────────────┐
│                      CONTAINER RUNTIME LAYER                              │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │                       Docker Engine                               │    │
│  │                                                                    │    │
│  │  Network: loom_network (bridge)                                  │    │
│  │                                                                    │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │    │
│  │  │ User         │  │ User         │  │ User         │           │    │
│  │  │ Container 1  │  │ Container 2  │  │ Container 3  │  ...      │    │
│  │  │              │  │              │  │              │           │    │
│  │  │ game-2048    │  │ grafana      │  │ minecraft    │           │    │
│  │  │              │  │              │  │              │           │    │
│  │  │ Labels:      │  │ Labels:      │  │ Labels:      │           │    │
│  │  │ traefik.     │  │ traefik.     │  │ traefik.     │           │    │
│  │  │ enable=true  │  │ enable=true  │  │ enable=true  │           │    │
│  │  │              │  │              │  │              │           │    │
│  │  │ Host:        │  │ Host:        │  │ Host:        │           │    │
│  │  │ game.        │  │ grafana.     │  │ mc.          │           │    │
│  │  │ pandaserver  │  │ pandaserver  │  │ pandaserver  │           │    │
│  │  │ .ddns.net    │  │ .ddns.net    │  │ .ddns.net    │           │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘           │    │
│  └──────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### Container Creation Flow

```
┌─────────────┐
│    USER     │
│  (Browser)  │
└──────┬──────┘
       │
       │ 1. Fills form and clicks "Create"
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  FRONTEND (app.js)                                       │
│                                                           │
│  createContainer({                                       │
│    name: "game-2048",                                    │
│    image: "alexwhen/docker-2048",                        │
│    subdomain: "game",                                    │
│    port: 80                                              │
│  })                                                      │
└──────┬───────────────────────────────────────────────────┘
       │
       │ 2. GraphQL Mutation
       │    POST /graphql
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  NGINX (Reverse Proxy)                                   │
│                                                           │
│  location /graphql {                                     │
│    proxy_pass http://backend:8000/graphql;              │
│  }                                                       │
└──────┬───────────────────────────────────────────────────┘
       │
       │ 3. Proxied request
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  BACKEND (schema.py)                                     │
│                                                           │
│  @strawberry.mutation                                    │
│  async def create_container(...) -> Container:           │
│    docker_manager = DockerManager()                      │
│    container_id = await docker_manager.create_container()│
└──────┬───────────────────────────────────────────────────┘
       │
       │ 4. Call Docker Manager
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  DOCKER MANAGER (docker_manager.py)                      │
│                                                           │
│  def _generate_traefik_labels():                         │
│    domain = os.getenv('TRAEFIK_DOMAIN')                 │
│    # 'pandaserver.ddns.net'                             │
│                                                           │
│    labels = {                                            │
│      'traefik.enable': 'true',                          │
│      'traefik.http.routers.game-2048.rule':             │
│        'Host(`game.pandaserver.ddns.net`)',             │
│      'traefik.http.services.game-2048.loadbalancer      │
│        .server.port': '80'                              │
│    }                                                     │
└──────┬───────────────────────────────────────────────────┘
       │
       │ 5. Create container with labels
       │    via Docker Socket
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  DOCKER ENGINE                                           │
│                                                           │
│  docker.containers.create(                               │
│    image='alexwhen/docker-2048:latest',                 │
│    name='game-2048',                                     │
│    labels=traefik_labels,                               │
│    network='loom_network'                               │
│  )                                                       │
└──────┬───────────────────────────────────────────────────┘
       │
       │ 6. Container created
       │    Returns container_id
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  DATABASE (PostgreSQL)                                   │
│                                                           │
│  INSERT INTO containers (                                │
│    id, name, image, subdomain, status, created_at       │
│  ) VALUES (                                              │
│    'abc123...', 'game-2048',                            │
│    'alexwhen/docker-2048', 'game',                      │
│    'created', NOW()                                      │
│  )                                                       │
└──────┬───────────────────────────────────────────────────┘
       │
       │ 7. Metadata saved
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  TRAEFIK (Automatic Discovery)                           │
│                                                           │
│  • Watches Docker socket for events                      │
│  • Detects new container: game-2048                      │
│  • Reads labels from container                           │
│  • Configures route:                                     │
│    game.pandaserver.ddns.net → container:80             │
│  • Updates routing table                                 │
└──────┬───────────────────────────────────────────────────┘
       │
       │ 8. Response sent back
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  FRONTEND (app.js)                                       │
│                                                           │
│  • Receives container object                             │
│  • Updates UI state                                      │
│  • Re-renders container list                             │
│  • Shows success message                                 │
│  • Displays clickable link:                              │
│    http://game.pandaserver.ddns.net                     │
└───────────────────────────────────────────────────────────┘
```

**Total Time:** ~15-30 seconds (depending on image pull)

---

## Network Architecture

### Docker Network Topology

```
┌─────────────────────────────────────────────────────────────┐
│  Host Network (pandaserver.ddns.net - 85.24.3.105)         │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  loom_network (Docker Bridge Network)                  │ │
│  │  Subnet: 172.18.0.0/16                                 │ │
│  │                                                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │ │
│  │  │   Traefik    │  │   Backend    │  │   Frontend   │ │ │
│  │  │              │  │              │  │              │ │ │
│  │  │ 172.18.0.2   │  │ 172.18.0.3   │  │ 172.18.0.4   │ │ │
│  │  │              │  │              │  │              │ │ │
│  │  │ Ports:       │  │ Ports:       │  │ Ports:       │ │ │
│  │  │ 80 → Host    │  │ 8000 → Host  │  │ 3000 → Host  │ │ │
│  │  │ 443 → Host   │  │              │  │              │ │ │
│  │  │ 8080 → Host  │  │              │  │              │ │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │ │
│  │         │                 │                 │          │ │
│  │         └─────────────────┴─────────────────┘          │ │
│  │                           │                             │ │
│  │  ┌────────────────────────┴──────────────────────────┐ │ │
│  │  │                                                    │ │ │
│  │  │  User Containers (Dynamic)                        │ │ │
│  │  │                                                    │ │ │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐       │ │ │
│  │  │  │ game-    │  │ grafana  │  │ minecraft│  ...  │ │ │
│  │  │  │ 2048     │  │          │  │          │       │ │ │
│  │  │  │          │  │          │  │          │       │ │ │
│  │  │  │172.18.0.5│  │172.18.0.6│  │172.18.0.7│       │ │ │
│  │  │  │          │  │          │  │          │       │ │ │
│  │  │  │ Port: 80 │  │Port: 3000│  │Port:25565│       │ │ │
│  │  │  └──────────┘  └──────────┘  └──────────┘       │ │ │
│  │  └────────────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  External Access:                                             │
│  • Port 80 → Traefik → Routes to containers                  │
│  • Port 443 → Traefik → SSL termination (future)             │
│  • Port 8080 → Traefik Dashboard                             │
│  • Port 8000 → Backend API (direct access)                   │
│  • Port 3000 → Frontend (direct access)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Interaction Diagram

### Request Flow for Different Endpoints

```
USER REQUEST: http://pandaserver.ddns.net
│
├─> DNS Resolution: pandaserver.ddns.net → 85.24.3.105
│
└─> HTTP Request to Port 80
    │
    └─> Traefik (Port 80)
        │
        ├─> Checks routing rules
        │   Rule: Host(`pandaserver.ddns.net`)
        │
        └─> Routes to: frontend:80 (nginx)
            │
            └─> Nginx serves: /usr/share/nginx/html/index.html
                │
                └─> Browser receives HTML + JS + CSS


USER REQUEST: http://pandaserver.ddns.net/graphql
│
├─> DNS Resolution: pandaserver.ddns.net → 85.24.3.105
│
└─> HTTP POST to Port 80
    │
    └─> Traefik (Port 80)
        │
        ├─> Checks routing rules
        │   Rule: Host(`pandaserver.ddns.net`) && Path(`/graphql`)
        │
        └─> Routes to: backend:8000/graphql
            │
            └─> FastAPI GraphQL endpoint
                │
                ├─> Parses GraphQL query
                ├─> Executes resolver
                ├─> Queries database / calls Docker
                └─> Returns JSON response


USER REQUEST: http://game.pandaserver.ddns.net
│
├─> DNS Resolution: game.pandaserver.ddns.net → 85.24.3.105
│
└─> HTTP Request to Port 80
    │
    └─> Traefik (Port 80)
        │
        ├─> Checks routing rules
        │   Rule: Host(`game.pandaserver.ddns.net`)
        │
        ├─> Finds matching container: game-2048
        │   (via Docker labels)
        │
        └─> Routes to: game-2048:80
            │
            └─> User container serves application
                │
                └─> Browser receives game interface
```

---

## Technology Stack Layers

```
┌─────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER                                      │
│  • HTML5 - Structure                                    │
│  • CSS3 - Styling                                       │
│  • JavaScript (ES6+) - Logic                            │
│  • WebAssembly (Pyodide) - Python in browser            │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP/GraphQL
                     │
┌────────────────────┴────────────────────────────────────┐
│  API LAYER                                               │
│  • GraphQL (Strawberry) - API schema                    │
│  • FastAPI - Web framework                              │
│  • Uvicorn - ASGI server                                │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Function calls
                     │
┌────────────────────┴────────────────────────────────────┐
│  BUSINESS LOGIC LAYER                                    │
│  • docker_manager.py - Container operations             │
│  • modpack_service.py - Modpack automation              │
│  • Validation & error handling                          │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────┴──────────┐    ┌────────┴─────────┐
│  DATA LAYER      │    │  RUNTIME LAYER   │
│  • PostgreSQL    │    │  • Docker Engine │
│  • SQLAlchemy    │    │  • Containers    │
│  • Async sessions│    │  • Networks      │
└──────────────────┘    └──────────────────┘
```

---

## Deployment Architecture

### Production Server Layout

```
Server: pandaserver.ddns.net (85.24.3.105)
OS: Ubuntu Linux 22.04

/opt/loom/                          # Application root
├── docker-compose.yml              # Service orchestration
├── .env                            # Environment variables
├── backend/                        # Backend code
│   ├── main.py
│   ├── api/
│   ├── services/
│   ├── models/
│   └── database/
├── frontend/                       # Frontend code
│   ├── dist/
│   │   ├── index.html
│   │   ├── app.js
│   │   └── styles.css
│   ├── Dockerfile
│   └── nginx.conf
├── infrastructure/                 # Infrastructure config
│   └── traefik/
│       └── traefik.yml
└── logs/                          # Application logs
    └── loom.log

Docker Containers:
├── loom_traefik        (traefik:v2.11)
├── loom_backend        (custom build)
├── loom_frontend       (nginx:alpine)
└── user_containers     (various images)

Docker Networks:
└── loom_network        (bridge)

External Services:
├── No-IP DNS           (pandaserver.ddns.net)
└── Internet Router     (Port forwarding: 80, 443, 8000)
```

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│  EXTERNAL THREATS                                        │
│  • DDoS attacks                                         │
│  • SQL injection                                        │
│  • XSS attacks                                          │
│  • Unauthorized access                                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  FIREWALL (UFW)                                          │
│  • Allow: 80, 443, 8000                                 │
│  • Deny: All other ports                                │
│  • Rate limiting (future)                               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  TRAEFIK (Reverse Proxy)                                 │
│  • SSL/TLS termination (future)                         │
│  • Request filtering                                    │
│  • Rate limiting (future)                               │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────┐          ┌──────────────┐
│  FRONTEND    │          │  BACKEND     │
│  • CORS      │          │  • CORS      │
│  • CSP       │          │  • Input val │
│  • XSS prot  │          │  • Auth      │
└──────────────┘          └──────┬───────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
            ┌──────────────┐          ┌──────────────┐
            │  DATABASE    │          │  DOCKER      │
            │  • Encrypted │          │  • Isolated  │
            │  • Access    │          │  • Resource  │
            │    control   │          │    limits    │
            └──────────────┘          └──────────────┘
```

---

## Use These Diagrams in PowerPoint

### Tips for Presentation:

1. **Architecture Overview:**
   - Use as full-slide diagram
   - Animate layers appearing one by one
   - Explain each layer's purpose

2. **Data Flow:**
   - Show step-by-step with animations
   - Highlight current step
   - Use different colors for different types of data

3. **Network Topology:**
   - Useful for explaining Docker networking
   - Show how containers communicate
   - Explain port mapping

4. **Component Interaction:**
   - Great for explaining request routing
   - Show different paths for different URLs
   - Demonstrate Traefik's role

### Visual Enhancements:

- Use icons for each component
- Color-code different layers
- Add arrows to show data flow
- Include timing information
- Show error paths (dotted lines)

---

**These diagrams provide visual support for your technical explanations!**
