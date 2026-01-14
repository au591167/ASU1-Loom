"""
ASU1-Loom Diagram Generator
Generates all presentation diagrams as PNG images

Usage:
    python generate_diagrams.py

Output:
    Diagrams/ folder with all generated images

Requirements:
    pip install graphviz pillow
"""

from graphviz import Digraph
from PIL import Image, ImageDraw, ImageFont
import os

# Create output directory
OUTPUT_DIR = "Diagrams"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Color scheme
COLORS = {
    'docker_blue': '#2496ED',
    'traefik_orange': '#FF6600',
    'graphql_pink': '#E10098',
    'success_green': '#28A745',
    'warning_yellow': '#FFC107',
    'error_red': '#DC3545',
    'light_gray': '#F5F5F5',
    'dark_gray': '#6C757D',
    'white': '#FFFFFF',
    'black': '#000000'
}

print("🎨 ASU1-Loom Diagram Generator")
print("=" * 50)

# ============================================================================
# DIAGRAM 1: System Architecture Overview
# ============================================================================
print("\n📊 Generating: 1_System_Architecture.png")

arch = Digraph('Architecture', format='png')
arch.attr(rankdir='TB', bgcolor='white', fontname='Arial')
arch.attr('node', shape='box', style='rounded,filled', fontname='Arial')

# Client Layer
with arch.subgraph(name='cluster_client') as c:
    c.attr(label='Client Layer', style='filled', color='lightgray')
    c.node('browser', 'Web Browser\n(User)', fillcolor=COLORS['light_gray'])
    c.node('wasm', 'WebAssembly Frontend\n(Pyodide + Python)', fillcolor=COLORS['graphql_pink'], fontcolor='white')

# Proxy Layer
with arch.subgraph(name='cluster_proxy') as c:
    c.attr(label='Reverse Proxy Layer', style='filled', color='lightgray')
    c.node('traefik', 'Traefik v2.11\nAutomatic Routing', fillcolor=COLORS['traefik_orange'], fontcolor='white')

# Backend Layer
with arch.subgraph(name='cluster_backend') as c:
    c.attr(label='Backend Layer', style='filled', color='lightgray')
    c.node('fastapi', 'FastAPI\nGraphQL API', fillcolor=COLORS['docker_blue'], fontcolor='white')
    c.node('docker_mgr', 'Docker Manager\nContainer Lifecycle', fillcolor=COLORS['docker_blue'], fontcolor='white')
    c.node('postgres', 'PostgreSQL\nMetadata Storage', fillcolor=COLORS['docker_blue'], fontcolor='white')

# Container Layer
with arch.subgraph(name='cluster_containers') as c:
    c.attr(label='Container Runtime Layer', style='filled', color='lightgray')
    c.node('docker', 'Docker Engine', fillcolor=COLORS['success_green'], fontcolor='white')
    c.node('containers', 'User Containers\n(game, grafana, etc.)', fillcolor=COLORS['success_green'], fontcolor='white')

# Connections
arch.edge('browser', 'wasm', label='Loads')
arch.edge('wasm', 'traefik', label='HTTP/GraphQL')
arch.edge('traefik', 'fastapi', label='Routes API')
arch.edge('traefik', 'containers', label='Routes Subdomains')
arch.edge('fastapi', 'docker_mgr', label='Calls')
arch.edge('fastapi', 'postgres', label='Queries')
arch.edge('docker_mgr', 'docker', label='Docker Socket')
arch.edge('docker', 'containers', label='Manages')

arch.render(f'{OUTPUT_DIR}/1_System_Architecture', cleanup=True)
print("✅ Saved: 1_System_Architecture.png")

# ============================================================================
# DIAGRAM 2: Container Creation Flow
# ============================================================================
print("\n📊 Generating: 2_Container_Creation_Flow.png")

flow = Digraph('ContainerFlow', format='png')
flow.attr(rankdir='TB', bgcolor='white', fontname='Arial')
flow.attr('node', shape='box', style='rounded,filled', fontname='Arial')

