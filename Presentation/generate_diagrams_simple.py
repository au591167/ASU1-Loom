"""
ASU1-Loom Simple Diagram Generator
Generates diagrams using only PIL/Pillow (no Graphviz needed!)

Usage:
    python generate_diagrams_simple.py

Requirements:
    pip install pillow
"""

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

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def draw_box(draw, x, y, width, height, fill_color, text, text_color='#FFFFFF', border=True):
    """Draw a rounded rectangle box with text"""
    # Draw rectangle
    fill_rgb = hex_to_rgb(fill_color)
    draw.rectangle([x, y, x + width, y + height], fill=fill_rgb, outline=(0, 0, 0) if border else None, width=2)
    
    # Draw text
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    text_color_rgb = hex_to_rgb(text_color)
    
    # Multi-line text support
    lines = text.split('\n')
    line_height = 25
    total_height = len(lines) * line_height
    start_y = y + (height - total_height) // 2
    
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = x + (width - text_width) // 2
        text_y = start_y + i * line_height
        draw.text((text_x, text_y), line, fill=text_color_rgb, font=font)

def draw_arrow(draw, x1, y1, x2, y2, label=''):
    """Draw an arrow from (x1,y1) to (x2,y2)"""
    # Draw line
    draw.line([x1, y1, x2, y2], fill=(0, 0, 0), width=2)
    
    # Draw arrowhead
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    arrow_length = 15
    arrow_angle = math.pi / 6
    
    x_left = x2 - arrow_length * math.cos(angle - arrow_angle)
    y_left = y2 - arrow_length * math.sin(angle - arrow_angle)
    x_right = x2 - arrow_length * math.cos(angle + arrow_angle)
    y_right = y2 - arrow_length * math.sin(angle + arrow_angle)
    
    draw.polygon([(x2, y2), (x_left, y_left), (x_right, y_right)], fill=(0, 0, 0))
    
    # Draw label
    if label:
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
        
        mid_x = (x1 + x2) // 2
        mid_y = (y1 + y2) // 2
        draw.text((mid_x + 5, mid_y - 15), label, fill=(0, 0, 0), font=font)

print("🎨 ASU1-Loom Simple Diagram Generator")
print("=" * 50)
print("Using PIL/Pillow only - no Graphviz needed!")
print()

# ============================================================================
# DIAGRAM 1: System Architecture
# ============================================================================
print("📊 Generating: 1_System_Architecture.png")

img = Image.new('RGB', (1200, 900), color=hex_to_rgb(COLORS['white']))
draw = ImageDraw.Draw(img)

# Title
try:
    title_font = ImageFont.truetype("arial.ttf", 24)
except:
    title_font = ImageFont.load_default()
draw.text((400, 20), "System Architecture", fill=(0, 0, 0), font=title_font)

# Client Layer
draw_box(draw, 100, 80, 1000, 100, COLORS['light_gray'], 
         "Client Layer\nWeb Browser + WebAssembly Frontend", COLORS['black'])

# Proxy Layer
draw_box(draw, 100, 220, 1000, 100, COLORS['traefik_orange'], 
         "Reverse Proxy Layer\nTraefik v2.11 - Automatic Routing")

# Backend Layer
draw_box(draw, 100, 360, 300, 100, COLORS['docker_blue'], "FastAPI\nGraphQL API")
draw_box(draw, 450, 360, 300, 100, COLORS['docker_blue'], "Docker Manager\nContainer Lifecycle")
draw_box(draw, 800, 360, 300, 100, COLORS['docker_blue'], "PostgreSQL\nMetadata Storage")

# Container Layer
draw_box(draw, 100, 500, 1000, 100, COLORS['success_green'], 
         "Container Runtime Layer\nDocker Engine + User Containers")

