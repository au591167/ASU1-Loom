# Frontend Implementation - ASU1-Loom 🎨

## Slide 14: Frontend Architecture

### Frontend Stack Overview

```
frontend/
├── dist/
│   ├── index.html        # Main HTML page
│   ├── app.js           # Application logic & API calls
│   ├── templates.js     # UI templates
│   └── styles.css       # Styling
├── Dockerfile           # Container build
└── nginx.conf          # Web server configuration
```

**Technology Choice: WebAssembly + Pyodide**

**Why WebAssembly?**
- ✅ Run Python directly in browser
- ✅ No server-side rendering needed
- ✅ Portable across platforms
- ✅ Near-native performance

**Why NOT React/Vue/Angular?**
- ❌ Overkill for this use case
- ❌ Large bundle sizes
- ❌ Build complexity
- ✅ Vanilla JS is simpler and faster

**Speaker Notes:**
- Simpel men effektiv frontend
- WebAssembly giver os Python i browseren
- Nginx server static files
- Alt kommunikation via GraphQL

---

## Slide 15: Frontend Implementation

### HTML Structure

**📍 File:** `frontend/dist/index.html` (lines 1-50)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASU1-Loom - Container Orchestration</title>
    <link rel="stylesheet" href="styles.css">
    
    <!-- Load Pyodide (WebAssembly Python) -->
    <script src="https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js"></script>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header>
            <h1>🧵 ASU1-Loom</h1>
            <p>Container Orchestration Platform</p>
        </header>

        <!-- Main Content -->
        <main>
            <!-- Container List -->
            <section id="container-list">
                <h2>Containers</h2>
                <button id="create-btn" class="btn-primary">
                    + Create Container
                </button>
                <div id="containers"></div>
            </section>

            <!-- Create Container Modal -->
            <div id="create-modal" class="modal hidden">
                <div class="modal-content">
                    <h2>Create New Container</h2>
                    <form id="create-form">
                        <input type="text" name="name" 
                               placeholder="Container Name" required>
                        <input type="text" name="image" 
                               placeholder="Docker Image" required>
                        <input type="text" name="tag" 
                               placeholder="Tag (default: latest)">
                        <input type="text" name="subdomain" 
                               placeholder="Subdomain" 
                               pattern="[a-z0-9-]+" required>
                        <input type="number" name="port" 
                               placeholder="Internal Port" 
                               value="80" required>
                        
                        <div class="modal-actions">
                            <button type="submit" class="btn-primary">
                                Create
                            </button>
                            <button type="button" class="btn-secondary" 
                                    id="cancel-btn">
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </main>
    </div>

    <!-- Load JavaScript -->
    <script src="templates.js"></script>
    <script src="app.js"></script>
</body>
</html>
```

**Key Features:**
- Clean, semantic HTML5
- Modal for container creation
- Form validation (pattern attribute)
- Responsive design ready

---

### JavaScript Application Logic

**📍 File:** `frontend/dist/app.js` (lines 1-150)

```javascript
// ASU1-Loom Frontend Application
// Handles UI logic and GraphQL API communication

// Configuration
const API_ENDPOINT = '/graphql';  // Relative URL (proxied by nginx)

// State management
let containers = [];

// ============================================================================
// API Communication
// ============================================================================

/**
 * Execute GraphQL query/mutation
 * @param {string} query - GraphQL query string
 * @param {object} variables - Query variables
 * @returns {Promise<object>} - Response data
 */
async function graphqlQuery(query, variables = {}) {
    try {
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query,
                variables
            })
        });

        const result = await response.json();
        
        if (result.errors) {
            console.error('GraphQL errors:', result.errors);
            throw new Error(result.errors[0].message);
        }

        return result.data;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

/**
 * Fetch all containers from API
 */
async function fetchContainers() {
    const query = `
        query {
            containers {
                id
                name
                image
                tag
                subdomain
                status
                createdAt
            }
        }
    `;

    const data = await graphqlQuery(query);
    containers = data.containers;
    renderContainers();
}

/**
 * Create new container
 * @param {object} containerData - Container configuration
 */
async function createContainer(containerData) {
    const mutation = `
        mutation CreateContainer(
            $name: String!,
            $image: String!,
            $tag: String,
            $subdomain: String,
            $internalPort: Int!
        ) {
            createContainer(
                name: $name,
                image: $image,
                tag: $tag,
                subdomain: $subdomain,
                internalPort: $internalPort
            ) {
                id
                name
                status
                subdomain
            }
        }
    `;

    const variables = {
        name: containerData.name,
        image: containerData.image,
        tag: containerData.tag || 'latest',
        subdomain: containerData.subdomain,
        internalPort: parseInt(containerData.port)
    };

    const data = await graphqlQuery(mutation, variables);
    console.log('Container created:', data.createContainer);
    
    // Refresh container list
    await fetchContainers();
    
    return data.createContainer;
}