# Steps
flow.node('user', '1. User\nFills Form', fillcolor=COLORS['light_gray'])
flow.node('frontend', '2. Frontend\nGraphQL Mutation', fillcolor=COLORS['graphql_pink'], fontcolor='white')
flow.node('nginx', '3. Nginx\nProxy Request', fillcolor=COLORS['success_green'], fontcolor='white')
flow.node('backend', '4. Backend\nGraphQL Resolver', fillcolor=COLORS['docker_blue'], fontcolor='white')
flow.node('docker_mgr', '5. Docker Manager\nGenerate Labels', fillcolor=COLORS['docker_blue'], fontcolor='white')
flow.node('docker_engine', '6. Docker Engine\nCreate Container', fillcolor=COLORS['success_green'], fontcolor='white')
flow.node('database', '7. Database\nSave Metadata', fillcolor=COLORS['docker_blue'], fontcolor='white')
flow.node('traefik_discover', '8. Traefik\nAuto-Discovery', fillcolor=COLORS['traefik_orange'], fontcolor='white')
flow.node('response', '9. Response\nUI Update', fillcolor=COLORS['graphql_pink'], fontcolor='white')

# Flow
flow.edge('user', 'frontend', label='Submit')
flow.edge('frontend', 'nginx', label='POST /graphql')
flow.edge('nginx', 'backend', label='Proxy')
flow.edge('backend', 'docker_mgr', label='Call')
flow.edge('docker_mgr', 'docker_engine', label='Create')
flow.edge('docker_engine', 'database', label='Save')
flow.edge('database', 'traefik_discover', label='Detect')
flow.edge('traefik_discover', 'response', label='Return')
flow.edge('response', 'user', label='Display', style='dashed')

flow.render(f'{OUTPUT_DIR}/2_Container_Creation_Flow', cleanup=True)
print("✅ Saved: 2_Container_Creation_Flow.png")

# ============================================================================
# DIAGRAM 3: Technology Stack Layers
# ============================================================================
print("\n📊 Generating: 3_Technology_Stack.png")

stack = Digraph('TechStack', format='png')
stack.attr(rankdir='TB', bgcolor='white', fontname='Arial')
stack.attr('node', shape='box', style='filled', fontname='Arial', width='4')

# Layers
stack.node('presentation', 'Presentation Layer\nHTML5 • CSS3 • JavaScript • WebAssembly', 
           fillcolor=COLORS['graphql_pink'], fontcolor='white')
stack.node('api', 'API Layer\nGraphQL (Strawberry) • FastAPI • Uvicorn', 
           fillcolor=COLORS['docker_blue'], fontcolor='white')
stack.node('business', 'Business Logic Layer\ndocker_manager.py • modpack_service.py', 
           fillcolor=COLORS['docker_blue'], fontcolor='white')
stack.node('data', 'Data Layer\nPostgreSQL • SQLAlchemy', 
           fillcolor=COLORS['success_green'], fontcolor='white')
stack.node('runtime', 'Runtime Layer\nDocker Engine • Containers • Networks', 
           fillcolor=COLORS['success_green'], fontcolor='white')

# Connections
stack.edge('presentation', 'api', label='HTTP/GraphQL')
stack.edge('api', 'business', label='Function Calls')
stack.edge('business', 'data', label='Queries')
stack.edge('business', 'runtime', label='Docker API')

stack.render(f'{OUTPUT_DIR}/3_Technology_Stack', cleanup=True)
print("✅ Saved: 3_Technology_Stack.png")

# ============================================================================
# DIAGRAM 4: Network Topology
# ============================================================================
print("\n📊 Generating: 4_Network_Topology.png")

network = Digraph('Network', format='png')
network.attr(rankdir='LR', bgcolor='white', fontname='Arial')
network.attr('node', shape='box', style='rounded,filled', fontname='Arial')

