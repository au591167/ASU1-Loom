# 🎮 Modpack Automation Implementation Plan

## Overview
Add 1-click modpack/server deployment with automatic file downloading and setup, similar to FTB/NeoForge installers.

---

## 📋 Available APIs & Resources

### 1. **CurseForge API** (Primary - Most Popular)
- **URL**: https://docs.curseforge.com/
- **Authentication**: API Key required (free tier available)
- **Coverage**: 
  - FTB Modpacks
  - Custom modpacks
  - Individual mods
  - Server files
- **Endpoints**:
  - `/v1/mods/search` - Search for modpacks
  - `/v1/mods/{modId}/files` - Get modpack files
  - `/v1/mods/{modId}/files/{fileId}/download-url` - Get download URL
- **Rate Limits**: Generous (varies by tier)
- **Registration**: https://console.curseforge.com/

### 2. **Modrinth API** (Alternative - Open Source Friendly)
- **URL**: https://docs.modrinth.com/
- **Authentication**: Optional API key (recommended for higher limits)
- **Coverage**:
  - Modern modpacks
  - Fabric/Forge/NeoForge mods
  - Server files
- **Endpoints**:
  - `/v2/search` - Search projects
  - `/v2/project/{id}/version` - Get versions
  - `/v2/version/{id}` - Get version details with download URLs
- **Rate Limits**: 300 requests/minute (unauthenticated), higher with key
- **Registration**: https://modrinth.com/settings/account

### 3. **FTB API** (FTB Specific)
- **URL**: https://api.modpacks.ch/
- **Authentication**: None required for public endpoints
- **Coverage**: FTB official modpacks only
- **Endpoints**:
  - `/public/modpack/all` - List all modpacks
  - `/public/modpack/{id}` - Get modpack details
  - `/public/modpack/{id}/{version}/server` - Get server files
- **Rate Limits**: Reasonable for personal use

### 4. **Minecraft Version Manifest** (Vanilla)
- **URL**: https://launchermeta.mojang.com/mc/game/version_manifest.json
- **Authentication**: None
- **Coverage**: Official Minecraft server JARs
- **No rate limits** for reasonable use

### 5. **PaperMC API** (Paper/Spigot)
- **URL**: https://api.papermc.io/v2/
- **Authentication**: None
- **Coverage**: Paper, Velocity, Waterfall builds
- **Endpoints**:
  - `/projects/paper` - Get Paper info
  - `/projects/paper/versions/{version}/builds` - Get builds
  - `/projects/paper/versions/{version}/builds/{build}/downloads/{download}` - Download

### 6. **Forge/NeoForge Maven** (Forge Installers)
- **Forge**: https://files.minecraftforge.net/
- **NeoForge**: https://maven.neoforged.net/
- **Authentication**: None
- **Coverage**: Forge/NeoForge installers and libraries

---

## 🏗️ Implementation Architecture

### Phase 1: Backend API Integration Service

```
backend/services/modpack_service.py
├── CurseForgeClient
├── ModrinthClient  
├── FTBClient
├── MinecraftClient
├── PaperMCClient
└── ModpackManager (orchestrator)
```

### Phase 2: Database Schema Extension

```sql
-- New tables
CREATE TABLE modpacks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    slug VARCHAR(255),
    source VARCHAR(50), -- 'curseforge', 'modrinth', 'ftb'
    source_id VARCHAR(255),
    version VARCHAR(50),
    minecraft_version VARCHAR(50),
    loader_type VARCHAR(50), -- 'forge', 'neoforge', 'fabric', 'vanilla'
    description TEXT,
    icon_url TEXT,
    download_url TEXT,
    file_size BIGINT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE modpack_downloads (
    id SERIAL PRIMARY KEY,
    container_id INTEGER REFERENCES containers(id),
    modpack_id INTEGER REFERENCES modpacks(id),
    status VARCHAR(50), -- 'pending', 'downloading', 'installing', 'complete', 'failed'
    progress INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

### Phase 3: Frontend Template Enhancement

Add modpack selection to Minecraft templates:
- Search/browse modpacks
- Preview modpack details
- One-click deployment
- Progress tracking

---

## 🔧 Implementation Steps

### Step 1: API Key Setup
1. Register for CurseForge API key
2. Register for Modrinth API key (optional but recommended)
3. Store keys in environment variables

### Step 2: Backend Service Layer
```python
# backend/services/modpack_service.py
class ModpackManager:
    def search_modpacks(query, source='all', loader=None, mc_version=None)
    def get_modpack_details(source, modpack_id)
    def get_modpack_versions(source, modpack_id)
    def download_modpack(source, modpack_id, version, destination)
    def install_modpack(container_id, modpack_path)
```

### Step 3: GraphQL Schema Extension
```graphql
type Modpack {
    id: ID!
    name: String!
    slug: String!
    source: String!
    version: String!
    minecraftVersion: String!
    loaderType: String!
    description: String
    iconUrl: String
    downloadUrl: String
    fileSize: Int
}

