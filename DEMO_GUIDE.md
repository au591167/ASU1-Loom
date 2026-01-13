# ASU1-Loom Demo Guide

## Overview
ASU1-Loom is a hybrid container orchestration platform that combines WebAssembly frontend with Python backend for managing Docker containers with automatic subdomain routing.

## Demo Scenarios

### 1. Basic Container Management
**Goal**: Demonstrate core container lifecycle operations

**Steps**:
1. Open http://localhost:3000 in browser
2. Navigate to "Containers" tab
3. Click "New Container" → Select "Custom Container"
4. Fill form:
   - Name: `demo-nginx`
   - Image: `nginx`
   - Tag: `latest`
   - Subdomain: `demo`
   - Internal Port: `80`
5. Click "Create Container"
6. Wait for creation, then click "Start" button
7. Container should be accessible at `demo.pandaserver.ddns.net` (if Traefik configured)
8. Click "Stop" to stop the container
9. Click "Delete" to remove it

**Expected Results**:
- Container appears in list
- Status changes from "created" → "running" → "stopped"
- System stats update in dashboard

### 2. System Monitoring
**Goal**: Show system information and container statistics

**Steps**:
1. Go to "Dashboard" tab
2. Observe system stats (containers, CPU, memory)
3. Create and start a container
4. Watch stats update in real-time

### 3. Modpack Search (Optional)
**Goal**: Demonstrate modpack integration

**Steps**:
1. Search for "skyfactory" in modpack browser
2. View results from CurseForge/Modrinth
3. Note: Full functionality requires API keys

## Technical Architecture

### Backend (Python/FastAPI)
- GraphQL API for container management
- Docker SDK integration
- PostgreSQL database
- Async operations

### Frontend (WebAssembly)
- Pyodide-powered interface
- Real-time GraphQL queries
- Responsive design

### Infrastructure
- Docker Compose orchestration
- Traefik reverse proxy
- Automatic subdomain routing

## Key Features Demonstrated

✅ **Container Lifecycle**: Create, start, stop, delete containers
✅ **Resource Management**: CPU/memory limits, environment variables
✅ **Automatic Routing**: Subdomain assignment via Traefik
✅ **System Monitoring**: Real-time stats and container information
✅ **Modpack Integration**: Search across multiple sources
✅ **WebAssembly GUI**: Modern, portable interface

## Troubleshooting

### Backend Not Starting
- Check database connection (pandaserver.ddns.net)
- Verify Docker is running
- Check logs in `backend/logs/loom.log`

### Frontend Not Loading
- Ensure backend is running on port 8000
- Check browser console for errors
- Verify Pyodide CDN is accessible

### Container Operations Fail
- Verify Docker daemon is running
- Check Docker network `loom_network` exists
- Ensure user has Docker permissions

## Demo Script

**Introduction (2 min)**:
- Explain project goals and architecture
- Show system overview diagram

**Live Demo (8 min)**:
- Container creation and management
- System monitoring
- Modpack search demonstration

**Q&A (5 min)**:
- Technical implementation details
- Future enhancements
- Challenges overcome

## Backup Plan

If Docker operations fail:
- Demonstrate GraphQL API directly
- Show database operations
- Explain container management logic

If frontend fails:
- Use GraphQL playground at `/graphql`
- Demonstrate API functionality
- Show backend logs and operations

## Success Criteria

✅ System starts without errors
✅ Container creation works
✅ Start/stop operations functional
✅ Frontend loads and connects to backend
✅ Basic modpack search operational
✅ System monitoring displays data

---

**Demo Duration**: 15 minutes
**Preparation Time**: Verify all services start correctly
**Backup**: GraphQL playground demonstration