# Arrows
draw_arrow(draw, 600, 180, 600, 220, "HTTP/GraphQL")
draw_arrow(draw, 250, 320, 250, 360, "API")
draw_arrow(draw, 600, 320, 600, 360, "Manages")
draw_arrow(draw, 950, 320, 950, 360, "Queries")
draw_arrow(draw, 600, 460, 600, 500, "Docker Socket")

img.save(f'{OUTPUT_DIR}/1_System_Architecture.png')
print("✅ Saved: 1_System_Architecture.png")

# ============================================================================
# DIAGRAM 2: Container Creation Flow
# ============================================================================
print("\n📊 Generating: 2_Container_Creation_Flow.png")

img = Image.new('RGB', (800, 1000), color=hex_to_rgb(COLORS['white']))
draw = ImageDraw.Draw(img)

# Title
draw.text((250, 20), "Container Creation Flow", fill=(0, 0, 0), font=title_font)

# Steps
steps = [
    ("1. User\nFills Form", COLORS['light_gray'], COLORS['black']),
    ("2. Frontend\nGraphQL Mutation", COLORS['graphql_pink'], COLORS['white']),
    ("3. Nginx\nProxy Request", COLORS['success_green'], COLORS['white']),
    ("4. Backend\nGraphQL Resolver", COLORS['docker_blue'], COLORS['white']),
    ("5. Docker Manager\nGenerate Labels", COLORS['docker_blue'], COLORS['white']),
    ("6. Docker Engine\nCreate Container", COLORS['success_green'], COLORS['white']),
    ("7. Database\nSave Metadata", COLORS['docker_blue'], COLORS['white']),
    ("8. Traefik\nAuto-Discovery", COLORS['traefik_orange'], COLORS['white']),
    ("9. Response\nUI Update", COLORS['graphql_pink'], COLORS['white']),
]

y_pos = 80
for i, (text, color, text_color) in enumerate(steps):
    draw_box(draw, 200, y_pos, 400, 80, color, text, text_color)
    if i < len(steps) - 1:
        draw_arrow(draw, 400, y_pos + 80, 400, y_pos + 100, "")
    y_pos += 100

img.save(f'{OUTPUT_DIR}/2_Container_Creation_Flow.png')
print("✅ Saved: 2_Container_Creation_Flow.png")

# ============================================================================
# DIAGRAM 3: Technology Stack
# ============================================================================
print("\n📊 Generating: 3_Technology_Stack.png")

img = Image.new('RGB', (1000, 700), color=hex_to_rgb(COLORS['white']))
draw = ImageDraw.Draw(img)

# Title
draw.text((350, 20), "Technology Stack Layers", fill=(0, 0, 0), font=title_font)

# Layers
layers = [
    ("Presentation Layer\nHTML5 • CSS3 • JavaScript • WebAssembly", COLORS['graphql_pink']),
    ("API Layer\nGraphQL (Strawberry) • FastAPI • Uvicorn", COLORS['docker_blue']),
    ("Business Logic Layer\ndocker_manager.py • modpack_service.py", COLORS['docker_blue']),
    ("Data Layer\nPostgreSQL • SQLAlchemy", COLORS['success_green']),
    ("Runtime Layer\nDocker Engine • Containers • Networks", COLORS['success_green']),
]

y_pos = 80
for i, (text, color) in enumerate(layers):
    draw_box(draw, 100, y_pos, 800, 100, color, text)
    if i < len(layers) - 1:
        draw_arrow(draw, 500, y_pos + 100, 500, y_pos + 120, "")
    y_pos += 120

img.save(f'{OUTPUT_DIR}/3_Technology_Stack.png')
print("✅ Saved: 3_Technology_Stack.png")

# ============================================================================
# DIAGRAM 4: Request Routing
# ============================================================================
print("\n📊 Generating: 4_Request_Routing.png")

img = Image.new('RGB', (1000, 800), color=hex_to_rgb(COLORS['white']))
draw = ImageDraw.Draw(img)

# Title
draw.text((350, 20), "Request Routing Flow", fill=(0, 0, 0), font=title_font)