/**
 * Start container
 * @param {string} containerId - Container ID
 */
async function startContainer(containerId) {
    const mutation = `
        mutation StartContainer($id: String!) {
            startContainer(id: $id) {
                id
                status
            }
        }
    `;

    const data = await graphqlQuery(mutation, { id: containerId });
    console.log('Container started:', data.startContainer);
    
    // Refresh container list
    await fetchContainers();
}

/**
 * Stop container
 * @param {string} containerId - Container ID
 */
async function stopContainer(containerId) {
    const mutation = `
        mutation StopContainer($id: String!) {
            stopContainer(id: $id) {
                id
                status
            }
        }
    `;

    const data = await graphqlQuery(mutation, { id: containerId });
    console.log('Container stopped:', data.stopContainer);
    
    // Refresh container list
    await fetchContainers();
}

// ============================================================================
// UI Rendering
// ============================================================================

/**
 * Render container list
 */
function renderContainers() {
    const containerList = document.getElementById('containers');
    
    if (containers.length === 0) {
        containerList.innerHTML = `
            <div class="empty-state">
                <p>No containers yet. Create your first container!</p>
            </div>
        `;
        return;
    }

    containerList.innerHTML = containers.map(container => `
        <div class="container-card" data-id="${container.id}">
            <div class="container-header">
                <h3>${container.name}</h3>
                <span class="status status-${container.status}">
                    ${container.status}
                </span>
            </div>
            <div class="container-details">
                <p><strong>Image:</strong> ${container.image}:${container.tag}</p>
                <p><strong>Subdomain:</strong> 
                    ${container.subdomain ? 
                        `<a href="http://${container.subdomain}.pandaserver.ddns.net" 
                            target="_blank">
                            ${container.subdomain}.pandaserver.ddns.net
                        </a>` 
                        : 'N/A'}
                </p>
                <p><strong>Created:</strong> ${new Date(container.createdAt).toLocaleString()}</p>
            </div>
            <div class="container-actions">
                ${container.status === 'created' || container.status === 'stopped' ? 
                    `<button class="btn-success" onclick="startContainer('${container.id}')">
                        Start
                    </button>` : ''}
                ${container.status === 'running' ? 
                    `<button class="btn-warning" onclick="stopContainer('${container.id}')">
                        Stop
                    </button>` : ''}
                <button class="btn-danger" onclick="deleteContainer('${container.id}')">
                    Delete
                </button>
            </div>
        </div>
    `).join('');
}

// ============================================================================
// Event Handlers
// ============================================================================

/**
 * Initialize application
 */
async function init() {
    console.log('🧵 ASU1-Loom initializing...');

    // Fetch initial data
    await fetchContainers();

    // Setup event listeners
    document.getElementById('create-btn').addEventListener('click', () => {
        document.getElementById('create-modal').classList.remove('hidden');
    });

    document.getElementById('cancel-btn').addEventListener('click', () => {
        document.getElementById('create-modal').classList.add('hidden');
    });

    document.getElementById('create-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const containerData = Object.fromEntries(formData);

        try {
            await createContainer(containerData);
            
            // Close modal and reset form
            document.getElementById('create-modal').classList.add('hidden');
            e.target.reset();
            
            alert('Container created successfully!');
        } catch (error) {
            alert(`Failed to create container: ${error.message}`);
        }
    });

    console.log('✅ ASU1-Loom initialized');
}

