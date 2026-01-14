# Diagram Generation Guide 📊

## Quick Start

### 1. Install Requirements
```bash
cd Presentation
pip install graphviz pillow
```

**Note:** Du skal også have Graphviz installeret på dit system:
- **Windows:** Download fra https://graphviz.org/download/
- **Mac:** `brew install graphviz`
- **Linux:** `sudo apt-get install graphviz`

### 2. Generate All Diagrams
```bash
python generate_diagrams.py
```

### 3. Find Your Diagrams
Alle diagrammer gemmes i `Diagrams/` mappen som PNG filer.

---

## Generated Diagrams

### 1. System Architecture (`1_System_Architecture.png`)
**Viser:** Overall system struktur med alle lag
**Brug til:** Slide 7 - Architecture Overview
**Indhold:**
- Client Layer (Browser + WebAssembly)
- Reverse Proxy Layer (Traefik)
- Backend Layer (FastAPI, Docker Manager, PostgreSQL)
- Container Runtime Layer (Docker Engine)

---

### 2. Container Creation Flow (`2_Container_Creation_Flow.png`)
**Viser:** Step-by-step proces for at oprette en container
**Brug til:** Slide 12 - Backend Implementation eller Demo explanation
**Indhold:**
- 9 steps fra user input til deployed container
- Viser data flow gennem hele systemet
- Perfekt til at forklare hvordan det hele hænger sammen

---

### 3. Technology Stack (`3_Technology_Stack.png`)
**Viser:** Teknologi lag fra presentation til runtime
**Brug til:** Slide 8 - Tech Stack Overview
**Indhold:**
- Presentation Layer (HTML, CSS, JS, WASM)
- API Layer (GraphQL, FastAPI)
- Business Logic Layer (Services)
- Data Layer (PostgreSQL)
- Runtime Layer (Docker)

---

### 4. Network Topology (`4_Network_Topology.png`)
**Viser:** Docker network layout og IP addressing
**Brug til:** Technical deep-dive eller Q&A
**Indhold:**
- Host network (pandaserver.ddns.net)
- Docker bridge network (loom_network)
- Container IP addresses
- Port mappings

---

### 5. Request Routing (`5_Request_Routing.png`)
**Viser:** Hvordan forskellige URLs routes til forskellige containers
**Brug til:** Demo explanation eller Traefik functionality
**Indhold:**
- DNS resolution
- Traefik routing decisions
- Different paths for different subdomains
- Perfect for explaining automatic routing

---

### 6. GraphQL Data Flow (`6_GraphQL_Data_Flow.png`)
**Viser:** GraphQL query/mutation flow gennem systemet
**Brug til:** Slide 12 - GraphQL explanation
**Indhold:**
- Browser → GraphQL endpoint
- Resolver execution
- Service layer calls
- Database/Docker queries
- Response formatting

---

### 7. Traefik Labels (`7_Traefik_Labels.png`)
**Viser:** Hvordan Traefik labels genereres og bruges
**Brug til:** Slide 13 - Docker Manager explanation
**Indhold:**
- Input parameters
- Environment variable reading
- Label generation
- Container attachment
- Traefik auto-discovery

---

### 8. Security Architecture (`8_Security_Architecture.png`)
**Viser:** Security layers fra external threats til data
**Brug til:** Q&A om security eller technical discussion
**Indhold:**
- External threats
- Firewall (UFW)
- Traefik security
- Application security
- Container isolation
- Data protection

---

### 9. Deployment Architecture (`9_Deployment_Architecture.png`)
**Viser:** Production deployment setup
**Brug til:** Slide 16 - Challenges/Production deployment
**Indhold:**
- Production server
- Docker Compose services
- External services (No-IP, Router)
- Port forwarding
- DNS configuration

---

## Color Scheme

Alle diagrammer bruger konsistent farve-skema:

- **Docker Blue** (`#2496ED`) - Backend, Docker-relateret
- **Traefik Orange** (`#FF6600`) - Traefik, routing
- **GraphQL Pink** (`#E10098`) - Frontend, GraphQL, API
- **Success Green** (`#28A745`) - Containers, runtime, success states
- **Warning Yellow** (`#FFC107`) - Warnings, environment
- **Error Red** (`#DC3545`) - Errors, threats
- **Light Gray** (`#F5F5F5`) - Neutral, user input
- **Dark Gray** (`#6C757D`) - Secondary elements

---

## Customization

### Ændre Farver
Rediger `COLORS` dictionary i `generate_diagrams.py`:
```python
COLORS = {
    'docker_blue': '#2496ED',  # Change this
    'traefik_orange': '#FF6600',  # Or this
    # etc.
}
```