# User Request
draw_box(draw, 400, 80, 200, 60, COLORS['light_gray'], "User Request", COLORS['black'])

# DNS
draw_box(draw, 350, 180, 300, 60, COLORS['warning_yellow'], 
         "DNS Resolution\n*.pandaserver.ddns.net", COLORS['black'])

# Traefik
draw_box(draw, 400, 280, 200, 60, COLORS['traefik_orange'], "Traefik\nPort 80")

# Routes
routes = [
    ("pandaserver.ddns.net\n→ Frontend", COLORS['graphql_pink'], 150),
    ("/graphql\n→ Backend API", COLORS['docker_blue'], 350),
    ("game.domain\n→ Container", COLORS['success_green'], 550),
    ("grafana.domain\n→ Container", COLORS['success_green'], 750),
]

for text, color, x_pos in routes:
    draw_box(draw, x_pos, 400, 180, 80, color, text)
    draw_arrow(draw, 500, 340, x_pos + 90, 400, "")

# Arrows
draw_arrow(draw, 500, 140, 500, 180, "")
draw_arrow(draw, 500, 240, 500, 280, "")

img.save(f'{OUTPUT_DIR}/4_Request_Routing.png')
print("✅ Saved: 4_Request_Routing.png")

# ============================================================================
# DIAGRAM 5: GraphQL Data Flow (Enhanced with Request/Response)
# ============================================================================
print("\n📊 Generating: 5_GraphQL_Data_Flow.png")

img = Image.new('RGB', (1200, 700), color=hex_to_rgb(COLORS['white']))
draw = ImageDraw.Draw(img)

# Title
draw.text((400, 20), "GraphQL Data Flow (Request/Response)", fill=(0, 0, 0), font=title_font)

# Request Flow (Top row)
request_components = [
    ("Browser\nGraphQL Query", COLORS['light_gray'], COLORS['black'], 100, 80),
    ("Nginx\nProxy", COLORS['success_green'], COLORS['white'], 300, 80),
    ("FastAPI\n/graphql", COLORS['graphql_pink'], COLORS['white'], 500, 80),
    ("Resolver\n@strawberry", COLORS['docker_blue'], COLORS['white'], 700, 80),
    ("Service Layer\nDocker Manager", COLORS['docker_blue'], COLORS['white'], 900, 80),
]

for text, color, text_color, x_pos, y_pos in request_components:
    draw_box(draw, x_pos, y_pos, 180, 80, color, text, text_color)

# Request arrows (going right) - ABOVE boxes
for i in range(len(request_components) - 1):
    x1 = request_components[i][3] + 180
    x2 = request_components[i + 1][3]
    y = 60  # Above boxes
    draw_arrow(draw, x1, y, x2, y, "")

# Data Sources (Bottom)
data_sources = [
    ("Docker API\nContainer Info", COLORS['success_green'], COLORS['white'], 850, 400),
    ("PostgreSQL\nMetadata", COLORS['success_green'], COLORS['white'], 1000, 400),
]

for text, color, text_color, x_pos, y_pos in data_sources:
    draw_box(draw, x_pos, y_pos, 150, 80, color, text, text_color)

# Arrows from Service Layer to Data Sources (vertical down)
draw_arrow(draw, 950, 160, 925, 400, "")
draw_arrow(draw, 1030, 160, 1075, 400, "")

# Response arrows (going back up from data sources)
draw_arrow(draw, 925, 480, 950, 240, "")
draw_arrow(draw, 1075, 480, 1030, 240, "")

# Response Flow (going left) - BELOW boxes
response_y = 200
draw_arrow(draw, 900, response_y, 880, response_y, "")
draw_arrow(draw, 880, response_y, 700, response_y, "")
draw_arrow(draw, 680, response_y, 500, response_y, "")
draw_arrow(draw, 480, response_y, 300, response_y, "")
draw_arrow(draw, 280, response_y, 100, response_y, "")