type ModpackDownload {
    id: ID!
    containerId: ID!
    modpack: Modpack!
    status: String!
    progress: Int!
    errorMessage: String
}

extend type Query {
    searchModpacks(query: String!, source: String, loader: String, mcVersion: String): [Modpack!]!
    getModpack(source: String!, modpackId: String!): Modpack
    getModpackVersions(source: String!, modpackId: String!): [Modpack!]!
}

extend type Mutation {
    createContainerWithModpack(
        name: String!
        subdomain: String!
        source: String!
        modpackId: String!
        version: String!
    ): Container!
}
```

### Step 4: Frontend Modpack Browser
- Add modpack search interface
- Display modpack cards with icons
- Show version selector
- Integrate with container creation modal

### Step 5: Docker Container Enhancement
- Mount modpack files as volumes
- Auto-accept EULA
- Auto-configure server.properties
- Handle mod installation
- Run server setup scripts

---

## 🎯 User Flow

### One-Click Deployment Flow:
1. User clicks "Create Container" → "Minecraft" → "Forge/NeoForge/Fabric"
2. **NEW**: "Browse Modpacks" button appears
3. User searches/browses modpacks (e.g., "FTB Skies")
4. User selects modpack and version
5. User enters container name and subdomain
6. System automatically:
   - Downloads modpack files
   - Extracts to container volume
   - Installs Forge/NeoForge/Fabric
   - Configures server.properties
   - Accepts EULA
   - Starts server
7. Server ready in 2-5 minutes!

---

## 📦 Required Environment Variables

```env
# CurseForge
CURSEFORGE_API_KEY=your_key_here

# Modrinth (optional)
MODRINTH_API_KEY=your_key_here

# Download settings
MODPACK_DOWNLOAD_DIR=/var/loom/modpacks
MODPACK_CACHE_ENABLED=true
MODPACK_CACHE_TTL=86400
```

---

## 🔒 Security Considerations

1. **API Key Protection**: Store in environment variables, never in code
2. **Download Validation**: Verify file hashes/checksums
3. **Size Limits**: Implement max download size (e.g., 2GB)
4. **Rate Limiting**: Respect API rate limits
5. **Malware Scanning**: Optional virus scan on downloaded files
6. **User Quotas**: Limit downloads per user/time period

---

## 📊 Progress Tracking

Implement real-time progress updates:
- WebSocket connection for live updates
- Progress bar showing:
  - Download progress (0-50%)
  - Extraction progress (50-70%)
  - Installation progress (70-90%)
  - Configuration progress (90-100%)

---

## 🧪 Testing Strategy

### Unit Tests
- API client methods
- Download/extraction logic
- Installation scripts

### Integration Tests
- End-to-end modpack deployment
- Multiple sources (CurseForge, Modrinth, FTB)
- Different loader types (Forge, NeoForge, Fabric)

### Manual Testing
- Deploy popular modpacks:
  - FTB Skies (NeoForge)
  - All the Mods 9 (NeoForge)
  - Vault Hunters (Forge)
  - Fabulously Optimized (Fabric)

---

## 🚀 Future Enhancements

1. **Mod Management**: Add/remove individual mods
2. **Auto-Updates**: Automatically update modpacks
3. **Backup/Restore**: Save world data before updates
4. **Custom Modpacks**: Upload custom modpack zips
5. **Mod Recommendations**: Suggest compatible mods
6. **Performance Profiles**: Optimize JVM args per modpack

---

## 📝 Implementation Priority

### Phase 1 (MVP) - Week 1
- [ ] CurseForge API integration
- [ ] Basic modpack search
- [ ] Download & install for Forge modpacks
- [ ] Simple progress tracking

### Phase 2 - Week 2
- [ ] Modrinth API integration
- [ ] NeoForge support
- [ ] Fabric support
- [ ] Enhanced UI with modpack browser

### Phase 3 - Week 3
- [ ] FTB API integration
- [ ] Real-time progress via WebSocket
- [ ] Caching system
- [ ] Error handling & retry logic

### Phase 4 - Week 4
- [ ] Auto-configuration
- [ ] Performance optimization
- [ ] Testing & bug fixes
- [ ] Documentation

---

## 🎓 Learning Resources

- [CurseForge API Docs](https://docs.curseforge.com/)
- [Modrinth API Docs](https://docs.modrinth.com/)
- [Minecraft Server Setup Guide](https://minecraft.fandom.com/wiki/Tutorials/Setting_up_a_server)
- [Docker Volumes Best Practices](https://docs.docker.com/storage/volumes/)

---

## ✅ Success Criteria

1. User can search and browse modpacks from multiple sources
2. One-click deployment creates fully functional server
3. Server starts successfully with all mods loaded
4. Progress is clearly communicated to user
5. Error handling provides clear feedback
6. System respects API rate limits
7. Downloads are cached to reduce API calls

---

**Next Step**: Get API keys and start implementing Phase 1! 🚀
