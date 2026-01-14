# ASU1-Loom - Project Overview 🧵

## Slide 1: Title Slide

### Content:
```
ASU1-Loom
Hybrid Container Orchestration Platform

Erik Kjær Klint
Aarhus Universitet
EH5ASU1 - Avanceret Softwareudvikling 1
```

**Speaker Notes:**
- Velkommen til min præsentation af ASU1-Loom
- Et container orchestration platform jeg har udviklet
- Kombinerer moderne web-teknologier med Docker

---

## Slide 2: Problem Statement & Solution

### Problem:
**"Hvordan kan vi gøre container deployment nemmere og mere tilgængeligt?"**

**Udfordringer:**
- Docker CLI er kompleks for begyndere
- Manuel konfiguration af reverse proxy
- Ingen visuel interface for container management
- Subdomain routing kræver manuel DNS/proxy setup

### Solution:
**ASU1-Loom - En-klik container deployment med automatisk subdomain routing**

**Nøgle Features:**
✅ Web-baseret dashboard (ingen CLI nødvendig)
✅ Automatisk subdomain routing via Traefik
✅ GraphQL API for fleksibel data-hentning
✅ 13+ pre-konfigurerede container templates
✅ Real-time container management

**Speaker Notes:**
- Problemet: Docker er kraftfuldt men komplekst
- Min løsning: Gør det simpelt gennem et web interface
- Automatiserer den kedelige del (DNS, proxy config)
- Fokus på brugeroplevelse uden at miste funktionalitet

---

## Slide 3: Real-World Use Cases

### Hvem kan bruge ASU1-Loom?

#### 1. **Udviklere**
- Hurtig deployment af test-miljøer
- Isolerede development containers
- Nem adgang via subdomains

#### 2. **Game Server Hosting**
- Minecraft servers med modpack support
- Valheim, Terraria servers
- Automatisk subdomain per server

#### 3. **Små Teams**
- Intern værktøjer (Grafana, Portainer)
- Web applications
- Monitoring services

#### 4. **Uddannelse**
- Lær Docker uden CLI
- Praktisk container management
- Visuel forståelse af containerization

**Speaker Notes:**
- Projektet er ikke bare et akademisk eksempel
- Har reelle anvendelsesmuligheder
- Jeg bruger det selv til at hoste min demo

---

## Project Statistics

### Technical Metrics:
- **Lines of Code:** ~2,500+
- **Technologies:** 8+ (Python, FastAPI, GraphQL, Docker, Traefik, PostgreSQL, WebAssembly, Nginx)
- **Container Templates:** 13+ pre-configured
- **API Operations:** 15+ GraphQL mutations/queries
- **Development Time:** 4+ weeks

### Performance:
- **Container Creation:** <30 seconds
- **API Response Time:** <100ms average
- **Memory Footprint:** <200MB base system
- **Concurrent Containers:** Tested with 5+ simultaneous

**Speaker Notes:**
- Projektet repræsenterer betydelig udviklingsindsats
- Fokus på performance og skalerbarhed
- Real-world testing på production server

---

## Architecture Overview (High-Level)

```
┌─────────────────────────────────────────────────────────┐
│                    User's Browser                        │
│              (WebAssembly Frontend)                      │
└────────────────────┬────────────────────────────────────┘
                     │ GraphQL API
┌────────────────────┴────────────────────────────────────┐
│                  Backend Server                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   FastAPI    │  │    Docker    │  │  PostgreSQL  │  │
│  │   GraphQL    │  │   Manager    │  │   Database   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│              Traefik Reverse Proxy                       │
│         (Automatic Subdomain Routing)                    │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────┴────────┐    ┌──────────┴─────────┐
│  User Container│    │  User Container    │
│  game.domain   │    │  grafana.domain    │
└────────────────┘    └────────────────────┘
```

**Key Components:**
1. **Frontend:** WebAssembly-based dashboard
2. **Backend:** FastAPI + GraphQL API
3. **Docker Manager:** Container lifecycle management
4. **Traefik:** Automatic reverse proxy routing
5. **PostgreSQL:** Container metadata storage

**Speaker Notes:**
- Simpel men kraftfuld arkitektur
- Hver komponent har et specifikt ansvar
- Traefik håndterer al routing automatisk
- Nu skal vi se det i aktion!

---

## Transition to Demo

**"Lad os se hvordan det fungerer i praksis..."**

**Speaker Notes:**
- Nu har I set problemet og løsningen
- Tid til at demonstrere systemet live
- Jeg vil vise hvor nemt det er at deploye en container
- Bemærk den automatiske subdomain routing

---

## PowerPoint Tips for This Section

### Slide Design:
- **Slide 1:** Clean title slide with project logo
- **Slide 2:** Split screen - Problem (left) vs Solution (right)
- **Slide 3:** Icons for each use case
- **Architecture:** Animated diagram showing data flow

### Animations:
- Fade in bullet points one at a time
- Architecture diagram: Components appear sequentially
- Use case icons: Zoom in effect

### Colors:
- Problem statements: Red/Orange tones
- Solutions: Green/Blue tones
- Architecture: Docker blue (#2496ED)

### Speaker Notes Timing:
- Slide 1: 15 seconds
- Slide 2: 30 seconds
- Slide 3: 15 seconds
- Total: ~1 minute

---

## Key Messages to Emphasize

1. **Simplicity:** "Gør Docker tilgængeligt for alle"
2. **Automation:** "Automatisk subdomain routing - ingen manuel konfiguration"
3. **Real-World:** "Ikke bare et skole-projekt - faktisk deployeret i production"
4. **Modern Tech:** "Bruger cutting-edge teknologier (WebAssembly, GraphQL)"

---

## Potential Questions & Answers

**Q: "Hvorfor WebAssembly til frontend?"**
A: Portabilitet og performance. Kan køre Python-kode direkte i browseren uden server-side rendering.

**Q: "Hvorfor GraphQL i stedet for REST?"**
A: Fleksibilitet - frontend kan hente præcis den data den har brug for. Bedre for real-time updates.

**Q: "Kan det skalere til mange brugere?"**
A: Ja, bygget på Docker og Traefik som begge er production-grade. PostgreSQL håndterer metadata effektivt.

**Q: "Hvad med sikkerhed?"**
A: Traefik håndterer SSL/TLS, containers er isolerede, Docker socket access er kontrolleret.
