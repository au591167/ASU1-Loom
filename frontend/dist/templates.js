// Container Templates Configuration
// Defines pre-configured templates for different container types

const CONTAINER_TEMPLATES = {
    development: {
        name: 'Development Container',
        icon: '🖥️',
        description: 'Web development environments (Node.js, Python, PHP, etc.)',
        types: {
            nodejs: {
                name: 'Node.js',
                image: 'node',
                tags: ['20-alpine', '18-alpine', '16-alpine', 'latest'],
                defaultTag: '20-alpine',
                defaultPort: 3000,
                envVars: [
                    { key: 'NODE_ENV', label: 'Environment', type: 'select', options: ['development', 'production', 'test'], default: 'production' },
                    { key: 'PORT', label: 'Port', type: 'number', default: 3000 },
                    { key: 'DATABASE_URL', label: 'Database URL', type: 'text', optional: true },
                    { key: 'API_KEY', label: 'API Key', type: 'text', optional: true }
                ]
            },
            python: {
                name: 'Python',
                image: 'python',
                tags: ['3.11-slim', '3.10-slim', '3.9-slim', 'latest'],
                defaultTag: '3.11-slim',
                defaultPort: 8000,
                envVars: [
                    { key: 'PYTHONUNBUFFERED', label: 'Unbuffered Output', type: 'checkbox', default: true },
                    { key: 'DATABASE_URL', label: 'Database URL', type: 'text', optional: true },
                    { key: 'SECRET_KEY', label: 'Secret Key', type: 'text', optional: true }
                ]
            },
            php: {
                name: 'PHP',
                image: 'php',
                tags: ['8.2-apache', '8.1-apache', '8.0-apache', 'latest'],
                defaultTag: '8.2-apache',
                defaultPort: 80,
                envVars: [
                    { key: 'PHP_MEMORY_LIMIT', label: 'Memory Limit', type: 'text', default: '256M' },
                    { key: 'DATABASE_HOST', label: 'Database Host', type: 'text', optional: true },
                    { key: 'DATABASE_NAME', label: 'Database Name', type: 'text', optional: true }
                ]
            },
            nginx: {
                name: 'Nginx',
                image: 'nginx',
                tags: ['alpine', 'latest', 'stable'],
                defaultTag: 'alpine',
                defaultPort: 80,
                envVars: []
            }
        }
    },
    
    minecraft: {
        name: 'Minecraft Server',
        icon: '⛏️',
        description: 'Minecraft game servers (Vanilla, Paper, Spigot, etc.)',
        types: {
            vanilla: {
                name: 'Vanilla',
                image: 'itzg/minecraft-server',
                tags: ['latest', 'java17', 'java11'],
                defaultTag: 'latest',
                defaultPort: 25565,
                envVars: [
                    { key: 'EULA', label: 'Accept EULA', type: 'checkbox', default: true, required: true },
                    { key: 'VERSION', label: 'Minecraft Version', type: 'select', options: ['1.20.4', '1.20.1', '1.19.4', '1.19.2', 'LATEST'], default: 'LATEST' },
                    { key: 'DIFFICULTY', label: 'Difficulty', type: 'select', options: ['peaceful', 'easy', 'normal', 'hard'], default: 'normal' },
                    { key: 'MODE', label: 'Game Mode', type: 'select', options: ['survival', 'creative', 'adventure', 'spectator'], default: 'survival' },
                    { key: 'MAX_PLAYERS', label: 'Max Players', type: 'number', default: 20, min: 1, max: 100 },
                    { key: 'PVP', label: 'Enable PVP', type: 'checkbox', default: true },
                    { key: 'ONLINE_MODE', label: 'Online Mode', type: 'checkbox', default: true },
                    { key: 'MOTD', label: 'Server MOTD', type: 'text', default: 'A Minecraft Server', optional: true }
                ],
                memory: { min: 1024, recommended: 2048, max: 8192 }
            },
            paper: {
                name: 'Paper',
                image: 'itzg/minecraft-server',
                tags: ['latest'],
                defaultTag: 'latest',
                defaultPort: 25565,
                envVars: [
                    { key: 'EULA', label: 'Accept EULA', type: 'checkbox', default: true, required: true },
                    { key: 'TYPE', label: 'Server Type', type: 'hidden', default: 'PAPER' },
                    { key: 'VERSION', label: 'Minecraft Version', type: 'select', options: ['1.20.4', '1.20.1', '1.19.4', 'LATEST'], default: 'LATEST' },
                    { key: 'DIFFICULTY', label: 'Difficulty', type: 'select', options: ['peaceful', 'easy', 'normal', 'hard'], default: 'normal' },
                    { key: 'MODE', label: 'Game Mode', type: 'select', options: ['survival', 'creative', 'adventure', 'spectator'], default: 'survival' },
                    { key: 'MAX_PLAYERS', label: 'Max Players', type: 'number', default: 20, min: 1, max: 100 },
                    { key: 'PVP', label: 'Enable PVP', type: 'checkbox', default: true }
                ],
                memory: { min: 2048, recommended: 4096, max: 8192 }
            },
            spigot: {
                name: 'Spigot',
                image: 'itzg/minecraft-server',
                tags: ['latest'],
                defaultTag: 'latest',
                defaultPort: 25565,
                envVars: [
                    { key: 'EULA', label: 'Accept EULA', type: 'checkbox', default: true, required: true },
                    { key: 'TYPE', label: 'Server Type', type: 'hidden', default: 'SPIGOT' },
                    { key: 'VERSION', label: 'Minecraft Version', type: 'select', options: ['1.20.4', '1.20.1', '1.19.4', 'LATEST'], default: 'LATEST' },
                    { key: 'DIFFICULTY', label: 'Difficulty', type: 'select', options: ['peaceful', 'easy', 'normal', 'hard'], default: 'normal' },
                    { key: 'MAX_PLAYERS', label: 'Max Players', type: 'number', default: 20 }
                ],
                memory: { min: 2048, recommended: 4096, max: 8192 }
            },
            forge: {
                name: 'Forge',
                image: 'itzg/minecraft-server',
                tags: ['latest', 'java21', 'java17'],
                defaultTag: 'latest',
                defaultPort: 25565,
                envVars: [
                    { key: 'EULA', label: 'Accept EULA', type: 'checkbox', default: true, required: true },
                    { key: 'TYPE', label: 'Server Type', type: 'hidden', default: 'FORGE' },
                    { key: 'VERSION', label: 'Minecraft Version', type: 'select', options: ['1.20.4', '1.20.1', '1.19.4', '1.19.2', 'LATEST'], default: 'LATEST' },
                    { key: 'FORGE_VERSION', label: 'Forge Version', type: 'text', default: 'RECOMMENDED', optional: true },
                    { key: 'DIFFICULTY', label: 'Difficulty', type: 'select', options: ['peaceful', 'easy', 'normal', 'hard'], default: 'normal' },
                    { key: 'MAX_PLAYERS', label: 'Max Players', type: 'number', default: 20, min: 1, max: 100 }
                ],
                memory: { min: 3072, recommended: 6144, max: 16384 }
            },
            neoforge: {
                name: 'NeoForge',
                image: 'itzg/minecraft-server',
                tags: ['latest', 'java21'],
                defaultTag: 'latest',
                defaultPort: 25565,
                envVars: [
                    { key: 'EULA', label: 'Accept EULA', type: 'checkbox', default: true, required: true },
                    { key: 'TYPE', label: 'Server Type', type: 'hidden', default: 'NEOFORGE' },
                    { key: 'VERSION', label: 'Minecraft Version', type: 'select', options: ['1.20.4', '1.20.1', 'LATEST'], default: 'LATEST' },
                    { key: 'NEOFORGE_VERSION', label: 'NeoForge Version', type: 'text', default: 'LATEST', optional: true },
                    { key: 'DIFFICULTY', label: 'Difficulty', type: 'select', options: ['peaceful', 'easy', 'normal', 'hard'], default: 'normal' },
                    { key: 'MAX_PLAYERS', label: 'Max Players', type: 'number', default: 20, min: 1, max: 100 }
                ],
                memory: { min: 3072, recommended: 6144, max: 16384 }
            },
            fabric: {
                name: 'Fabric',
                image: 'itzg/minecraft-server',
                tags: ['latest', 'java21', 'java17'],
                defaultTag: 'latest',
                defaultPort: 25565,
                envVars: [
                    { key: 'EULA', label: 'Accept EULA', type: 'checkbox', default: true, required: true },
                    { key: 'TYPE', label: 'Server Type', type: 'hidden', default: 'FABRIC' },
                    { key: 'VERSION', label: 'Minecraft Version', type: 'select', options: ['1.20.4', '1.20.1', '1.19.4', 'LATEST'], default: 'LATEST' },
                    { key: 'FABRIC_LOADER_VERSION', label: 'Fabric Loader Version', type: 'text', default: 'LATEST', optional: true },
                    { key: 'DIFFICULTY', label: 'Difficulty', type: 'select', options: ['peaceful', 'easy', 'normal', 'hard'], default: 'normal' },
                    { key: 'MAX_PLAYERS', label: 'Max Players', type: 'number', default: 20, min: 1, max: 100 }
                ],
                memory: { min: 2048, recommended: 4096, max: 12288 }
            }
        }
    },
    
    gameserver: {
        name: 'Game Server',
        icon: '🎮',
        description: 'Other game servers (Valheim, Terraria, etc.)',
        types: {
            valheim: {
                name: 'Valheim',
                image: 'lloesche/valheim-server',
                tags: ['latest'],
                defaultTag: 'latest',
                defaultPort: 2456,
                envVars: [
                    { key: 'SERVER_NAME', label: 'Server Name', type: 'text', default: 'My Valheim Server', required: true },
                    { key: 'WORLD_NAME', label: 'World Name', type: 'text', default: 'Dedicated', required: true },
                    { key: 'SERVER_PASS', label: 'Server Password', type: 'password', required: true },
                    { key: 'SERVER_PUBLIC', label: 'Public Server', type: 'checkbox', default: false }
                ],
                memory: { min: 2048, recommended: 4096, max: 8192 }
            },
            terraria: {
                name: 'Terraria',
                image: 'ryshe/terraria',
                tags: ['latest', 'vanilla'],
                defaultTag: 'latest',
                defaultPort: 7777,
                envVars: [
                    { key: 'WORLD', label: 'World Name', type: 'text', default: 'world', required: true },
                    { key: 'PASS', label: 'Server Password', type: 'password', optional: true },
                    { key: 'MAXPLAYERS', label: 'Max Players', type: 'number', default: 8, min: 1, max: 255 }
                ],
                memory: { min: 512, recommended: 1024, max: 2048 }
            }
        }
    },
    
    custom: {
        name: 'Custom Container',
        icon: '📦',
        description: 'Advanced: Specify any Docker image',
        types: {
            custom: {
                name: 'Custom',
                image: '',
                tags: [],
                defaultTag: 'latest',
                defaultPort: 80,
                envVars: [
                    { key: 'TZ', label: 'Timezone', type: 'text', default: 'UTC', optional: true },
                    { key: 'PUID', label: 'User ID (PUID)', type: 'number', default: '1000', optional: true },
                    { key: 'PGID', label: 'Group ID (PGID)', type: 'number', default: '1000', optional: true },
                    { key: 'UMASK', label: 'File Permission Mask (UMASK)', type: 'text', default: '022', optional: true },
                    { key: 'LOG_LEVEL', label: 'Log Level', type: 'select', options: ['debug', 'info', 'warning', 'error'], default: 'info', optional: true },
                    { key: 'RESTART_POLICY', label: 'Auto Restart on Failure', type: 'checkbox', default: true, optional: true }
                ],
                advanced: true
            }
        }
    }
};

// Helper function to get template by category and type
function getTemplate(category, type) {
    return CONTAINER_TEMPLATES[category]?.types[type] || null;
}

// Helper function to get all categories
function getCategories() {
    return Object.keys(CONTAINER_TEMPLATES).map(key => ({
        id: key,
        ...CONTAINER_TEMPLATES[key]
    }));
}

// Helper function to get types for a category
function getTypesForCategory(category) {
    const cat = CONTAINER_TEMPLATES[category];
    if (!cat) return [];
    
    return Object.keys(cat.types).map(key => ({
        id: key,
        ...cat.types[key]
    }));
}
