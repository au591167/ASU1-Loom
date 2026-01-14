# Live Demo Scenarios - ASU1-Loom 🎬

## Demo Overview

**Timing:** 3-4 minutter
**Goal:** Vise systemets funktionalitet og automatiske subdomain routing
**Impact:** Hook audience med working system

---

## Pre-Demo Checklist ✅

### Before Presentation:
- [ ] Server kører: `http://pandaserver.ddns.net`
- [ ] Backend er healthy: Check `/health` endpoint
- [ ] Traefik dashboard tilgængelig: Port 8080
- [ ] DNS wildcard virker: Test `test.pandaserver.ddns.net`
- [ ] Browser cache cleared
- [ ] Backup container klar (nginx-test)

### Browser Setup:
- [ ] Tab 1: Dashboard (`http://pandaserver.ddns.net`)
- [ ] Tab 2: Tom (klar til demo container)
- [ ] Tab 3: Traefik dashboard (optional, til debugging)

### Network Check:
```bash
# Fra server
curl http://pandaserver.ddns.net/health
# Should return: {"status":"healthy","service":"loom-backend"}

# DNS check
nslookup game.pandaserver.ddns.net
# Should resolve to: 85.24.3.105
```

---

## Demo Scenario 1: 2048 Game Deployment (PRIMARY)

### Why This Demo?
✅ Visuelt imponerende (farverig, interaktiv)
✅ Hurtig deployment (<30 sekunder)
✅ Demonstrerer web hosting capability
✅ Audience kan relatere til det (kendt spil)

### Step-by-Step Script:

#### **Step 1: Show Dashboard (15 sec)**
**Action:** Åbn `http://pandaserver.ddns.net`

**Say:**
> "Her er ASU1-Loom dashboardet. Som I kan se, har vi en simpel, ren interface til at administrere containers."

**Point Out:**
- Container list (hvis nogen kører)
- "Create Container" knap
- Clean, moderne design

---

#### **Step 2: Start Container Creation (10 sec)**
**Action:** Klik "Create Container" knap

**Say:**
> "Lad os deploye en web application. Jeg klikker bare på 'Create Container'..."

**Show:**
- Modal åbner med form fields
- Forskellige input felter vises

---

#### **Step 3: Fill Container Details (30 sec)**
**Action:** Udfyld følgende:

```
Container Name: game-2048
Image: alexwhen/docker-2048
Tag: latest
Subdomain: game
Internal Port: 80
Environment Variables: (leave empty)
```

**Say:**
> "Jeg giver containeren et navn - 'game-2048'. 
> Docker image er 'alexwhen/docker-2048' - et simpelt HTML5 spil.
> Tag er 'latest' for nyeste version.
> Subdomain bliver 'game' - systemet vil automatisk lave 'game.pandaserver.ddns.net'.
> Internal port er 80, da det er en web server.
> Ingen environment variables nødvendige for dette image."

**Point Out:**
- Subdomain field - "Dette er magien - automatisk routing"
- Port mapping - "Traefik håndterer dette automatisk"

---

#### **Step 4: Create Container (5 sec)**
**Action:** Klik "Create" knap

**Say:**
> "Og nu klikker jeg bare 'Create'..."

**Watch:**
- Loading indicator
- Success message
- Container appears in list

---

#### **Step 5: Start Container (10 sec)**
**Action:** Find container i listen, klik "Start"

**Say:**
> "Containeren er nu oprettet. Lad os starte den..."

**Watch:**
- Status ændrer til "Running"
- Green indicator

---

#### **Step 6: Access via Subdomain (20 sec)**
**Action:** Åbn ny tab, gå til `http://game.pandaserver.ddns.net`

**Say:**
> "Og nu - det interessante. Jeg åbner bare 'game.pandaserver.ddns.net' i browseren..."

**Result:**
- 2048 game loads instantly
- Colorful, interactive interface
- **WOW MOMENT** 🎉

