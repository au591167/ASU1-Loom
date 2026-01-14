# Challenges & Solutions - ASU1-Loom 🔧

## Slide 16: Technical Challenges Overcome

### Challenge 1: Subdomain Routing Not Working

#### **Problem:**
Containers created with wrong Traefik labels - using `localhost` instead of actual domain `pandaserver.ddns.net`

**Symptom:**
```
Expected: game.pandaserver.ddns.net
Actual:   game.localhost (doesn't resolve)
```

#### **Root Cause:**
Backend container didn't have access to `TRAEFIK_DOMAIN` environment variable

**Investigation Process:**
1. Checked container labels: `docker inspect game-2048`
2. Found: `traefik.http.routers.game-2048.rule=Host('game.localhost')`
3. Traced to `docker_manager.py`: `domain = os.getenv('TRAEFIK_DOMAIN', 'localhost')`
4. Realized: Environment variable not passed to backend container

#### **Solution:**

**📍 File:** `docker-compose.yml` (lines 30-35)

```yaml
backend:
  build:
    context: ./backend
  environment:
    DATABASE_URL: ${DATABASE_URL}
    DOCKER_HOST: ${DOCKER_HOST:-unix:///var/run/docker.sock}
    API_HOST: ${API_HOST:-0.0.0.0}
    API_PORT: ${API_PORT:-8000}
    SECRET_KEY: ${SECRET_KEY}
    TRAEFIK_DOMAIN: ${TRAEFIK_DOMAIN:-localhost}  # ✅ ADDED
    DOCKER_NETWORK: ${DOCKER_NETWORK:-loom_network}  # ✅ ADDED
```

**Result:**
- Backend now reads correct domain from environment
- Containers get proper labels: `Host('game.pandaserver.ddns.net')`
- Subdomain routing works perfectly

**What I Learned:**
- Always verify environment variables are passed to containers
- Docker Compose environment section is crucial for configuration
- Test with actual domain, not just localhost

**Speaker Notes:**
- Dette var den største udfordring i production deployment
- Tog flere timer at debugge
- Løsningen var simpel, men finding the root cause var svært
- Nu fungerer subdomain routing perfekt

---

### Challenge 2: DNS Wildcard Configuration

#### **Problem:**
Subdomains not resolving - DNS errors when accessing `game.pandaserver.ddns.net`

**Symptom:**
```
DNS_PROBE_FINISHED_NXDOMAIN
```

#### **Root Cause:**
No-IP free tier doesn't enable wildcard DNS by default

**Investigation:**
1. Tested main domain: `pandaserver.ddns.net` ✅ Works
2. Tested subdomain: `game.pandaserver.ddns.net` ❌ Fails
3. Checked DNS records: `nslookup game.pandaserver.ddns.net` → No record
4. Researched No-IP documentation → Found wildcard option

#### **Solution:**

**No-IP Configuration:**
1. Login to No-IP dashboard
2. Navigate to hostname settings
3. Enable "Wildcard" option
4. Wait for DNS propagation (5-10 minutes)

**Verification:**
```bash
# Test DNS resolution
nslookup game.pandaserver.ddns.net
# Should return: 85.24.3.105

nslookup test.pandaserver.ddns.net
# Should return: 85.24.3.105

# All subdomains now resolve to same IP
```

**Result:**
- All `*.pandaserver.ddns.net` subdomains resolve correctly
- Traefik can route based on subdomain
- No manual DNS records needed per container

**What I Learned:**
- DNS configuration is critical for subdomain routing
- Free tier services have limitations
- Always test DNS before assuming routing issues
- DNS propagation takes time - be patient

**Speaker Notes:**
- DNS er ofte overlooked men kritisk
- Wildcard DNS er essentiel for dynamic subdomains
- Propagation kan tage tid - ikke panic hvis det ikke virker med det samme

---

### Challenge 3: Frontend Serving Issues

#### **Problem:**
Webpage downloading instead of displaying when accessing dashboard

**Symptom:**
- Browser downloads file instead of rendering HTML
- Content-Type header incorrect

#### **Root Cause:**
Missing `dist/` directory in frontend container

**Investigation:**
1. Checked Dockerfile: `COPY dist/ /usr/share/nginx/html/`
2. Verified dist/ exists locally ✅
3. Checked nginx logs: File not found errors
4. Realized: dist/ not in git repository

#### **Solution:**

**Build Process:**
1. Ensure `frontend/dist/` directory exists
2. Contains: `index.html`, `app.js`, `templates.js`, `styles.css`
3. Dockerfile copies to nginx html directory
4. Nginx serves with correct MIME types

