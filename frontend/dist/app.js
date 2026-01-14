// ASU1-Loom Frontend Application

// Use relative URL so it works from any domain (localhost or pandaserver.ddns.net)
// Traefik will route /graphql to the backend
const API_ENDPOINT = '/graphql';

// State management
let containers = [];
let pyodide = null;

// Initialize application
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🧵 ASU1-Loom initializing...');
    
    // Setup navigation
    setupNavigation();
    
    // Setup form handlers
    setupFormHandlers();
    
    // Load initial data
    await loadDashboard();
    
    // Check API connection
    checkConnection();
    
    console.log('✅ ASU1-Loom initialized');
});

// Navigation
function setupNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    
    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const view = btn.dataset.view;
            switchView(view);
            
            // Update active state
            navButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });
}

function switchView(viewName) {
    const views = document.querySelectorAll('.view');
    views.forEach(view => view.classList.remove('active'));
    
    const targetView = document.getElementById(`${viewName}-view`);
    if (targetView) {
        targetView.classList.add('active');
        
        // Load data for specific views
        if (viewName === 'dashboard') {
            loadDashboard();
        } else if (viewName === 'containers') {
            loadAllContainers();
        }
    }
}

// Form handlers
function setupFormHandlers() {
    const createForm = document.getElementById('create-container-form');
    
    if (createForm) {
        createForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await createContainer(new FormData(createForm));
        });
    }
}

// GraphQL API calls
async function graphqlRequest(query, variables = {}) {
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
        showNotification('API request failed: ' + error.message, 'error');
        throw error;
    }
}

// Load dashboard data
async function loadDashboard() {
    try {
        const query = `
            query {
                containers {
                    id
                    name
                    image
                    status
                    subdomain
                    createdAt
                }
            }
        `;
        
        const data = await graphqlRequest(query);
        containers = data.containers || [];
        
        updateDashboardStats();
        displayRecentContainers();
    } catch (error) {
        console.error('Failed to load dashboard:', error);
        document.getElementById('recent-containers').innerHTML = 
            '<p class="error">Failed to load containers. Please check your connection.</p>';
    }
}

// Update dashboard statistics
function updateDashboardStats() {
    const total = containers.length;
    const running = containers.filter(c => c.status === 'running').length;
    const stopped = containers.filter(c => c.status === 'stopped').length;
    
    document.getElementById('total-containers').textContent = total;
    document.getElementById('running-containers').textContent = running;
    document.getElementById('stopped-containers').textContent = stopped;
    document.getElementById('cpu-usage').textContent = '0%'; // Placeholder
}

// Display recent containers
function displayRecentContainers() {
    const container = document.getElementById('recent-containers');
    
    if (containers.length === 0) {
        container.innerHTML = '<p class="loading">No containers yet. Create your first one!</p>';
        return;
    }
    
    const recentContainers = containers.slice(0, 5);
    container.innerHTML = recentContainers.map(c => createContainerCard(c)).join('');
}

// Load all containers
async function loadAllContainers() {
    try {
        const query = `
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
        `;
        
        const data = await graphqlRequest(query);
        containers = data.containers || [];
        
        displayAllContainers();
    } catch (error) {
        console.error('Failed to load containers:', error);
        document.getElementById('all-containers').innerHTML = 
            '<p class="error">Failed to load containers.</p>';
    }
}

// Display all containers
function displayAllContainers() {
    const container = document.getElementById('all-containers');
    
    if (containers.length === 0) {
        container.innerHTML = '<p class="loading">No containers found.</p>';
        return;
    }
    
    container.innerHTML = containers.map(c => createContainerCard(c, true)).join('');
}

// Create container card HTML
function createContainerCard(container, showActions = false) {
    const statusClass = container.status === 'running' ? 'running' : 'stopped';
    const url = `http://${container.subdomain}.pandaserver.ddns.net`;
    
    return `
        <div class="container-card">
            <div class="container-info">
                <h3>${container.name}</h3>
                <div class="container-meta">
                    <span class="status-badge ${statusClass}">${container.status}</span>
                    <span>📦 ${container.image}:${container.tag || 'latest'}</span>
                    <span>🌐 <a href="${url}" target="_blank">${container.subdomain}</a></span>
                    <span>🔌 Port ${container.port}</span>
                </div>
            </div>
            ${showActions ? `
                <div class="container-actions">
                    ${container.status === 'running' 
                        ? `<button class="btn btn-small btn-secondary" onclick="stopContainer('${container.id}')">Stop</button>`
                        : `<button class="btn btn-small btn-success" onclick="startContainer('${container.id}')">Start</button>`
                    }
                    <button class="btn btn-small btn-danger" onclick="deleteContainer('${container.id}')">Delete</button>
                </div>
            ` : ''}
        </div>
    `;
}

