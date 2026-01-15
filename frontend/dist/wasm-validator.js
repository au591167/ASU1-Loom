// WASM-powered validation using Pyodide
let validatorReady = false;
let pyodideInstance = null;

async function initValidator() {
    if (validatorReady) return pyodideInstance;
    
    try {
        console.log('🔧 Initializing WASM validator...');
        pyodideInstance = await loadPyodide();
        
        // Load validation logic
        await pyodideInstance.runPythonAsync(`
import re
import json

def validate_container_name(name):
    """Validate container name according to Docker standards"""
    if not name:
        return {"valid": False, "error": "Name cannot be empty"}
    
    if len(name) < 3:
        return {"valid": False, "error": "Name must be at least 3 characters"}
    
    if len(name) > 63:
        return {"valid": False, "error": "Name must be less than 63 characters"}
    
    # Docker naming rules: lowercase, numbers, hyphens
    if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', name):
        return {"valid": False, "error": "Only lowercase letters, numbers, and hyphens allowed"}
    
    # Cannot start or end with hyphen
    if name.startswith('-') or name.endswith('-'):
        return {"valid": False, "error": "Cannot start or end with hyphen"}
    
    # Check for consecutive hyphens
    if '--' in name:
        return {"valid": False, "error": "Cannot have consecutive hyphens"}
    
    return {"valid": True, "error": None}

def validate_subdomain(subdomain):
    """Validate subdomain according to DNS standards"""
    if not subdomain:
        return {"valid": False, "error": "Subdomain cannot be empty"}
    
    if len(subdomain) < 2:
        return {"valid": False, "error": "Subdomain must be at least 2 characters"}
    
    if len(subdomain) > 63:
        return {"valid": False, "error": "Subdomain must be less than 63 characters"}
    
    # DNS naming rules
    if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', subdomain):
        return {"valid": False, "error": "Only lowercase letters, numbers, and hyphens allowed"}
    
    # Reserved subdomains
    reserved = ['www', 'api', 'admin', 'mail', 'ftp', 'localhost', 'traefik']
    if subdomain in reserved:
        return {"valid": False, "error": f"'{subdomain}' is a reserved subdomain"}
    
    return {"valid": True, "error": None}

def validate_port(port):
    """Validate port number"""
    try:
        port_num = int(port)
        if port_num < 1 or port_num > 65535:
            return {"valid": False, "error": "Port must be between 1 and 65535"}
        
        # Common reserved ports
        reserved_ports = [22, 25, 80, 443, 3306, 5432, 8080]
        if port_num in reserved_ports:
            return {"valid": True, "warning": f"Port {port_num} is commonly used by other services"}
        
        return {"valid": True, "error": None}
    except:
        return {"valid": False, "error": "Port must be a number"}
        `);
        
        validatorReady = true;
        console.log('✅ WASM Validator ready');
        
        return pyodideInstance;
    } catch (error) {
        console.error('❌ Failed to initialize WASM validator:', error);
        return null;
    }
}

// Validate container name using WASM
async function validateContainerName(name) {
    const py = await initValidator();
    if (!py) {
        // Fallback to JavaScript validation
        return jsValidateContainerName(name);
    }
    
    try {
        // Set the name in Python globals to avoid injection issues
        py.globals.set('input_name', name);
        const result = await py.runPythonAsync(`
import json
json.dumps(validate_container_name(input_name))
        `);
        return JSON.parse(result);
    } catch (error) {
        console.error('WASM validation error:', error);
        return jsValidateContainerName(name);
    }
}

// Validate subdomain using WASM
async function validateSubdomain(subdomain) {
    const py = await initValidator();
    if (!py) {
        return jsValidateSubdomain(subdomain);
    }
    
    try {
        // Set the subdomain in Python globals to avoid injection issues
        py.globals.set('input_subdomain', subdomain);
        const result = await py.runPythonAsync(`
import json
json.dumps(validate_subdomain(input_subdomain))
        `);
        return JSON.parse(result);
    } catch (error) {
        console.error('WASM validation error:', error);
        return jsValidateSubdomain(subdomain);
    }
}

// Validate port using WASM
async function validatePort(port) {
    const py = await initValidator();
    if (!py) {
        return jsValidatePort(port);
    }
    
    try {
        // Set the port in Python globals to avoid injection issues
        py.globals.set('input_port', port);
        const result = await py.runPythonAsync(`
import json
json.dumps(validate_port(input_port))
        `);
        return JSON.parse(result);
    } catch (error) {
        console.error('WASM validation error:', error);
        return jsValidatePort(port);
    }
}

// JavaScript fallback validations
function jsValidateContainerName(name) {
    if (!name) return {valid: false, error: "Name cannot be empty"};
    if (name.length < 3) return {valid: false, error: "Name must be at least 3 characters"};
    if (!/^[a-z0-9][a-z0-9-]*[a-z0-9]$/.test(name)) {
        return {valid: false, error: "Only lowercase letters, numbers, and hyphens allowed"};
    }
    return {valid: true, error: null};
}

function jsValidateSubdomain(subdomain) {
    if (!subdomain) return {valid: false, error: "Subdomain cannot be empty"};
    if (subdomain.length < 2) return {valid: false, error: "Subdomain must be at least 2 characters"};
    if (!/^[a-z0-9][a-z0-9-]*[a-z0-9]$/.test(subdomain)) {
        return {valid: false, error: "Only lowercase letters, numbers, and hyphens allowed"};
    }
    const reserved = ['www', 'api', 'admin', 'mail', 'ftp', 'localhost', 'traefik'];
    if (reserved.includes(subdomain)) {
        return {valid: false, error: `'${subdomain}' is a reserved subdomain`};
    }
    return {valid: true, error: null};
}

function jsValidatePort(port) {
    const portNum = parseInt(port);
    if (isNaN(portNum) || portNum < 1 || portNum > 65535) {
        return {valid: false, error: "Port must be between 1 and 65535"};
    }
    return {valid: true, error: null};
}

// Export functions
window.validateContainerName = validateContainerName;
window.validateSubdomain = validateSubdomain;
window.validatePort = validatePort;
window.initValidator = initValidator;