**📍 File:** `frontend/nginx.conf` (lines 10-15)

```nginx
http {
    include /etc/nginx/mime.types;  # ✅ Critical for correct Content-Type
    default_type application/octet-stream;
    
    # WASM MIME type
    types {
        application/wasm wasm;
    }
}
```

**Result:**
- HTML files served with `text/html` Content-Type
- JavaScript with `application/javascript`
- CSS with `text/css`
- Browser renders correctly

**What I Learned:**
- MIME types are critical for browser rendering
- Always include `/etc/nginx/mime.types`
- Verify file structure before building containers
- Test with actual browser, not just curl

**Speaker Notes:**
- Simpel fejl men svær at debugge
- MIME types er ofte glemt
- Nginx defaults er ikke altid korrekte

---

### Challenge 4: Docker Socket Permissions

#### **Problem:**
Backend couldn't communicate with Docker daemon - permission denied errors

**Symptom:**
```python
docker.errors.DockerException: Error while fetching server API version
```

#### **Root Cause:**
Docker socket requires specific permissions - not available by default in container

#### **Solution:**

**📍 File:** `docker-compose.yml` (lines 40-45)

```yaml
backend:
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock  # ✅ Mount socket
    - ./backend:/app
    - ./logs:/app/logs
```

**Additional Configuration:**
```bash
# On host server
sudo usermod -aG docker $USER  # Add user to docker group
sudo systemctl restart docker   # Restart Docker daemon
```

**Security Consideration:**
- Docker socket access = root access to host
- Only backend container has this access
- Frontend and user containers are isolated
- Production: Consider Docker-in-Docker or remote API

**Result:**
- Backend can create/manage containers
- Proper isolation maintained
- Security risk acknowledged and mitigated

**What I Learned:**
- Docker socket is powerful but dangerous
- Proper volume mounting is critical
- Security vs functionality tradeoff
- Document security implications

**Speaker Notes:**
- Docker socket access er nødvendig men risikabelt
- I production ville jeg overveje alternativer
- For dette projekt er risikoen acceptabel
- Isolation mellem containers er vigtig

---

### Challenge 5: Async Database Sessions

#### **Problem:**
Database connection errors and session leaks in async context

**Symptom:**
```
sqlalchemy.exc.InvalidRequestError: Session is already closed
```

#### **Root Cause:**
Improper async session management - sessions not properly closed

#### **Solution:**

**📍 File:** `backend/database/connection.py` (lines 20-30)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,  # ✅ Verify connections before use
    pool_recycle=3600,   # ✅ Recycle connections after 1 hour
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # ✅ Don't expire objects after commit
    autoflush=False,         # ✅ Manual flush control
)

# Dependency for FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()  # ✅ Always close
```

**Usage in GraphQL Resolvers:**
```python
@strawberry.mutation
async def create_container(self, name: str, ...) -> Container:
    async with get_db() as session:  # ✅ Context manager
        # Database operations
        db_container = ContainerModel(...)
        session.add(db_container)
        await session.commit()
        await session.refresh(db_container)
        return Container(...)
    # Session automatically closed here
```

**Result:**
- No more session leaks
- Proper transaction handling
- Automatic rollback on errors
- Connection pooling works correctly

**What I Learned:**
- Async database sessions need careful management
- Context managers are your friend
- Always close sessions in finally block
- Connection pooling prevents resource exhaustion

**Speaker Notes:**
- Async programming har sine udfordringer
- Proper resource management er kritisk
- Context managers gør det nemmere
- SQLAlchemy 2.0 async support er excellent

---

### Challenge 6: Production Deployment

#### **Problem:**
Development setup worked locally but failed on production server

**Issues:**
1. Different network configuration
2. Firewall blocking ports
3. DNS not configured
4. Environment variables missing

#### **Solution Process:**

**1. Network Configuration:**
```bash
# Create Docker network
docker network create loom_network

# Verify network
docker network inspect loom_network
```

**2. Firewall Setup:**
```bash
# Allow necessary ports
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000/tcp  # Backend API
sudo ufw enable
```

**3. Environment Variables:**
```bash
# Create .env file on server
cat > .env << EOF
TRAEFIK_DOMAIN=pandaserver.ddns.net
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/loom
SECRET_KEY=production-secret-key
DOCKER_NETWORK=loom_network
EOF
```

**4. DNS Configuration:**
- Configured No-IP dynamic DNS
- Enabled wildcard subdomains
- Verified resolution

**5. Docker Compose Adjustments:**
```yaml
# Production-specific settings
services:
  backend:
    restart: unless-stopped  # ✅ Auto-restart
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Result:**
- System runs reliably on production server
- Automatic restarts on failure
- Proper logging and monitoring
- Secure configuration