# Host
with network.subgraph(name='cluster_host') as c:
    c.attr(label='Host: pandaserver.ddns.net (85.24.3.105)', style='filled', color='lightblue')
    
    # Docker Network
    with c.subgraph(name='cluster_docker_net') as d:
        d.attr(label='loom_network (172.18.0.0/16)', style='filled', color='lightgray')
        d.node('traefik_net', 'Traefik\n172.18.0.2\nPorts: 80,443,8080', fillcolor=COLORS['traefik_orange'], fontcolor='white')
        d.node('backend_net', 'Backend\n172.18.0.3\nPort: 8000', fillcolor=COLORS['docker_blue'], fontcolor='white')
        d.node('frontend_net', 'Frontend\n172.18.0.4\nPort: 3000', fillcolor=COLORS['graphql_pink'], fontcolor='white')
        d.node('container1', 'game-2048\n172.18.0.5\nPort: 80', fillcolor=COLORS['success_green'], fontcolor='white')
        d.node('container2', 'grafana\n172.18.0.6\nPort: 3000', fillcolor=COLORS['success_green'], fontcolor='white')

# Internet
network.node('internet', 'Internet\nDNS: *.pandaserver.ddns.net', shape='cloud', fillcolor='lightblue')

# Connections
network.edge('internet', 'traefik_net', label='Port 80/443')
network.edge('traefik_net', 'backend_net', label='API Routing')
network.edge('traefik_net', 'frontend_net', label='Dashboard')
network.edge('traefik_net', 'container1', label='game.domain')
network.edge('traefik_net', 'container2', label='grafana.domain')

network.render(f'{OUTPUT_DIR}/4_Network_Topology', cleanup=True)
print("✅ Saved: 4_Network_Topology.png")

# ============================================================================
# DIAGRAM 5: Request Routing Flow
# ============================================================================
print("\n📊 Generating: 5_Request_Routing.png")

routing = Digraph('Routing', format='png')
routing.attr(rankdir='TB', bgcolor='white', fontname='Arial')
routing.attr('node', shape='box', style='rounded,filled', fontname='Arial')

# User requests
routing.node('user_req', 'User Request', shape='ellipse', fillcolor=COLORS['light_gray'])

# Different paths
routing.node('dns', 'DNS Resolution\n*.pandaserver.ddns.net\n→ 85.24.3.105', fillcolor='lightblue')
routing.node('traefik_route', 'Traefik\nPort 80', fillcolor=COLORS['traefik_orange'], fontcolor='white')

# Routing decisions
routing.node('route1', 'pandaserver.ddns.net\n→ Frontend', fillcolor=COLORS['graphql_pink'], fontcolor='white')
routing.node('route2', 'pandaserver.ddns.net/graphql\n→ Backend API', fillcolor=COLORS['docker_blue'], fontcolor='white')
routing.node('route3', 'game.pandaserver.ddns.net\n→ game-2048 Container', fillcolor=COLORS['success_green'], fontcolor='white')
routing.node('route4', 'grafana.pandaserver.ddns.net\n→ grafana Container', fillcolor=COLORS['success_green'], fontcolor='white')

# Flow
routing.edge('user_req', 'dns')
routing.edge('dns', 'traefik_route')
routing.edge('traefik_route', 'route1', label='Host Match')
routing.edge('traefik_route', 'route2', label='Path Match')
routing.edge('traefik_route', 'route3', label='Subdomain Match')
routing.edge('traefik_route', 'route4', label='Subdomain Match')

routing.render(f'{OUTPUT_DIR}/5_Request_Routing', cleanup=True)
print("✅ Saved: 5_Request_Routing.png")

# ============================================================================
# DIAGRAM 6: Data Flow - GraphQL Query
# ============================================================================
print("\n📊 Generating: 6_GraphQL_Data_Flow.png")

graphql_flow = Digraph('GraphQLFlow', format='png')
graphql_flow.attr(rankdir='LR', bgcolor='white', fontname='Arial')
graphql_flow.attr('node', shape='box', style='rounded,filled', fontname='Arial')

# Components
graphql_flow.node('browser_gql', 'Browser\nGraphQL Query', fillcolor=COLORS['light_gray'])
graphql_flow.node('graphql_endpoint', 'GraphQL Endpoint\n/graphql', fillcolor=COLORS['graphql_pink'], fontcolor='white')
graphql_flow.node('resolver', 'Resolver\n@strawberry.field', fillcolor=COLORS['docker_blue'], fontcolor='white')
graphql_flow.node('service', 'Service Layer\ndocker_manager', fillcolor=COLORS['docker_blue'], fontcolor='white')
graphql_flow.node('docker_api', 'Docker API\nSocket', fillcolor=COLORS['success_green'], fontcolor='white')
graphql_flow.node('db_query', 'Database\nPostgreSQL', fillcolor=COLORS['success_green'], fontcolor='white')
graphql_flow.node('response_gql', 'JSON Response', fillcolor=COLORS['graphql_pink'], fontcolor='white')

