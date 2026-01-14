# Quick Start Guide - Diagram Generation 🚀

## Super Simpel Løsning (ANBEFALET) ✅

### Kun 2 kommandoer:

```bash
# 1. Installer Pillow (tager 10 sekunder)
pip install pillow

# 2. Generer diagrammer (tager 30 sekunder)
python generate_diagrams_simple.py
```

**Det er det! Ingen Graphviz, ingen ekstra værktøjer!**

### Hvad får du?

6 professionelle PNG diagrammer i `Diagrams/` mappen:
- ✅ System Architecture
- ✅ Container Creation Flow (9 steps)
- ✅ Technology Stack
- ✅ Request Routing
- ✅ GraphQL Data Flow
- ✅ Security Architecture

### Indsæt i PowerPoint:

1. Åbn PowerPoint
2. Insert → Pictures → From File
3. Vælg fra `Diagrams/` mappen
4. Resize og placer på slides

**Færdig!** 🎉

---

## Avanceret Løsning (Valgfri)

Hvis du vil have mere komplekse diagrammer med Graphviz:

```bash
# 1. Download og installer Graphviz
# Windows: https://graphviz.org/download/
# Mac: brew install graphviz
# Linux: sudo apt-get install graphviz

# 2. Installer Python pakke
pip install graphviz

# 3. Generer diagrammer
python generate_diagrams.py
```

Giver 9 diagrammer i stedet for 6.

---

## Hvilken Skal Du Vælge?

### Brug Simple Version Hvis:
- ✅ Du vil have det nemt og hurtigt
- ✅ Du ikke vil installere ekstra software
- ✅ 6 diagrammer er nok til din præsentation
- ✅ Du vil undgå problemer

### Brug Advanced Version Hvis:
- ⚠️ Du vil have alle 9 diagrammer
- ⚠️ Du er okay med at installere Graphviz
- ⚠️ Du vil have mere komplekse layouts

**Anbefaling: Start med simple version!** 

Du kan altid køre advanced version senere hvis du vil have flere diagrammer.

---

## Troubleshooting

### Problem: "No module named 'PIL'"
**Løsning:**
```bash
pip install pillow
```

### Problem: Diagrammer ser mærkelige ud
**Løsning:** 
- Prøv at køre scriptet igen
- Check at `Diagrams/` mappen blev oprettet
- Åbn PNG filerne for at verificere

### Problem: Vil have andre farver
**Løsning:**
- Åbn `generate_diagrams_simple.py`
- Rediger `COLORS` dictionary i toppen
- Kør scriptet igen

---

## 🎊 Du er Klar!

**Simple version = 2 kommandoer = 6 diagrammer = Ingen problemer!**

Held og lykke! 🍀