**What I Learned:**
- Development ≠ Production
- Always test on target environment
- Document deployment process
- Automation prevents errors

**Speaker Notes:**
- Production deployment er altid udfordrende
- Mange små detaljer skal være korrekte
- Documentation er kritisk
- Nu kører systemet stabilt

---

## Slide 17: Lessons Learned

### Technical Lessons

#### **1. Environment Configuration is Critical**
- Always pass necessary env vars to containers
- Use `.env` files for configuration
- Document all required variables
- Test with production-like settings

#### **2. DNS and Networking**
- DNS propagation takes time
- Wildcard DNS is essential for dynamic subdomains
- Test DNS before assuming routing issues
- Network isolation is important for security

#### **3. Async Programming Requires Care**
- Proper session management prevents leaks
- Context managers simplify resource cleanup
- Always handle errors and rollback
- Test concurrent operations

#### **4. Docker Best Practices**
- Socket access is powerful but risky
- Use networks for container isolation
- Resource limits prevent resource exhaustion
- Health checks enable monitoring

#### **5. Production vs Development**
- Test on target environment early
- Automate deployment process
- Monitor logs and metrics
- Have rollback plan

### Development Process Lessons

#### **1. Debugging Strategy**
- Start with logs (backend, Docker, nginx)
- Verify each layer independently
- Use `docker inspect` for container details
- Test DNS with `nslookup`

#### **2. Documentation**
- Document as you build
- Include troubleshooting guides
- Write clear error messages
- Keep README updated

#### **3. Incremental Development**
- Build one feature at a time
- Test thoroughly before moving on
- Don't skip error handling
- Refactor as you learn

#### **4. Testing Approach**
- Test locally first
- Then test on server
- Verify each component independently
- Integration testing is crucial

---

## Problem-Solving Methodology

### My Debugging Process:

```
1. IDENTIFY THE PROBLEM
   └─> What exactly is failing?
   └─> What error messages appear?
   └─> When did it start failing?

2. GATHER INFORMATION
   └─> Check logs (backend, Docker, nginx)
   └─> Inspect containers: docker inspect
   └─> Test DNS: nslookup
   └─> Verify environment variables

3. FORM HYPOTHESIS
   └─> What could cause this?
   └─> What changed recently?
   └─> What are the dependencies?

4. TEST HYPOTHESIS
   └─> Make minimal changes
   └─> Test one thing at a time
   └─> Document results

5. IMPLEMENT SOLUTION
   └─> Fix the root cause
   └─> Test thoroughly
   └─> Document the fix

6. PREVENT RECURRENCE
   └─> Add error handling
   └─> Improve logging
   └─> Update documentation
```

**Speaker Notes:**
- Systematisk approach til debugging
- Documentation hjælper fremtidige problemer
- Lær af hver fejl

---

## PowerPoint Tips for This Section

### Slide Design:
- **Slide 16:** Problem-Solution format (2 columns)
- **Slide 17:** Bullet points with icons

### Visual Elements:
- ❌ Red for problems
- ✅ Green for solutions
- 💡 Light bulb for lessons learned
- 🔧 Wrench for technical fixes

### Code Snippets:
- Show before/after comparisons
- Highlight the fix
- Include error messages

### Timing:
- Slide 16: 45 seconds (challenges)
- Slide 17: 15 seconds (lessons)
- **Total: 1 minute**

---

## Key Messages

1. **Persistence:** "Hver fejl var en læringsmulighed"
2. **Methodology:** "Systematisk debugging finder root cause"
3. **Documentation:** "Dokumenter problemer og løsninger"
4. **Growth:** "Projektet blev bedre gennem challenges"

---

## Potential Questions & Answers

**Q: "Hvad var den sværeste udfordring?"**
A: "Subdomain routing - det tog længst tid at debugge fordi problemet var på flere niveauer: environment variables, DNS, og Traefik konfiguration."

**Q: "Hvordan ville du undgå disse problemer næste gang?"**
A: "Bedre initial planning, test på production-like environment tidligere, mere comprehensive documentation fra start."

**Q: "Hvad ville du gøre anderledes?"**
A: "Implementere proper CI/CD pipeline, automated testing, bedre monitoring og alerting."

---

## Transition to Conclusion

**Say:**
> "Disse udfordringer gjorde projektet bedre og lærte mig meget om production deployment. Lad os afslutte med at se på fremtiden for ASU1-Loom..."

**Next:** Slide 18 - Conclusion & Future Work