# Flow
graphql_flow.edge('browser_gql', 'graphql_endpoint', label='POST')
graphql_flow.edge('graphql_endpoint', 'resolver', label='Parse')
graphql_flow.edge('resolver', 'service', label='Call')
graphql_flow.edge('service', 'docker_api', label='Query')
graphql_flow.edge('service', 'db_query', label='Query')
graphql_flow.edge('db_query', 'resolver', label='Data', style='dashed')
graphql_flow.edge('docker_api', 'resolver', label='Data', style='dashed')
graphql_flow.edge('resolver', 'response_gql', label='Format')
graphql_flow.edge('response_gql', 'browser_gql', label='Return', style='dashed')

graphql_flow.render(f'{OUTPUT_DIR}/6_GraphQL_Data_Flow', cleanup=True)
print("✅ Saved: 6_GraphQL_Data_Flow.png")

# ============================================================================
# DIAGRAM 7: Traefik Label Generation
# ============================================================================
print("\n📊 Generating: 7_Traefik_Labels.png")

labels = Digraph('TraefikLabels', format='png')
labels.attr(rankdir='TB', bgcolor='white', fontname='Arial')
labels.attr('node', shape='box', style='rounded,filled', fontname='Arial')

# Process
labels.node('input', 'Input:\nname="game-2048"\nsubdomain="game"\nport=80', fillcolor=COLORS['light_gray'])
labels.node('env', 'Read Environment:\nTRAEFIK_DOMAIN=\npandaserver.ddns.net', fillcolor=COLORS['warning_yellow'])
labels.node('generate', 'Generate Labels:\ntraefik.enable=true\ntraefik.http.routers.game-2048.rule=\n  Host(`game.pandaserver.ddns.net`)\ntraefik.http.services.game-2048\n  .loadbalancer.server.port=80', fillcolor=COLORS['docker_blue'], fontcolor='white')
labels.node('attach', 'Attach to Container', fillcolor=COLORS['success_green'], fontcolor='white')
labels.node('discover', 'Traefik Auto-Discovery', fillcolor=COLORS['traefik_orange'], fontcolor='white')
labels.node('route', 'Route Configured:\ngame.pandaserver.ddns.net\n→ container:80', fillcolor=COLORS['success_green'], fontcolor='white')

# Flow
labels.edge('input', 'env')
labels.edge('env', 'generate')
labels.edge('generate', 'attach')
labels.edge('attach', 'discover')
labels.edge('discover', 'route')

labels.render(f'{OUTPUT_DIR}/7_Traefik_Labels', cleanup=True)
print("✅ Saved: 7_Traefik_Labels.png")

# ============================================================================
# DIAGRAM 8: Security Architecture
# ============================================================================
print("\n📊 Generating: 8_Security_Architecture.png")

security = Digraph('Security', format='png')
security.attr(rankdir='TB', bgcolor='white', fontname='Arial')
security.attr('node', shape='box', style='rounded,filled', fontname='Arial')

# Layers
security.node('threats', 'External Threats\nDDoS • SQL Injection • XSS', fillcolor=COLORS['error_red'], fontcolor='white')
security.node('firewall', 'Firewall (UFW)\nAllow: 80, 443, 8000\nDeny: All Others', fillcolor=COLORS['warning_yellow'])
security.node('traefik_sec', 'Traefik\nSSL/TLS (future)\nRate Limiting (future)', fillcolor=COLORS['traefik_orange'], fontcolor='white')
security.node('app_sec', 'Application Layer\nCORS • Input Validation\nAuthentication (future)', fillcolor=COLORS['docker_blue'], fontcolor='white')
security.node('container_sec', 'Container Isolation\nDocker Networks\nResource Limits', fillcolor=COLORS['success_green'], fontcolor='white')
security.node('data_sec', 'Data Layer\nEncrypted Connections\nAccess Control', fillcolor=COLORS['success_green'], fontcolor='white')

