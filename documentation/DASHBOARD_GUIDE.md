# 🎨 ASU1-Loom Dashboard Guide

## Overview

The ASU1-Loom dashboard is a modern, responsive web interface for managing Docker containers through a hybrid WebAssembly-powered platform.

## Accessing the Dashboard

### Quick Start
1. **Start Backend Server** (Terminal 1):
   ```bash
   cd Project/ASU1-Loom/backend
   .\venv\Scripts\activate
   python run.py
   ```
   Backend will run on: http://localhost:8000

2. **Start Frontend Server** (Terminal 2):
   ```bash
   cd Project/ASU1-Loom/frontend
   python serve.py
   ```
   Frontend will run on: http://localhost:3000

3. **Open Dashboard**:
   - Navigate to: http://localhost:3000
   - Or run: `start http://localhost:3000`

## Dashboard Features

### 1. 📊 Dashboard View (Home)
**Purpose**: Overview of your container infrastructure

**Features**:
- **Statistics Cards**:
  - Total Containers count
  - Running containers (green)
  - Stopped containers (red)
  - CPU Usage (placeholder for future monitoring)

- **Recent Containers**:
  - Shows last 5 containers created
  - Quick status overview
  - Direct links to container subdomains

**What You'll See**:
- Empty state: "No containers yet. Create your first one!"
- Populated state: Container cards with status badges

### 2. ➕ Create New Container
**Purpose**: Deploy new Docker containers with automatic subdomain routing

**Form Fields**:

#### Required Fields
- **Container Name**: 
  - Format: lowercase letters, numbers, hyphens
  - Example: `my-nginx-app`
  - Used as container identifier

- **Docker Image**: 
  - Format: image name from Docker Hub
  - Example: `nginx`, `postgres`, `node`
  - Can include registry: `ghcr.io/user/image`

- **Tag**: 
  - Default: `latest`
  - Example: `14-alpine`, `3.11-slim`

- **Subdomain**: 
  - Format: lowercase letters, numbers, hyphens
  - Example: `myapp`
  - Will be accessible at: `myapp.pandasserver.ddns.net`

- **Internal Port**: 
  - Port your application listens on inside the container
  - Example: `80` (nginx), `3000` (node), `5432` (postgres)

#### Optional Fields
- **Environment Variables**: 
  - Format: JSON object
  - Example:
    ```json
    {
      "NODE_ENV": "production",
      "PORT": "3000",
      "DATABASE_URL": "postgresql://..."
    }
    ```

- **CPU Limit**: 
  - Number of CPU cores
  - Example: `1.0`, `0.5`, `2.0`

- **Memory Limit**: 
  - Memory in MB
  - Example: `512`, `1024`, `2048`

**Actions**:
- **Create Container**: Submits the form and creates the container
- **Reset**: Clears all form fields

**Example Configurations**:

1. **Nginx Web Server**:
   ```
   Name: my-website
   Image: nginx
   Tag: alpine
   Subdomain: website
   Port: 80
   ```

2. **Node.js Application**:
   ```
   Name: node-api
   Image: node
   Tag: 18-alpine
   Subdomain: api
   Port: 3000
   Environment: {"NODE_ENV": "production"}
   ```

3. **PostgreSQL Database**:
   ```
   Name: postgres-db
   Image: postgres
   Tag: 15-alpine
   Subdomain: db
   Port: 5432
   Environment: {"POSTGRES_PASSWORD": "secret"}
   Memory: 1024
   ```

### 3. 📦 Containers List
**Purpose**: View and manage all containers

**Features**:
- **Refresh Button**: Reload container list
- **Container Cards**: Each card shows:
  - Container name
  - Status badge (running/stopped)
  - Docker image and tag
  - Subdomain link (clickable)
  - Internal port
  - Action buttons

**Actions Per Container**:
- **Start**: Start a stopped container
- **Stop**: Stop a running container
- **Delete**: Remove container (with confirmation)

**Status Indicators**:
- 🟢 **Running**: Container is active
- 🔴 **Stopped**: Container is inactive
- 🟡 **Starting**: Container is starting up
- 🟠 **Error**: Container has errors

### 4. ⚙️ Settings
**Purpose**: Configuration and system information

**Sections**:

1. **API Configuration**:
   - API Endpoint: `http://localhost:8000/graphql`
   - Connection Status: Connected/Disconnected

2. **About**:
   - Version: 1.0.0
   - Author: Erik Kjær Klint
   - Course: EH5ASU1
   - License: MIT

## User Interface Elements

### Navigation Bar
- **Dashboard**: Home view with statistics
- **Create New**: Container creation form
- **Containers**: Full container list
- **Settings**: Configuration and info

### Notifications
Appears at top of screen for 3 seconds:
- 🔵 **Info**: Loading/processing messages
- 🟢 **Success**: Operation completed
- 🔴 **Error**: Operation failed

### Container Cards
```
┌─────────────────────────────────────────┐
│ Container Name                          │
│ ● Status | 📦 Image:Tag                │
│ 🌐 subdomain.pandaserver.ddns.net      │
│ 🔌 Port 80                              │
│                                         │
│ [Start/Stop]  [Delete]                  │
└─────────────────────────────────────────┘
```