// Create new container
async function createContainer(formData) {
    try {
        const name = formData.get('name');
        const image = formData.get('image');
        const tag = formData.get('tag') || 'latest';
        const subdomain = formData.get('subdomain');
        const port = parseInt(formData.get('port'));
        
        let environment = {};
        const envInput = formData.get('environment');
        if (envInput && envInput.trim()) {
            try {
                environment = JSON.parse(envInput);
            } catch (e) {
                showNotification('Invalid JSON in environment variables', 'error');
                return;
            }
        }
        
        const cpuLimit = formData.get('cpu_limit') ? parseFloat(formData.get('cpu_limit')) : null;
        const memoryLimit = formData.get('memory_limit') ? parseInt(formData.get('memory_limit')) : null;
        
        const mutation = `
            mutation CreateContainer($input: ContainerInput!) {
                createContainer(input: $input) {
                    id
                    name
                    status
                }
            }
        `;
        
        const variables = {
            input: {
                name,
                image,
                tag,
                subdomain,
                internalPort: port,
                environmentVars: environment,
                cpuLimit: cpuLimit ? cpuLimit.toString() : null,
                memoryLimit: memoryLimit ? memoryLimit.toString() + 'M' : null
            }
        };
        
        showNotification('Creating container...', 'info');
        
        const data = await graphqlRequest(mutation, variables);
        
        showNotification(`Container "${data.createContainer.name}" created successfully!`, 'success');
        
        // Reset form and switch to containers view
        document.getElementById('create-container-form').reset();
        switchView('containers');
        loadAllContainers();
        
    } catch (error) {
        console.error('Failed to create container:', error);
        showNotification('Failed to create container: ' + error.message, 'error');
    }
}

// Start container
async function startContainer(id) {
    try {
        const mutation = `
            mutation StartContainer($id: ID!) {
                startContainer(id: $id) {
                    id
                    status
                }
            }
        `;
        
        await graphqlRequest(mutation, { id });
        showNotification('Container started successfully', 'success');
        loadAllContainers();
    } catch (error) {
        showNotification('Failed to start container: ' + error.message, 'error');
    }
}

// Stop container
async function stopContainer(id) {
    try {
        const mutation = `
            mutation StopContainer($id: ID!) {
                stopContainer(id: $id) {
                    id
                    status
                }
            }
        `;
        
        await graphqlRequest(mutation, { id });
        showNotification('Container stopped successfully', 'success');
        loadAllContainers();
    } catch (error) {
        showNotification('Failed to stop container: ' + error.message, 'error');
    }
}

// Delete container
async function deleteContainer(id) {
    if (!confirm('Are you sure you want to delete this container?')) {
        return;
    }
    
    try {
        const mutation = `
            mutation DeleteContainer($id: ID!) {
                deleteContainer(id: $id)
            }
        `;
        
        await graphqlRequest(mutation, { id });
        showNotification('Container deleted successfully', 'success');
        loadAllContainers();
        loadDashboard();
    } catch (error) {
        showNotification('Failed to delete container: ' + error.message, 'error');
    }
}

// Refresh containers
function refreshContainers() {
    loadAllContainers();
    showNotification('Refreshing containers...', 'info');
}

