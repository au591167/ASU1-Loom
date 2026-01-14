# ASU1-Loom - Frontend Fix Deployment Guide

## 🎯 Quick Fix Summary

**Problem:** Frontend downloads as file instead of displaying in browser
**Root Cause:** Nginx `default_type` was `application/octet-stream` instead of `text/html`
**Solution:** Updated nginx.conf and docker-compose.yml with proper MIME types and routing

---

## 📋 Step-by-Step Deployment

### Step 1: Pull Latest Changes
```bash
cd /path/to/ASU1-Loom
git pull origin main
```

### Step 2: Stop Containers
```bash
docker-compose down
```

### Step 3: Rebuild Frontend (Important!)
```bash
docker-compose build --no-cache frontend
```

### Step 4: Start All Services
```bash
docker-compose up -d
```

### Step 5: Wait for Startup
```bash
sleep 10
```

### Step 6: Verify Deployment
```bash
# Check all containers are running
docker-compose ps

# Test frontend (should return text/html)
curl -I http://localhost:3000 | grep "Content-Type"

# Test backend
curl http://localhost:8000/health
```

---

## ✅ Verification Tests

### Test 1: Frontend Content-Type
```bash
curl -I http://localhost:3000
```
**Expected:** `Content-Type: text/html; charset=utf-8`
**NOT:** `Content-Type: application/octet-stream`

### Test 2: Traefik Routing
```bash
curl -I http://localhost
```
**Expected:** `HTTP/1.1 200 OK` with `Content-Type: text/html`

### Test 3: Backend Health
```bash
curl http://localhost:8000/health
```
**Expected:** `{"status":"healthy","service":"loom-backend","version":"1.0.0"}`

### Test 4: Browser Test
1. Clear browser cache (Ctrl+Shift+Delete) or use incognito
2. Navigate to: `http://pandaserver.ddns.net` or `http://localhost`
3. **Should display dashboard** (not download file)
4. Open console (F12) - should be no errors

---

## 🔧 What Was Changed

### File 1: `frontend/nginx.conf`
- Changed `default_type application/octet-stream` → `default_type text/html`
- Added explicit Content-Type headers for HTML, JS, CSS
- Added specific location blocks for proper MIME types

### File 2: `docker-compose.yml`
- Added routing priorities (backend=10, frontend=1)
- Changed `Path()` to `PathPrefix()` for backend routes
- Ensures Traefik routes API calls to backend, everything else to frontend

---

## 🐛 Troubleshooting

### Issue: Still Downloads File
```bash
# 1. Clear browser cache completely or use incognito mode

# 2. Verify nginx config was updated
docker exec loom_frontend cat /etc/nginx/nginx.conf | grep "default_type"
# Should show: default_type text/html;

# 3. Check container was rebuilt (look at CREATED time)
docker images | grep loom_frontend

# 4. Restart frontend
docker-compose restart frontend
```

### Issue: 404 on JS/CSS Files
```bash
# Verify files exist in container
docker exec loom_frontend ls -la /usr/share/nginx/html/
# Should show: index.html, app.js, styles.css, templates.js
```

### Issue: CORS Errors
```bash
# Check backend CORS settings include your domain
docker exec loom_backend cat /app/config/settings.py | grep CORS_ORIGINS
```

### Issue: Traefik Not Routing
```bash
# Check Traefik dashboard
# Open: http://localhost:8080

# View Traefik logs
docker logs loom_traefik --tail 50
```

---

## 🚀 Quick Commands Reference

```bash
# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f frontend
docker-compose logs -f backend

# Restart everything
docker-compose restart

# Rebuild specific service
docker-compose up -d --build frontend

# Check container status
docker-compose ps

# Check resource usage
docker stats --no-stream
```

---

## 🆘 Emergency Backup Plan

If frontend still doesn't work through Traefik:

```bash
# Stop Traefik
docker-compose stop traefik

# Access services directly
# Frontend: http://pandaserver.ddns.net:3000
# Backend: http://pandaserver.ddns.net:8000
```

---

## ✨ Success Checklist

- [ ] All containers running (`docker-compose ps`)
- [ ] Frontend returns `text/html` Content-Type
- [ ] Frontend displays in browser (not downloads)
- [ ] No errors in browser console (F12)
- [ ] Backend API responds (`/health` endpoint)
- [ ] Can create/start/stop containers
- [ ] GraphQL queries work

---

**Status:** Ready for deployment
**Estimated Time:** 5 minutes
**Risk Level:** Low (only config changes, no code changes)