## API Communication

### GraphQL Queries Used

1. **List Containers**:
   ```graphql
   query {
     containers {
       id
       name
       image
       tag
       status
       subdomain
       port
       createdAt
     }
   }
   ```

2. **Create Container**:
   ```graphql
   mutation CreateContainer($input: ContainerInput!) {
     createContainer(input: $input) {
       id
       name
       status
     }
   }
   ```

3. **Start Container**:
   ```graphql
   mutation StartContainer($id: ID!) {
     startContainer(id: $id) {
       id
       status
     }
   }
   ```

4. **Stop Container**:
   ```graphql
   mutation StopContainer($id: ID!) {
     stopContainer(id: $id) {
       id
       status
     }
   }
   ```

5. **Delete Container**:
   ```graphql
   mutation DeleteContainer($id: ID!) {
     deleteContainer(id: $id)
   }
   ```

## Technical Details

### Frontend Stack
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with flexbox/grid
- **Vanilla JavaScript**: No framework dependencies
- **Pyodide**: WebAssembly Python runtime (loaded but not yet utilized)

### API Integration
- **Endpoint**: http://localhost:8000/graphql
- **Protocol**: GraphQL over HTTP POST
- **CORS**: Enabled for localhost:3000
- **Error Handling**: User-friendly error messages

### Browser Compatibility
- ✅ Chrome/Edge (recommended)
- ✅ Firefox
- ✅ Safari
- ⚠️ IE11 (not supported)

## Troubleshooting

### Dashboard Won't Load
1. Check backend is running: http://localhost:8000/health
2. Check frontend server is running: http://localhost:3000
3. Check browser console for errors (F12)

### "API request failed" Error
1. Verify backend server is running
2. Check CORS configuration in backend
3. Verify GraphQL endpoint is accessible
4. Check browser network tab (F12)

### Containers Not Showing
1. Check database connection in backend
2. Verify GraphQL query is working: http://localhost:8000/docs
3. Check browser console for JavaScript errors

### Create Container Fails
1. Verify all required fields are filled
2. Check environment variables JSON is valid
3. Ensure subdomain is unique
4. Check backend logs for errors

## Keyboard Shortcuts

- **Ctrl + R**: Refresh current view
- **Esc**: Close notifications
- **Tab**: Navigate form fields

## Best Practices

### Container Naming
- Use descriptive names: `nginx-prod`, `api-staging`
- Avoid special characters
- Keep names short but meaningful

### Subdomain Selection
- Use project/service names
- Avoid conflicts with existing subdomains
- Consider environment: `app-dev`, `app-prod`

### Resource Limits
- Set CPU limits for production containers
- Allocate memory based on application needs
- Monitor resource usage regularly

### Environment Variables
- Never store secrets in plain text
- Use environment variables for configuration
- Validate JSON before submitting

## Future Enhancements

### Planned Features
- [ ] Real-time container logs viewer
- [ ] Resource usage graphs (CPU, Memory, Network)
- [ ] Container templates library
- [ ] Bulk operations (start/stop multiple)
- [ ] Container health monitoring
- [ ] Backup and restore functionality
- [ ] User authentication and authorization
- [ ] WebSocket for real-time updates
- [ ] Dark mode toggle
- [ ] Export container configurations

### WebAssembly Integration
- [ ] Python-based container validation
- [ ] Client-side data processing
- [ ] Advanced filtering and search
- [ ] Offline functionality

## Support

### Documentation
- **Setup Guide**: `docs/SETUP.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **API Reference**: http://localhost:8000/docs

### Logs
- **Backend Logs**: Terminal running `python run.py`
- **Frontend Logs**: Browser console (F12)
- **Server Logs**: `logs/loom.log`

### Common Issues
See `TROUBLESHOOTING.md` for detailed solutions

## Screenshots

### Dashboard View
```
┌────────────────────────────────────────────────────┐
│  🧵 ASU1-Loom                                      │
│  Hybrid Container Orchestration Platform           │
│                                                    │
│  [Dashboard] [Create New] [Containers] [Settings] │
├────────────────────────────────────────────────────┤
│                                                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────┐│
│  │  Total   │ │ Running  │ │ Stopped  │ │  CPU  ││
│  │    0     │ │    0     │ │    0     │ │  0%   ││
│  └──────────┘ └──────────┘ └──────────┘ └───────┘│
│                                                    │
│  Recent Containers                                 │
│  ┌────────────────────────────────────────────┐  │
│  │ No containers yet. Create your first one!  │  │
│  └────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
```

## Conclusion

The ASU1-Loom dashboard provides an intuitive interface for managing containerized applications with automatic subdomain routing and resource management. The WebAssembly-powered frontend ensures high performance and portability, while the GraphQL API provides flexible and efficient data communication.

For more information, see the main README.md or visit the documentation at `docs/`.

---

**Last Updated**: December 4, 2025  
**Version**: 1.0.0  
**Status**: ✅ Operational