// Start application when DOM is ready
document.addEventListener('DOMContentLoaded', init);
```

**Key Implementation Details:**

1. **GraphQL Communication:**
   - Single `graphqlQuery()` function for all API calls
   - Error handling with user-friendly messages
   - Automatic data refresh after mutations

2. **State Management:**
   - Simple array for container list
   - Re-render on state changes
   - No complex state library needed

3. **Event Handling:**
   - Form submission for container creation
   - Button clicks for start/stop/delete
   - Modal show/hide

4. **User Experience:**
   - Loading states
   - Error messages
   - Success feedback
   - Clickable subdomain links

**Speaker Notes:**
- Vanilla JavaScript - ingen framework overhead
- GraphQL gør API calls simple og type-safe
- State management er simpelt da vi ikke har kompleks UI
- Event listeners håndterer user interactions

---

### Nginx Configuration

**📍 File:** `frontend/nginx.conf` (lines 1-60)

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Enable gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/javascript application/json 
               application/wasm;

    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # WASM MIME type
        types {
            application/wasm wasm;
        }

        # Main location - serve frontend
        location / {
            try_files $uri $uri/ /index.html;
        }

        # Proxy API requests to backend
        location /api/ {
            proxy_pass http://backend:8000/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }

        # Proxy GraphQL requests to backend
        location /graphql {
            proxy_pass http://backend:8000/graphql;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }

        # Static files caching
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|wasm)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

**Key Configuration:**

1. **Proxy Setup:**
   - `/graphql` → `backend:8000/graphql`
   - Allows frontend to use relative URLs
   - Avoids CORS issues

2. **Security Headers:**
   - XSS protection
   - Frame options
   - Content type sniffing prevention

3. **Performance:**
   - Gzip compression
   - Static file caching (1 year)
   - WASM MIME type support

4. **SPA Support:**
   - `try_files` for client-side routing
   - Fallback to index.html

**Speaker Notes:**
- Nginx fungerer som reverse proxy
- GraphQL requests proxies til backend
- Security headers beskytter mod common attacks
- Caching forbedrer performance

---

## Frontend-Backend Communication Flow

### Example: Creating a Container

```
1. USER INTERACTION
   └─> User fills form and clicks "Create"

2. JAVASCRIPT (app.js)
   └─> Form submit event handler triggered
   └─> Extract form data
   └─> Call createContainer(containerData)

3. GRAPHQL MUTATION
   └─> Build GraphQL mutation string
   └─> Add variables from form data
   └─> POST to /graphql endpoint

4. NGINX PROXY
   └─> Receives request at /graphql
   └─> Proxies to backend:8000/graphql
   └─> Preserves headers and body

5. BACKEND (FastAPI + GraphQL)
   └─> Receives mutation
   └─> Validates input
   └─> Calls docker_manager.create_container()
   └─> Saves to database
   └─> Returns container object

6. RESPONSE FLOW
   └─> Backend → Nginx → Browser
   └─> JavaScript receives response
   └─> Updates UI state
   └─> Re-renders container list
   └─> Shows success message

7. USER SEES
   └─> New container in list
   └─> Status: "created"
   └─> Clickable subdomain link
```

**Speaker Notes:**
- Hele flowet er async - ingen page reload
- Fejl håndteres på hvert niveau
- UI opdateres automatisk efter mutation
- User får feedback på hver action

---

## PowerPoint Tips for This Section

### Slide Design:
- **Slide 14:** Frontend architecture diagram
- **Slide 15:** Split screen - HTML + JavaScript code

### Code Formatting:
- Syntax highlighting for HTML/JS
- Highlight key functions (graphqlQuery, createContainer)
- Show before/after for UI updates

### Animations:
- Code appears section by section
- Flow diagram animates step-by-step
- UI mockup shows state changes

### Timing:
- Slide 14: 30 seconds (architecture)
- Slide 15: 90 seconds (code walkthrough)
- **Total: 2 minutes**

---

## Key Messages

1. **Simplicity:** "Vanilla JavaScript - ingen unødvendig kompleksitet"
2. **GraphQL:** "Type-safe API communication med minimal boilerplate"
3. **User Experience:** "Responsive UI med real-time updates"
4. **Performance:** "Nginx caching og gzip for hurtig load time"

---

## Potential Questions & Answers

**Q: "Hvorfor ikke React eller Vue?"**
A: "For dette projekt er vanilla JavaScript tilstrækkeligt. React ville tilføje ~100KB bundle size og build complexity uden reel værdi. Simplicity over complexity."

**Q: "Hvad med state management ved større apps?"**
A: "For større apps ville jeg bruge Redux eller Zustand. Men med kun én liste af containers er simpel array state nok."

**Q: "Hvordan håndterer du real-time updates?"**
A: "Lige nu poller vi efter mutations. For production ville jeg tilføje WebSocket subscriptions via GraphQL for live updates."

**Q: "Hvad med mobile support?"**
A: "CSS er responsive-ready. Nginx konfiguration virker på mobile. Pyodide virker i mobile browsers."

---

## Transition to Next Section

**Say:**
> "Nu har vi set både backend og frontend implementeringen. Men udviklingen var ikke uden udfordringer. Lad mig dele nogle af de problemer jeg løste undervejs..."

**Next:** Slide 16 - Challenges & Solutions