**Say:**
> "Og voilà! På under 30 sekunder har vi deployed en fuldt funktionel web application med automatisk subdomain routing. Ingen manuel DNS konfiguration, ingen proxy setup - alt er automatisk."

---

#### **Step 7: Demonstrate Functionality (15 sec)**
**Action:** Spil et par moves i 2048

**Say:**
> "Og som I kan se, er det fuldt funktionelt. Jeg kan spille spillet direkte."

**Point Out:**
- Responsive design
- Real-time updates
- Professional appearance

---

### Demo 1 Total Time: ~2 minutter

---

## Demo Scenario 2: Grafana (BACKUP/EXTENDED)

**Use If:** Du har ekstra tid eller vil vise environment variables

### Container Details:
```
Container Name: monitoring
Image: grafana/grafana
Tag: latest
Subdomain: grafana
Internal Port: 3000
Environment Variables:
  GF_SECURITY_ADMIN_PASSWORD=demo123
  GF_USERS_ALLOW_SIGN_UP=false
```

### Script:
**Say:**
> "Lad mig vise et mere enterprise-grade eksempel. Grafana er et monitoring tool brugt af virksomheder som Uber og Bloomberg."

**Demonstrate:**
1. Create container med environment variables
2. Start container
3. Access `http://grafana.pandaserver.ddns.net`
4. Login: admin / demo123
5. Show professional dashboard

**Point Out:**
- Environment variable support
- Enterprise-grade software
- Complex applications work seamlessly

### Time: +2 minutter (hvis tid tillader)

---

## Demo Scenario 3: Show Container Management (QUICK)

**Use If:** Du vil vise lifecycle management

### Actions:
1. **Stop Container:** Klik "Stop" på game-2048
2. **Show Status Change:** Status → "Stopped"
3. **Restart:** Klik "Start" igen
4. **Verify:** Refresh `game.pandaserver.ddns.net` - works again

**Say:**
> "Jeg kan også nemt stoppe og starte containers gennem interfacet. Alt håndteres gennem API'et."

### Time: +30 sekunder

---

## Troubleshooting During Demo

### Problem: Container won't start
**Solution:**
- Check backend logs (have terminal ready)
- Use backup container (nginx-test already running)
- Say: "Lad mig vise en container jeg forberedte tidligere..."

### Problem: Subdomain doesn't load
**Solution:**
- Check DNS: `nslookup game.pandaserver.ddns.net`
- Use direct port access: `http://pandaserver.ddns.net:3000`
- Say: "DNS propagation kan tage et øjeblik, men containeren kører..."

### Problem: Dashboard won't load
**Solution:**
- Have screenshots ready
- Use localhost version if available
- Say: "Lad mig vise arkitekturen i stedet..."

---

## Backup Demo Plan

### If Everything Fails:
1. **Show nginx-test:** `http://test.pandaserver.ddns.net`
2. **Explain:** "Jeg har en container kørende fra tidligere..."
3. **Show code:** Walk through docker_manager.py instead
4. **Use screenshots:** Have demo screenshots ready

---

## Demo Talking Points

### While Container Creates:
> "Bag kulisserne sker der flere ting:
> 1. Backend sender request til Docker API
> 2. Docker puller image hvis nødvendig
> 3. Container oprettes med Traefik labels
> 4. Traefik opdager automatisk den nye container
> 5. Subdomain routing konfigureres automatisk"

### While Showing Running Container:
> "Bemærk at jeg ikke har:
> - Redigeret DNS records manuelt
> - Konfigureret nginx eller Apache
> - Skrevet proxy regler
> - Alt dette håndteres automatisk af Traefik baseret på Docker labels"

### Technical Details (If Asked):
> "Traefik læser Docker labels på containeren:
> - `traefik.http.routers.game-2048.rule=Host('game.pandaserver.ddns.net')`
> - `traefik.http.services.game-2048.loadbalancer.server.port=80`
> Disse labels genereres automatisk af min docker_manager.py service"

---

## Post-Demo Transition