# Flow
security.edge('threats', 'firewall', label='Blocked')
security.edge('firewall', 'traefik_sec', label='Allowed Ports')
security.edge('traefik_sec', 'app_sec', label='Filtered')
security.edge('app_sec', 'container_sec', label='Validated')
security.edge('app_sec', 'data_sec', label='Validated')

security.render(f'{OUTPUT_DIR}/8_Security_Architecture', cleanup=True)
print("✅ Saved: 8_Security_Architecture.png")

# ============================================================================
# DIAGRAM 9: Deployment Architecture
# ============================================================================
print("\n📊 Generating: 9_Deployment_Architecture.png")

deploy = Digraph('Deployment', format='png')
deploy.attr(rankdir='TB', bgcolor='white', fontname='Arial')
deploy.attr('node', shape='box', style='rounded,filled', fontname='Arial')

# Server
with deploy.subgraph(name='cluster_server') as c:
    c.attr(label='Production Server\npandaserver.ddns.net (85.24.3.105)', style='filled', color='lightblue')
    
    # Docker Compose
    with c.subgraph(name='cluster_compose') as d:
        d.attr(label='Docker Compose', style='filled', color='lightgray')
        d.node('traefik_deploy', 'Traefik Container', fillcolor=COLORS['traefik_orange'], fontcolor='white')
        d.node('backend_deploy', 'Backend Container', fillcolor=COLORS['docker_blue'], fontcolor='white')
        d.node('frontend_deploy', 'Frontend Container', fillcolor=COLORS['graphql_pink'], fontcolor='white')
        d.node('user_containers', 'User Containers', fillcolor=COLORS['success_green'], fontcolor='white')

# External services
deploy.node('noip', 'No-IP DNS\nDynamic DNS\nWildcard Enabled', shape='ellipse', fillcolor='lightblue')
deploy.node('router', 'Internet Router\nPort Forwarding\n80, 443, 8000', shape='ellipse', fillcolor='lightblue')

# Connections
deploy.edge('noip', 'router', label='DNS Resolution')
deploy.edge('router', 'traefik_deploy', label='Incoming Traffic')
deploy.edge('traefik_deploy', 'backend_deploy', label='API Routing')
deploy.edge('traefik_deploy', 'frontend_deploy', label='Dashboard')
deploy.edge('traefik_deploy', 'user_containers', label='Subdomain Routing')

deploy.render(f'{OUTPUT_DIR}/9_Deployment_Architecture', cleanup=True)
print("✅ Saved: 9_Deployment_Architecture.png")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 50)
print("✅ All diagrams generated successfully!")
print(f"📁 Location: {OUTPUT_DIR}/")
print("\n📊 Generated Diagrams:")
print("  1. 1_System_Architecture.png - Overall system structure")
print("  2. 2_Container_Creation_Flow.png - Step-by-step container creation")
print("  3. 3_Technology_Stack.png - Technology layers")
print("  4. 4_Network_Topology.png - Docker network layout")
print("  5. 5_Request_Routing.png - How requests are routed")
print("  6. 6_GraphQL_Data_Flow.png - GraphQL query flow")
print("  7. 7_Traefik_Labels.png - Label generation process")
print("  8. 8_Security_Architecture.png - Security layers")
print("  9. 9_Deployment_Architecture.png - Production deployment")
print("\n💡 Usage:")
print("  - Insert these PNG images directly into PowerPoint")
print("  - High quality, ready for presentation")
print("  - Clear, professional diagrams")
print("\n🎨 All diagrams use consistent color scheme:")
print(f"  - Docker Blue: {COLORS['docker_blue']}")
print(f"  - Traefik Orange: {COLORS['traefik_orange']}")
print(f"  - GraphQL Pink: {COLORS['graphql_pink']}")
print(f"  - Success Green: {COLORS['success_green']}")
print("\n🚀 Ready for your presentation!")