### Tilføj Nyt Diagram
1. Åbn `generate_diagrams.py`
2. Kopier en eksisterende diagram sektion
3. Modificer nodes og edges
4. Gem med nyt nummer

Eksempel:
```python
# DIAGRAM 10: Your New Diagram
print("\n📊 Generating: 10_Your_Diagram.png")

new_diagram = Digraph('YourDiagram', format='png')
new_diagram.attr(rankdir='TB', bgcolor='white', fontname='Arial')
new_diagram.attr('node', shape='box', style='rounded,filled', fontname='Arial')

# Add nodes
new_diagram.node('node1', 'Label 1', fillcolor=COLORS['docker_blue'], fontcolor='white')
new_diagram.node('node2', 'Label 2', fillcolor=COLORS['success_green'], fontcolor='white')

# Add edges
new_diagram.edge('node1', 'node2', label='Connection')

# Render
new_diagram.render(f'{OUTPUT_DIR}/10_Your_Diagram', cleanup=True)
print("✅ Saved: 10_Your_Diagram.png")
```

---

## Troubleshooting

### Problem: "graphviz not found"
**Solution:** Install Graphviz system package:
```bash
# Windows (download installer)
https://graphviz.org/download/

# Mac
brew install graphviz

# Linux
sudo apt-get install graphviz
```

### Problem: "Module not found: graphviz"
**Solution:** Install Python package:
```bash
pip install graphviz pillow
```

### Problem: Diagrams look blurry
**Solution:** Graphviz generates vector graphics, så de skulle være skarpe. Hvis de ser blurry ud i PowerPoint:
1. Højreklik på billedet
2. Format Picture
3. Size → Uncheck "Lock aspect ratio"
4. Adjust size manually

### Problem: Want higher resolution
**Solution:** Graphviz PNG output er allerede høj kvalitet. Hvis du vil have endnu højere:
1. Ændr `format='png'` til `format='svg'` i scriptet
2. Import SVG i PowerPoint (supports vector graphics)

---

## Tips for PowerPoint

### Inserting Diagrams:
1. Insert → Pictures → From File
2. Navigate to `Diagrams/` folder
3. Select diagram
4. Resize as needed

### Best Practices:
- **Full-slide diagrams:** Use for architecture overviews
- **Half-slide diagrams:** Combine with bullet points
- **Animations:** Fade in for impact
- **Annotations:** Add text boxes to highlight specific parts

### Recommended Sizes:
- **Full slide:** Width 10" (25cm)
- **Half slide:** Width 5" (12.5cm)
- **Quarter slide:** Width 3" (7.5cm)

---

## Advanced: Batch Generation

### Generate Only Specific Diagrams:
Kommenter ud de diagrammer du ikke vil have:
```python
# Comment out unwanted diagrams
# arch.render(f'{OUTPUT_DIR}/1_System_Architecture', cleanup=True)
flow.render(f'{OUTPUT_DIR}/2_Container_Creation_Flow', cleanup=True)
# etc.
```

### Generate Different Formats:
Ændr `format='png'` til:
- `format='svg'` - Vector graphics (scalable)
- `format='pdf'` - PDF format
- `format='jpg'` - JPEG format

---

## File Structure After Generation

```
Presentation/
├── generate_diagrams.py          # Generator script
├── DIAGRAM_GENERATION.md         # This file
├── Diagrams/                     # Generated diagrams
│   ├── 1_System_Architecture.png
│   ├── 2_Container_Creation_Flow.png
│   ├── 3_Technology_Stack.png
│   ├── 4_Network_Topology.png
│   ├── 5_Request_Routing.png
│   ├── 6_GraphQL_Data_Flow.png
│   ├── 7_Traefik_Labels.png
│   ├── 8_Security_Architecture.png
│   └── 9_Deployment_Architecture.png
└── ... (other presentation files)
```

---

## Quick Reference

| Diagram | Best For | Slide |
|---------|----------|-------|
| 1_System_Architecture | Overall structure | 7 |
| 2_Container_Creation_Flow | Process explanation | 12 |
| 3_Technology_Stack | Tech choices | 8 |
| 4_Network_Topology | Technical deep-dive | Q&A |
| 5_Request_Routing | Routing explanation | Demo |
| 6_GraphQL_Data_Flow | API explanation | 12 |
| 7_Traefik_Labels | Docker Manager | 13 |
| 8_Security_Architecture | Security discussion | Q&A |
| 9_Deployment_Architecture | Production setup | 16 |

---

## 🎨 You're All Set!

**One command generates all diagrams:**
```bash
python generate_diagrams.py
```

**Professional, consistent, ready-to-use diagrams for your presentation!** 🚀