**Say:**
> "Som I lige har set, gør ASU1-Loom det utroligt nemt at deploye containers. Men hvordan virker det under motorhjelmen? Lad os kigge på tech stacken..."

**Transition to:** Slide 7 - Tech Stack Overview

---

## Demo Success Criteria

### Minimum Success:
✅ Dashboard loads
✅ Container creation form works
✅ Container appears in list
✅ Status shows "Running"

### Full Success:
✅ All of above +
✅ Subdomain loads in browser
✅ Application is functional
✅ Smooth, no errors

### Excellent:
✅ All of above +
✅ Show second container
✅ Demonstrate stop/start
✅ Answer technical questions confidently

---

## Timing Breakdown

| Action | Time | Cumulative |
|--------|------|------------|
| Show dashboard | 15s | 0:15 |
| Open create modal | 10s | 0:25 |
| Fill form | 30s | 0:55 |
| Create container | 5s | 1:00 |
| Start container | 10s | 1:10 |
| Open subdomain | 20s | 1:30 |
| Demonstrate app | 15s | 1:45 |
| Explain automation | 30s | 2:15 |
| **Buffer** | 45s | 3:00 |

**Target:** 2-3 minutter
**Maximum:** 4 minutter

---

## Visual Aids for PowerPoint

### Slide Content During Demo:

**Slide Title:** "Live Demo: Container Deployment"

**Bullet Points:**
- ✅ Web-based dashboard
- ✅ Simple form input
- ✅ Automatic subdomain routing
- ✅ <30 second deployment
- ✅ No manual configuration

**Screenshot:** Dashboard with create modal open

**Speaker Notes:**
- Switch to live demo
- Follow script above
- Return to slides after demo

---

## Practice Tips

### Before Presentation:
1. **Run through demo 3 times**
2. **Time yourself** - aim for 2-3 minutes
3. **Test backup scenarios**
4. **Prepare for questions**
5. **Have terminal ready** (just in case)

### During Practice:
- Speak clearly and not too fast
- Explain what you're doing
- Point out key features
- Maintain eye contact with audience
- Don't apologize for minor glitches

### Common Mistakes to Avoid:
❌ Typing too fast (makes mistakes)
❌ Not explaining what you're doing
❌ Assuming audience knows Docker
❌ Skipping the "wow moment"
❌ Not having backup plan

---

## Audience Engagement

### Questions to Anticipate:

**Q: "Hvad hvis to brugere vælger samme subdomain?"**
A: "God pointe! Systemet tjekker for duplikater og giver en fejl. I en multi-user version ville jeg implementere namespace per bruger."

**Q: "Kan det håndtere SSL/HTTPS?"**
A: "Ja! Traefik kan automatisk håndtere Let's Encrypt SSL certificates. Jeg har fokuseret på HTTP for demo, men HTTPS er en simpel konfiguration."

**Q: "Hvad med performance ved mange containers?"**
A: "Docker og Traefik er begge production-grade. Jeg har testet med 5+ samtidige containers uden problemer. Bottleneck ville være server resources, ikke softwaren."

**Q: "Hvordan håndterer du container crashes?"**
A: "Docker har built-in restart policies. Jeg kan konfigurere containers til at auto-restart ved crashes. Traefik opdager automatisk når containers er nede."

---

## Success Metrics

### Demo Went Well If:
- ✅ Audience looks engaged
- ✅ No major technical failures
- ✅ Questions show understanding
- ✅ Stayed within time limit
- ✅ Smooth transition to next section

### Red Flags:
- ❌ Confused faces
- ❌ No questions
- ❌ Technical difficulties >1 minute
- ❌ Went over time significantly

---

## Final Checklist

**5 Minutes Before Presentation:**
- [ ] Server is running
- [ ] Dashboard loads
- [ ] DNS resolves
- [ ] Browser tabs ready
- [ ] Backup plan ready
- [ ] Deep breath! 😊

**You've got this! The demo is your strongest asset - show them what you built!** 🚀