// Check API connection
async function checkConnection() {
    try {
        const query = `query { containers { id } }`;
        await graphqlRequest(query);
        
        const statusEl = document.getElementById('connection-status');
        if (statusEl) {
            statusEl.textContent = 'Connected';
            statusEl.className = 'status connected';
        }
    } catch (error) {
        const statusEl = document.getElementById('connection-status');
        if (statusEl) {
            statusEl.textContent = 'Disconnected';
            statusEl.className = 'status disconnected';
        }
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type} show`;
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// Initialize Pyodide (WebAssembly Python runtime)
async function initPyodide() {
    if (pyodide) return pyodide;
    
    try {
        console.log('Loading Pyodide...');
        pyodide = await loadPyodide();
        console.log('✅ Pyodide loaded');
        return pyodide;
    } catch (error) {
        console.error('Failed to load Pyodide:', error);
        return null;
    }
}

// ============================================================================
// TEMPLATE SYSTEM FUNCTIONALITY
// ============================================================================

// Template system state
let selectedCategory = null;
let selectedType = null;
let currentTemplate = null;

// Initialize template system
function initTemplateSystem() {
    // Setup split button and dropdown
    const dropdownBtn = document.getElementById('create-dropdown-btn');
    const mainBtn = document.getElementById('create-main-btn');
    const dropdown = document.getElementById('create-dropdown-menu');
    const modal = document.getElementById('container-modal');
    const modalCloseBtn = document.getElementById('modal-close-btn');
    const modalCancelBtn = document.getElementById('modal-cancel-btn');
    const modalBackBtn = document.getElementById('modal-back-btn');
    const modalOverlay = modal?.querySelector('.modal-overlay');
    
    if (dropdownBtn) {
        dropdownBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleDropdown();
        });
    }
    
    if (mainBtn) {
        mainBtn.addEventListener('click', () => {
            // Main button always opens Custom template in modal
            openModal('custom', 'custom');
        });
    }
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (dropdown && !dropdown.contains(e.target) && 
            e.target !== dropdownBtn && e.target !== mainBtn) {
            closeDropdown();
        }
    });
    
    // Setup dropdown items
    const dropdownItems = document.querySelectorAll('.dropdown-item');
    dropdownItems.forEach(item => {
        item.addEventListener('click', () => {
            const category = item.dataset.category;
            if (category) {
                closeDropdown();
                // For custom, go directly to form
                if (category === 'custom') {
                    openModal('custom', 'custom');
                } else {
                    // For others, show template selection in modal
                    openModalWithCategory(category);
                }
            }
        });
    });
    
    // Setup modal close buttons
    if (modalCloseBtn) {
        modalCloseBtn.addEventListener('click', closeModal);
    }
    
    if (modalCancelBtn) {
        modalCancelBtn.addEventListener('click', closeModal);
    }
    
    if (modalOverlay) {
        modalOverlay.addEventListener('click', closeModal);
    }
    
    // Setup modal back button
    if (modalBackBtn) {
        modalBackBtn.addEventListener('click', () => {
            backToModalSelection();
        });
    }
    
    // Setup modal form submission
    const modalForm = document.getElementById('modal-container-form');
    if (modalForm) {
        modalForm.removeEventListener('submit', modalForm._submitHandler);
        modalForm._submitHandler = async (e) => {
            e.preventDefault();
            await submitModalForm();
        };
        modalForm.addEventListener('submit', modalForm._submitHandler);
    }
    
    // Close modal on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal?.classList.contains('show')) {
            closeModal();
        }
    });
}

// Toggle dropdown menu
function toggleDropdown() {
    const dropdown = document.getElementById('create-dropdown-menu');
    if (dropdown) {
        dropdown.classList.toggle('show');
    }
}

// Close dropdown menu
function closeDropdown() {
    const dropdown = document.getElementById('create-dropdown-menu');
    if (dropdown) {
        dropdown.classList.remove('show');
    }
}

// Select category and show template types
function selectCategory(category) {
    selectedCategory = category;
    const categoryData = CONTAINER_TEMPLATES[category];
    
    if (!categoryData) {
        console.error('Category not found:', category);
        return;
    }
    
    // Show template selection area
    const selectionArea = document.getElementById('template-selection');
    const titleEl = document.getElementById('template-category-title');
    const typesContainer = document.getElementById('template-types');
    
    if (titleEl) {
        titleEl.textContent = `${categoryData.icon} ${categoryData.name}`;
    }
    
    // Generate template type cards
    const types = Object.keys(categoryData.types).map(typeKey => {
        const type = categoryData.types[typeKey];
        return {
            id: typeKey,
            ...type
        };
    });
    
    if (typesContainer) {
        typesContainer.innerHTML = types.map(type => `
            <div class="template-card" data-type="${type.id}">
                <div class="template-card-icon">${getTypeIcon(category, type.id)}</div>
                <div class="template-card-title">${type.name}</div>
                <div class="template-card-description">
                    ${type.image ? `Image: ${type.image}` : 'Custom configuration'}
                </div>
            </div>
        `).join('');
        
        // Add click handlers to template cards
        const cards = typesContainer.querySelectorAll('.template-card');
        cards.forEach(card => {
            card.addEventListener('click', () => {
                const type = card.dataset.type;
                selectTemplate(category, type);
            });
        });
    }
    
    if (selectionArea) {
        selectionArea.style.display = 'block';
    }
}

// Get icon for template type
function getTypeIcon(category, type) {
    const icons = {
        development: {
            nodejs: '🟢',
            python: '🐍',
            php: '🐘',
            nginx: '🌐'
        },
        minecraft: {
            vanilla: '⛏️',
            paper: '📄',
            spigot: '🔧',
            forge: '🔥',
            neoforge: '⚡',
            fabric: '🧵'
        },
        gameserver: {
            valheim: '⚔️',
            terraria: '🌍'
        },
        custom: {
            custom: '📦'
        }
    };
    
    return icons[category]?.[type] || '📦';
}

// Select template and show form
function selectTemplate(category, type) {
    selectedCategory = category;
    selectedType = type;
    currentTemplate = getTemplate(category, type);
    
    if (!currentTemplate) {
        console.error('Template not found:', category, type);
        return;
    }
    
    showTemplateForm(category, type);
}

// Show template configuration form
function showTemplateForm(category, type) {
    const template = getTemplate(category, type);
    if (!template) return;
    
    // Hide template selection
    const selectionArea = document.getElementById('template-selection');
    if (selectionArea) {
        selectionArea.style.display = 'none';
    }
    
    // Show form
    const form = document.getElementById('create-container-form');
    const formTitle = document.getElementById('form-title');
    const dynamicFields = document.getElementById('dynamic-form-fields');
    
    if (formTitle) {
        const categoryData = CONTAINER_TEMPLATES[category];
        formTitle.textContent = `${categoryData.icon} ${template.name} Configuration`;
    }
    
    // Set hidden fields
    document.getElementById('selected-category').value = category;
    document.getElementById('selected-type').value = type;
    
    // Generate form fields
    if (dynamicFields) {
        dynamicFields.innerHTML = generateFormFields(template);
    }
    
    if (form) {
        form.style.display = 'block';
    }
    
    // Setup dynamic interactions
    setupFormInteractions();
}

// Generate form fields based on template
function generateFormFields(template) {
    let html = '';
    
    // Container Name
    html += `
        <div class="form-group">
            <label for="template-name">Container Name <span class="required-indicator">*</span></label>
            <input type="text" id="template-name" name="name" required 
                   placeholder="my-${template.name.toLowerCase().replace(/\s+/g, '-')}" 
                   pattern="[a-z0-9-]+" />
            <small class="helper-text">Lowercase letters, numbers, and hyphens only</small>
        </div>
    `;
    
    // Image Selection
    if (!template.advanced) {
        html += `
            <div class="form-group">
                <label for="template-image">Docker Image</label>
                <div class="image-selection">
                    <input type="text" id="template-image" name="image" 
                           value="${template.image}" readonly />
                    <small class="helper-text">Pre-configured for ${template.name}</small>
                </div>
            </div>
        `;
        
        // Tag Selection
        if (template.tags && template.tags.length > 0) {
            html += `
                <div class="form-group">
                    <label for="template-tag">Version/Tag</label>
                    <select id="template-tag" name="tag">
                        ${template.tags.map(tag => `
                            <option value="${tag}" ${tag === template.defaultTag ? 'selected' : ''}>
                                ${tag}
                            </option>
                        `).join('')}
                    </select>
                </div>
            `;
        }
    } else {
        // Custom image input
        html += `
            <div class="form-group">
                <label for="template-image">Docker Image <span class="required-indicator">*</span></label>
                <input type="text" id="template-image" name="image" required 
                       placeholder="nginx" />
            </div>
            <div class="form-group">
                <label for="template-tag">Tag</label>
                <input type="text" id="template-tag" name="tag" 
                       value="latest" placeholder="latest" />
            </div>
        `;
    }
    
    // Subdomain and Port
    html += `
        <div class="form-row">
            <div class="form-group">
                <label for="template-subdomain">Subdomain <span class="required-indicator">*</span></label>
                <input type="text" id="template-subdomain" name="subdomain" required 
                       placeholder="myapp" pattern="[a-z0-9-]+" />
                <small class="helper-text">Will be accessible at: subdomain.pandasserver.ddns.net</small>
            </div>
            <div class="form-group">
                <label for="template-port">Internal Port <span class="required-indicator">*</span></label>
                <input type="number" id="template-port" name="port" required 
                       value="${template.defaultPort}" min="1" max="65535" />
            </div>
        </div>
    `;
    
    // Environment Variables
    if (template.envVars && template.envVars.length > 0) {
        html += `
            <div class="form-section">
                <div class="form-section-title">Environment Variables</div>
                <div class="env-var-group">
                    ${template.envVars.map((envVar, index) => generateEnvVarField(envVar, index)).join('')}
                </div>
            </div>
        `;
    }
    
    // Resource Limits
    html += `
        <div class="form-section">
            <div class="form-section-title">Resource Limits</div>
            <div class="form-row">
                <div class="form-group">
                    <label for="template-cpu">CPU Limit (cores)</label>
                    <input type="number" id="template-cpu" name="cpu_limit" 
                           placeholder="1.0" step="0.1" min="0.1" value="1.0" />
                </div>
                <div class="form-group">
                    <label for="template-memory">Memory Limit (MB)</label>
                    <input type="number" id="template-memory" name="memory_limit" 
                           placeholder="512" step="128" min="128" 
                           value="${template.memory?.recommended || 512}" />
                    ${template.memory ? `
                        <div class="memory-badge">
                            Recommended: ${template.memory.recommended} MB
                        </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
    
    return html;
}

// Generate environment variable field
function generateEnvVarField(envVar, index) {
    const isRequired = envVar.required || false;
    const isOptional = envVar.optional || false;
    const fieldId = `env-${index}`;
    const inputId = `env-input-${index}`;
    
    let inputHtml = '';
    
    switch (envVar.type) {
        case 'text':
        case 'password':
            inputHtml = `
                <input type="${envVar.type}" id="${inputId}" 
                       placeholder="${envVar.default || ''}" 
                       ${!isOptional ? 'disabled' : ''} />
            `;
            break;
            
        case 'number':
            inputHtml = `
                <input type="number" id="${inputId}" 
                       value="${envVar.default || ''}" 
                       min="${envVar.min || 0}" 
                       max="${envVar.max || ''}"
                       ${!isOptional ? 'disabled' : ''} />
            `;
            break;
            
        case 'select':
            inputHtml = `
                <select id="${inputId}" ${!isOptional ? 'disabled' : ''}>
                    ${envVar.options.map(opt => `
                        <option value="${opt}" ${opt === envVar.default ? 'selected' : ''}>
                            ${opt}
                        </option>
                    `).join('')}
                </select>
            `;
            break;
            
        case 'checkbox':
            return `
                <div class="env-var-item">
                    <div class="env-var-content">
                        <label class="env-var-label">
                            <input type="checkbox" id="${fieldId}" 
                                   data-key="${envVar.key}" 
                                   ${envVar.default ? 'checked' : ''} 
                                   ${isRequired ? 'required' : ''} />
                            ${envVar.label} ${isRequired ? '<span class="required-indicator">*</span>' : ''}
                        </label>
                    </div>
                </div>
            `;
            
        case 'hidden':
            return `<input type="hidden" data-key="${envVar.key}" value="${envVar.default}" />`;
            
        default:
            inputHtml = `<input type="text" id="${inputId}" placeholder="${envVar.default || ''}" disabled />`;
    }
    
    return `
        <div class="env-var-item">
            <div class="env-var-checkbox">
                <input type="checkbox" id="${fieldId}" 
                       ${!isOptional && !isRequired ? 'checked' : ''} 
                       ${isRequired ? 'checked disabled' : ''} 
                       onchange="toggleEnvVarInput('${fieldId}', '${inputId}')" />
            </div>
            <div class="env-var-content">
                <label class="env-var-label" for="${fieldId}">
                    ${envVar.label} ${isRequired ? '<span class="required-indicator">*</span>' : ''}
                </label>
                <div class="env-var-input">
                    ${inputHtml}
                    <input type="hidden" data-key="${envVar.key}" data-input="${inputId}" />
                </div>
            </div>
        </div>
    `;
}

// Setup form interactions
function setupFormInteractions() {
    // Initialize disabled states for env var inputs
    const envVarItems = document.querySelectorAll('.env-var-item');
    envVarItems.forEach(item => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        const inputs = item.querySelectorAll('.env-var-input input:not([type="hidden"]), .env-var-input select');
        
        if (checkbox && !checkbox.disabled) {
            inputs.forEach(input => {
                input.disabled = !checkbox.checked;
            });
        }
    });
}

// Toggle environment variable input
function toggleEnvVarInput(checkboxId, inputId) {
    const checkbox = document.getElementById(checkboxId);
    const input = document.getElementById(inputId);
    
    if (checkbox && input) {
        input.disabled = !checkbox.checked;
        if (!checkbox.checked) {
            input.value = '';
        }
    }
}

// Back to template selection
function backToSelection() {
    const form = document.getElementById('create-container-form');
    const selectionArea = document.getElementById('template-selection');
    
    if (form) {
        form.style.display = 'none';
        form.reset();
    }
    
    if (selectionArea) {
        selectionArea.style.display = 'block';
    }
}

// Submit template form
async function submitTemplateForm() {
    try {
        const form = document.getElementById('create-container-form');
        const formData = new FormData(form);
        
        // Collect basic data
        const name = formData.get('name');
        const image = formData.get('image');
        const tag = formData.get('tag') || 'latest';
        const subdomain = formData.get('subdomain');
        const port = parseInt(formData.get('port'));
        const cpuLimit = formData.get('cpu_limit') ? parseFloat(formData.get('cpu_limit')) : null;
        const memoryLimit = formData.get('memory_limit') ? parseInt(formData.get('memory_limit')) : null;
        
        // Collect environment variables
        const environment = {};
        
        // Get all env var items
        const envVarItems = document.querySelectorAll('.env-var-item');
        envVarItems.forEach(item => {
            const checkbox = item.querySelector('input[type="checkbox"]');
            const hiddenInput = item.querySelector('input[type="hidden"][data-key]');
            
            if (hiddenInput) {
                const key = hiddenInput.dataset.key;
                
                // For checkbox type env vars
                if (checkbox && !hiddenInput.dataset.input) {
                    if (checkbox.checked) {
                        environment[key] = 'true';
                    }
                }
                // For other types with checkbox toggle
                else if (checkbox && hiddenInput.dataset.input) {
                    if (checkbox.checked || checkbox.disabled) {
                        const inputId = hiddenInput.dataset.input;
                        const input = document.getElementById(inputId);
                        if (input && input.value) {
                            environment[key] = input.value;
                        }
                    }
                }
            }
        });
        
        // Get hidden env vars (like TYPE for Minecraft)
        const hiddenEnvVars = document.querySelectorAll('input[type="hidden"][data-key]');
        hiddenEnvVars.forEach(input => {
            if (!input.dataset.input && input.value) {
                environment[input.dataset.key] = input.value;
            }
        });
        
        // Validate required fields
        if (!name || !image || !subdomain || !port) {
            showNotification('Please fill in all required fields', 'error');
            return;
        }
        
        // Create container via GraphQL
        const mutation = `
            mutation CreateContainer($input: ContainerInput!) {
                createContainer(input: $input) {
                    id
                    name
                    status
                }
            }
        `;
        
        const variables = {
            input: {
                name,
                image,
                tag,
                subdomain,
                internalPort: port,
                environmentVars: environment,
                cpuLimit: cpuLimit ? cpuLimit.toString() : null,
                memoryLimit: memoryLimit ? memoryLimit.toString() + 'M' : null
            }
        };
        
        showNotification('Creating container...', 'info');
        
        const data = await graphqlRequest(mutation, variables);
        
        showNotification(`Container "${data.createContainer.name}" created successfully!`, 'success');
        
        // Reset and switch view
        form.reset();
        form.style.display = 'none';
        const selectionArea = document.getElementById('template-selection');
        if (selectionArea) {
            selectionArea.style.display = 'none';
        }
        
        switchView('containers');
        loadAllContainers();
        
    } catch (error) {
        console.error('Failed to create container:', error);
        showNotification('Failed to create container: ' + error.message, 'error');
    }
}

// ============================================================================
// MODAL FUNCTIONS
// ============================================================================

// Open modal with specific template
function openModal(category, type) {
    const modal = document.getElementById('container-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalForm = document.getElementById('modal-container-form');
    const modalSelection = document.getElementById('modal-template-selection');
    
    if (!modal) return;
    
    // Show modal
    modal.classList.add('show');
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
    
    // Hide both selection and form initially
    if (modalSelection) modalSelection.style.display = 'none';
    if (modalForm) modalForm.style.display = 'none';
    
    // Load template and show form
    const template = getTemplate(category, type);
    if (template) {
        selectedCategory = category;
        selectedType = type;
        currentTemplate = template;
        
        const categoryData = CONTAINER_TEMPLATES[category];
        if (modalTitle) {
            modalTitle.textContent = `${categoryData.icon} ${template.name}`;
        }
        
        // No back button when opening directly
        showModalForm(category, type, false);
    }
}

// Open modal with category selection
function openModalWithCategory(category) {
    const modal = document.getElementById('container-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalForm = document.getElementById('modal-container-form');
    const modalSelection = document.getElementById('modal-template-selection');
    const modalCategoryTitle = document.getElementById('modal-template-category-title');
    const modalTypesContainer = document.getElementById('modal-template-types');
    
    if (!modal) return;
    
    selectedCategory = category;
    const categoryData = CONTAINER_TEMPLATES[category];
    
    if (!categoryData) {
        console.error('Category not found:', category);
        return;
    }
    
    // Show modal
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
    
    // Hide form, show selection
    if (modalForm) modalForm.style.display = 'none';
    if (modalSelection) modalSelection.style.display = 'block';
    
    // Set titles
    if (modalTitle) {
        modalTitle.textContent = `${categoryData.icon} ${categoryData.name}`;
    }
    
    if (modalCategoryTitle) {
        modalCategoryTitle.textContent = 'Select Template Type';
    }
    
    // Generate template type cards
    const types = Object.keys(categoryData.types).map(typeKey => {
        const type = categoryData.types[typeKey];
        return {
            id: typeKey,
            ...type
        };
    });
    
    if (modalTypesContainer) {
        modalTypesContainer.innerHTML = types.map(type => `
            <div class="template-card" data-type="${type.id}">
                <div class="template-card-icon">${getTypeIcon(category, type.id)}</div>
                <div class="template-card-title">${type.name}</div>
                <div class="template-card-description">
                    ${type.image ? `Image: ${type.image}` : 'Custom configuration'}
                </div>
            </div>
        `).join('');
        
        // Add click handlers to template cards
        const cards = modalTypesContainer.querySelectorAll('.template-card');
        cards.forEach(card => {
            card.addEventListener('click', () => {
                const type = card.dataset.type;
                selectModalTemplate(category, type);
            });
        });
    }
}

// Select template in modal
function selectModalTemplate(category, type) {
    selectedCategory = category;
    selectedType = type;
    currentTemplate = getTemplate(category, type);
    
    if (!currentTemplate) {
        console.error('Template not found:', category, type);
        return;
    }
    
    // Show back button since we came from template selection
    showModalForm(category, type, true);
}

// Show form in modal
function showModalForm(category, type, showBackButton = false) {
    const template = getTemplate(category, type);
    if (!template) return;
    
    const modalSelection = document.getElementById('modal-template-selection');
    const modalForm = document.getElementById('modal-container-form');
    const modalFormTitle = document.getElementById('modal-form-title');
    const modalDynamicFields = document.getElementById('modal-dynamic-form-fields');
    const modalTitle = document.getElementById('modal-title');
    const modalBackBtn = document.getElementById('modal-back-btn');
    
    // Hide selection, show form
    if (modalSelection) modalSelection.style.display = 'none';
    if (modalForm) modalForm.style.display = 'block';
    
    // Show/hide back button based on context
    if (modalBackBtn) {
        modalBackBtn.style.display = showBackButton ? 'inline-flex' : 'none';
    }
    
    // Set titles
    const categoryData = CONTAINER_TEMPLATES[category];
    if (modalTitle) {
        modalTitle.textContent = `${categoryData.icon} Create ${template.name}`;
    }
    
    if (modalFormTitle) {
        modalFormTitle.textContent = 'Configuration';
    }
    
    // Set hidden fields
    const modalCategoryInput = document.getElementById('modal-selected-category');
    const modalTypeInput = document.getElementById('modal-selected-type');
    if (modalCategoryInput) modalCategoryInput.value = category;
    if (modalTypeInput) modalTypeInput.value = type;
    
    // Generate form fields
    if (modalDynamicFields) {
        modalDynamicFields.innerHTML = generateFormFields(template);
    }
    
    // Setup dynamic interactions
    setupModalFormInteractions();
}

// Setup modal form interactions
function setupModalFormInteractions() {
    // Initialize disabled states for env var inputs in modal
    const modal = document.getElementById('container-modal');
    const envVarItems = modal.querySelectorAll('.env-var-item');
    
    envVarItems.forEach(item => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        const inputs = item.querySelectorAll('.env-var-input input:not([type="hidden"]), .env-var-input select');
        
        if (checkbox && !checkbox.disabled) {
            inputs.forEach(input => {
                input.disabled = !checkbox.checked;
            });
        }
    });
    
    // Initialize WASM validator
    if (window.initValidator) {
        window.initValidator().then(() => {
            console.log('✅ WASM validator initialized for form');
        }).catch(err => {
            console.warn('⚠️ WASM validator failed to initialize, using JavaScript fallback');
        });
    }
    
    // Real-time validation for container name
    const nameInput = document.getElementById('template-name');
    if (nameInput) {
        let validationTimeout;
        nameInput.addEventListener('input', async (e) => {
            clearTimeout(validationTimeout);
            
            // Show loading indicator
            showValidationStatus(nameInput, 'validating', '🔄 Checking...');
            
            validationTimeout = setTimeout(async () => {
                if (window.validateContainerName) {
                    const result = await window.validateContainerName(e.target.value);
                    
                    if (result.valid) {
                        showValidationStatus(nameInput, 'valid', '✓ Valid name');
                    } else {
                        showValidationStatus(nameInput, 'invalid', result.error);
                    }
                }
            }, 500); // Debounce 500ms
        });
    }
    
    // Real-time validation for subdomain
    const subdomainInput = document.getElementById('template-subdomain');
    if (subdomainInput) {
        let validationTimeout;
        subdomainInput.addEventListener('input', async (e) => {
            clearTimeout(validationTimeout);
            
            showValidationStatus(subdomainInput, 'validating', '🔄 Checking...');
            
            validationTimeout = setTimeout(async () => {
                if (window.validateSubdomain) {
                    const result = await window.validateSubdomain(e.target.value);
                    
                    if (result.valid) {
                        showValidationStatus(subdomainInput, 'valid', '✓ Valid subdomain');
                    } else {
                        showValidationStatus(subdomainInput, 'invalid', result.error);
                    }
                }
            }, 500);
        });
    }
    
    // Real-time validation for port
    const portInput = document.getElementById('template-port');
    if (portInput) {
        portInput.addEventListener('input', async (e) => {
            if (window.validatePort) {
                const result = await window.validatePort(e.target.value);
                
                if (result.valid) {
                    if (result.warning) {
                        showValidationStatus(portInput, 'warning', '⚠️ ' + result.warning);
                    } else {
                        showValidationStatus(portInput, 'valid', '✓ Valid port');
                    }
                } else {
                    showValidationStatus(portInput, 'invalid', result.error);
                }
            }
        });
    }
}

// Helper function to show validation status
function showValidationStatus(input, status, message) {
    // Remove existing validation message
    const existingMsg = input.parentElement.querySelector('.validation-message');
    if (existingMsg) {
        existingMsg.remove();
    }
    
    // Remove existing status classes
    input.classList.remove('input-valid', 'input-invalid', 'input-validating', 'input-warning');
    
    // Add new status
    if (status === 'valid') {
        input.classList.add('input-valid');
    } else if (status === 'invalid') {
        input.classList.add('input-invalid');
    } else if (status === 'validating') {
        input.classList.add('input-validating');
    } else if (status === 'warning') {
        input.classList.add('input-warning');
    }
    
    // Add validation message
    if (message) {
        const msgEl = document.createElement('div');
        msgEl.className = `validation-message validation-${status}`;
        msgEl.textContent = message;
        input.parentElement.appendChild(msgEl);
    }
}

// Back to modal template selection
function backToModalSelection() {
    const modalForm = document.getElementById('modal-container-form');
    const modalSelection = document.getElementById('modal-template-selection');
    
    if (modalForm) {
        modalForm.style.display = 'none';
        modalForm.reset();
    }
    
    if (modalSelection) {
        modalSelection.style.display = 'block';
    }
}

// Close modal
function closeModal() {
    const modal = document.getElementById('container-modal');
    const modalForm = document.getElementById('modal-container-form');
    const modalSelection = document.getElementById('modal-template-selection');
    
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = ''; // Restore scrolling
    }
    
    // Reset modal content
    if (modalForm) {
        modalForm.style.display = 'none';
        modalForm.reset();
    }
    
    if (modalSelection) {
        modalSelection.style.display = 'none';
    }
    
    // Reset state
    selectedCategory = null;
    selectedType = null;
    currentTemplate = null;
}

// Submit modal form
async function submitModalForm() {
    try {
        const form = document.getElementById('modal-container-form');
        const formData = new FormData(form);
        
        // Collect basic data
        const name = formData.get('name');
        const image = formData.get('image');
        const tag = formData.get('tag') || 'latest';
        const subdomain = formData.get('subdomain');
        const port = parseInt(formData.get('port'));
        const cpuLimit = formData.get('cpu_limit') ? parseFloat(formData.get('cpu_limit')) : null;
        const memoryLimit = formData.get('memory_limit') ? parseInt(formData.get('memory_limit')) : null;
        
        // Collect environment variables from modal
        const environment = {};
        const modal = document.getElementById('container-modal');
        const envVarItems = modal.querySelectorAll('.env-var-item');
        
        envVarItems.forEach(item => {
            const checkbox = item.querySelector('input[type="checkbox"]');
            const hiddenInput = item.querySelector('input[type="hidden"][data-key]');
            
            if (hiddenInput) {
                const key = hiddenInput.dataset.key;
                
                // For checkbox type env vars
                if (checkbox && !hiddenInput.dataset.input) {
                    if (checkbox.checked) {
                        environment[key] = 'true';
                    }
                }
                // For other types with checkbox toggle
                else if (checkbox && hiddenInput.dataset.input) {
                    if (checkbox.checked || checkbox.disabled) {
                        const inputId = hiddenInput.dataset.input;
                        const input = document.getElementById(inputId);
                        if (input && input.value) {
                            environment[key] = input.value;
                        }
                    }
                }
            }
        });
        
        // Get hidden env vars
        const hiddenEnvVars = modal.querySelectorAll('input[type="hidden"][data-key]');
        hiddenEnvVars.forEach(input => {
            if (!input.dataset.input && input.value) {
                environment[input.dataset.key] = input.value;
            }
        });
        
        // Validate required fields
        if (!name || !image || !subdomain || !port) {
            showNotification('Please fill in all required fields', 'error');
            return;
        }
        
        // Create container via GraphQL
        const mutation = `
            mutation CreateContainer($input: ContainerInput!) {
                createContainer(input: $input) {
                    id
                    name
                    status
                }
            }
        `;
        
        const variables = {
            input: {
                name,
                image,
                tag,
                subdomain,
                internalPort: port,
                environmentVars: environment,
                cpuLimit: cpuLimit ? cpuLimit.toString() : null,
                memoryLimit: memoryLimit ? memoryLimit.toString() + 'M' : null
            }
        };
        
        showNotification('Creating container...', 'info');
        
        const data = await graphqlRequest(mutation, variables);
        
        showNotification(`Container "${data.createContainer.name}" created successfully!`, 'success');
        
        // Close modal and refresh
        closeModal();
        loadAllContainers();
        loadDashboard();
        
    } catch (error) {
        console.error('Failed to create container:', error);
        showNotification('Failed to create container: ' + error.message, 'error');
    }
}

// Initialize template system when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initTemplateSystem();
});

// Export template functions
window.toggleEnvVarInput = toggleEnvVarInput;
window.openModal = openModal;
window.closeModal = closeModal;

// Export functions for inline onclick handlers
window.startContainer = startContainer;
window.stopContainer = stopContainer;
window.deleteContainer = deleteContainer;
window.refreshContainers = refreshContainers;
