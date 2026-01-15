# ASU1-Loom TODO List

## 🚀 Future Enhancements

### High Priority

#### 1. Enhanced Container Status Display
**Status:** Not Started  
**Priority:** High  
**Description:** Add detailed container status indicators in frontend

**Current State:**
- Only shows basic "running" or "stopped" status
- No indication of container health or errors

**Desired Features:**
- ✅ **Running** - Container is healthy and operational
- ⚠️ **Warning** - Container running but with issues
- 🔄 **Restarting** - Container in restart loop
- ❌ **Error** - Container failed to start
- 🛑 **Stopped** - Container intentionally stopped
- ⏸️ **Paused** - Container paused
- 🔨 **Creating** - Container being created
- 📦 **Exited** - Container exited (with exit code)

**Implementation Plan:**
1. **Backend Changes:**
   - Extend `docker_manager.py` to fetch detailed container state
   - Add health check status to GraphQL schema
   - Include restart count and exit codes
   
2. **Frontend Changes:**
   - Update `ContainerType` in schema to include:
     - `healthStatus: String`
     - `restartCount: Int`
     - `exitCode: Int`
     - `lastError: String`
   - Add status badge component with icons and colors
   - Show tooltip with detailed status info on hover
   
3. **Real-Time Updates:**
   - Consider WebSocket for live status updates
   - Or polling every 5-10 seconds for status refresh

**Files to Modify:**
- `backend/services/docker_manager.py` - Add `get_container_health()` method
- `backend/api/schema.py` - Extend `ContainerType` with health fields
- `frontend/dist/app.js` - Update `createContainerCard()` function
- `frontend/dist/styles.css` - Add status badge styles

**Example Status Badge:**
```html
<span class="status-badge status-restarting">
  🔄 Restarting (3 attempts)
</span>
```

---

### Medium Priority

#### 2. Container Logs Viewer
**Status:** Not Started  
**Priority:** Medium  
**Description:** Add ability to view container logs from UI

**Features:**
- View last 100 lines of logs
- Real-time log streaming
- Download logs as file
- Filter by log level

---

#### 3. Resource Usage Graphs
**Status:** Not Started  
**Priority:** Medium  
**Description:** Add charts showing CPU/Memory usage over time

**Features:**
- Line charts for CPU and memory
- Historical data (last 24 hours)
- Alerts when thresholds exceeded

---

#### 4. Bulk Container Operations
**Status:** Not Started  
**Priority:** Low  
**Description:** Allow starting/stopping multiple containers at once

**Features:**
- Checkbox selection
- Bulk start/stop/restart/delete
- Confirmation dialog

---

### Low Priority

#### 5. Container Templates Import/Export
**Status:** Not Started  
**Priority:** Low  
**Description:** Allow users to save and share custom templates

---

#### 6. Backup and Restore
**Status:** Not Started  
**Priority:** Low  
**Description:** Backup container configurations and volumes

---

## 🐛 Known Issues

### Minor Issues
- [ ] Browser cache sometimes prevents WASM validator updates (need hard refresh)
- [ ] No loading indicator when creating containers (just notification)

---

## ✅ Completed

- [x] WASM real-time validation system
- [x] EULA checkbox bug fix
- [x] Docker network configuration
- [x] Template system with 13 templates
- [x] GraphQL API
- [x] Traefik integration

---

## 📝 Notes

**Remember:** After exam, prioritize the container status display feature as it significantly improves UX and helps debug issues faster!

**Created:** 2025-01-15  
**Last Updated:** 2025-01-15