# Labels
try:
    label_font = ImageFont.truetype("arial.ttf", 14)
    bold_font = ImageFont.truetype("arialbd.ttf", 16)
except:
    label_font = ImageFont.load_default()
    bold_font = ImageFont.load_default()

# Flow labels
draw.text((20, 50), "1. Request →", fill=hex_to_rgb(COLORS['docker_blue']), font=bold_font)
draw.text((20, 190), "3. Response ←", fill=hex_to_rgb(COLORS['success_green']), font=bold_font)
draw.text((1050, 280), "2. Fetch", fill=hex_to_rgb(COLORS['traefik_orange']), font=label_font)
draw.text((1050, 300), "   Data ↓↑", fill=hex_to_rgb(COLORS['traefik_orange']), font=label_font)

# Legend at bottom
draw.text((100, 600), "Complete Flow: Browser → Nginx → FastAPI → Resolver → Service → Docker/DB → Response back through all layers", 
          fill=(0, 0, 0), font=label_font)

img.save(f'{OUTPUT_DIR}/5_GraphQL_Data_Flow.png')
print("✅ Saved: 5_GraphQL_Data_Flow.png")

# ============================================================================
# DIAGRAM 6: Security Architecture
# ============================================================================
print("\n📊 Generating: 6_Security_Architecture.png")

img = Image.new('RGB', (800, 900), color=hex_to_rgb(COLORS['white']))
draw = ImageDraw.Draw(img)

# Title
draw.text((250, 20), "Security Architecture", fill=(0, 0, 0), font=title_font)

# Security layers
security_layers = [
    ("External Threats\nDDoS • SQL Injection • XSS", COLORS['error_red']),
    ("Firewall (UFW)\nAllow: 80, 443, 8000", COLORS['warning_yellow']),
    ("Traefik\nSSL/TLS • Rate Limiting", COLORS['traefik_orange']),
    ("Application Layer\nCORS • Input Validation", COLORS['docker_blue']),
    ("Container Isolation\nDocker Networks • Limits", COLORS['success_green']),
    ("Data Layer\nEncrypted • Access Control", COLORS['success_green']),
]

y_pos = 80
for i, (text, color) in enumerate(security_layers):
    text_color = COLORS['white'] if i > 1 else COLORS['black']
    draw_box(draw, 150, y_pos, 500, 100, color, text, text_color)
    if i < len(security_layers) - 1:
        # Draw arrow without label to avoid overlap
        draw_arrow(draw, 400, y_pos + 100, 400, y_pos + 120, "")
    y_pos += 120

# Add legend at bottom to explain flow
try:
    legend_font = ImageFont.truetype("arial.ttf", 14)
except:
    legend_font = ImageFont.load_default()

draw.text((150, y_pos + 20), "⬇ Flow: Threats are blocked/filtered at each layer", 
          fill=(0, 0, 0), font=legend_font)

img.save(f'{OUTPUT_DIR}/6_Security_Architecture.png')
print("✅ Saved: 6_Security_Architecture.png")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 50)
print("✅ All diagrams generated successfully!")
print(f"📁 Location: {OUTPUT_DIR}/")
print("\n📊 Generated Diagrams:")
print("  1. 1_System_Architecture.png - Overall system structure")
print("  2. 2_Container_Creation_Flow.png - Step-by-step process")
print("  3. 3_Technology_Stack.png - Technology layers")
print("  4. 4_Request_Routing.png - How requests are routed")
print("  5. 5_GraphQL_Data_Flow.png - GraphQL query flow")
print("  6. 6_Security_Architecture.png - Security layers")
print("\n💡 Usage:")
print("  - Insert these PNG images directly into PowerPoint")
print("  - High quality, ready for presentation")
print("  - No Graphviz needed - only Pillow!")
print("\n🎨 All diagrams use consistent color scheme")
print("\n🚀 Ready for your presentation!")
print("\n📝 Note: This is a simplified version.")
print("   For more complex diagrams, use generate_diagrams.py with Graphviz")
