"""
Modpack Service - Handles automated modpack downloading and installation
Supports CurseForge, Modrinth, and FTB APIs
"""

import os
import json
import asyncio
import aiohttp
import hashlib
from typing import Dict, List, Optional, Any
from pathlib import Path
import zipfile
import shutil
from datetime import datetime, timedelta

from config.settings import settings


class ModpackAPIClient:
    """Base class for modpack API clients"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = timedelta(hours=1)
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_cache_key(self, *args) -> str:
        """Generate cache key from arguments"""
        return hashlib.md5(str(args).encode()).hexdigest()
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.cache_ttl:
                return data
            del self.cache[key]
        return None
    
    def _set_cache(self, key: str, value: Any):
        """Set cache value with timestamp"""
        self.cache[key] = (value, datetime.now())


class CurseForgeClient(ModpackAPIClient):
    """CurseForge API Client"""
    
    BASE_URL = "https://api.curseforge.com/v1"
    MINECRAFT_GAME_ID = 432
    MODPACK_CLASS_ID = 4471
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.headers = {
            "Accept": "application/json",
            "x-api-key": api_key
        }
    
    async def search_modpacks(
        self,
        query: str,
        minecraft_version: Optional[str] = None,
        loader_type: Optional[str] = None,
        page_size: int = 20
    ) -> List[Dict]:
        """Search for modpacks on CurseForge"""
        cache_key = self._get_cache_key("search", query, minecraft_version, loader_type)
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        params = {
            "gameId": self.MINECRAFT_GAME_ID,
            "classId": self.MODPACK_CLASS_ID,
            "searchFilter": query,
            "pageSize": page_size,
            "sortField": 2,  # Popularity
            "sortOrder": "desc"
        }
        
        if minecraft_version:
            params["gameVersion"] = minecraft_version
        
        if loader_type:
            params["modLoaderType"] = self._get_loader_id(loader_type)
        
        async with self.session.get(
            f"{self.BASE_URL}/mods/search",
            headers=self.headers,
            params=params
        ) as response:
            if response.status == 200:
                data = await response.json()
                modpacks = self._format_modpacks(data.get("data", []))
                self._set_cache(cache_key, modpacks)
                return modpacks
            else:
                raise Exception(f"CurseForge API error: {response.status}")
    
    async def get_modpack_details(self, modpack_id: str) -> Dict:
        """Get detailed information about a modpack"""
        cache_key = self._get_cache_key("details", modpack_id)
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        async with self.session.get(
            f"{self.BASE_URL}/mods/{modpack_id}",
            headers=self.headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                modpack = self._format_modpack(data.get("data", {}))
                self._set_cache(cache_key, modpack)
                return modpack
            else:
                raise Exception(f"CurseForge API error: {response.status}")
    
    async def get_modpack_files(self, modpack_id: str) -> List[Dict]:
        """Get available files/versions for a modpack"""
        cache_key = self._get_cache_key("files", modpack_id)
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        async with self.session.get(
            f"{self.BASE_URL}/mods/{modpack_id}/files",
            headers=self.headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                files = self._format_files(data.get("data", []))
                self._set_cache(cache_key, files)
                return files
            else:
                raise Exception(f"CurseForge API error: {response.status}")
    
    async def get_download_url(self, modpack_id: str, file_id: str) -> str:
        """Get download URL for a specific file"""
        async with self.session.get(
            f"{self.BASE_URL}/mods/{modpack_id}/files/{file_id}/download-url",
            headers=self.headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("data", "")
            else:
                raise Exception(f"CurseForge API error: {response.status}")
    
    def _get_loader_id(self, loader_type: str) -> int:
        """Convert loader type to CurseForge loader ID"""
        loaders = {
            "forge": 1,
            "fabric": 4,
            "neoforge": 6
        }
        return loaders.get(loader_type.lower(), 0)
    
    def _format_modpack(self, data: Dict) -> Dict:
        """Format modpack data to standard format"""
        return {
            "id": str(data.get("id")),
            "name": data.get("name"),
            "slug": data.get("slug"),
            "summary": data.get("summary"),
            "description": data.get("description"),
            "icon_url": data.get("logo", {}).get("url"),
            "author": data.get("authors", [{}])[0].get("name") if data.get("authors") else "Unknown",
            "download_count": data.get("downloadCount", 0),
            "date_created": data.get("dateCreated"),
            "date_modified": data.get("dateModified"),
            "source": "curseforge"
        }
    
    def _format_modpacks(self, data_list: List[Dict]) -> List[Dict]:
        """Format list of modpacks"""
        return [self._format_modpack(data) for data in data_list]
    
    def _format_files(self, data_list: List[Dict]) -> List[Dict]:
        """Format file list to standard format"""
        files = []
        for data in data_list:
            # Extract Minecraft version and loader type
            game_versions = data.get("gameVersions", [])
            mc_version = next((v for v in game_versions if v.startswith("1.")), "Unknown")
            
            files.append({
                "file_id": str(data.get("id")),
                "display_name": data.get("displayName"),
                "file_name": data.get("fileName"),
                "file_size": data.get("fileLength"),
                "minecraft_version": mc_version,
                "release_type": data.get("releaseType"),  # 1=Release, 2=Beta, 3=Alpha
                "date_published": data.get("fileDate"),
                "download_url": data.get("downloadUrl")
            })
        return files


class ModrinthClient(ModpackAPIClient):
    """Modrinth API Client"""
    
    BASE_URL = "https://api.modrinth.com/v2"
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "ASU1-Loom/1.0"
        }
        if api_key:
            self.headers["Authorization"] = api_key
    
    async def search_modpacks(
        self,
        query: str,
        minecraft_version: Optional[str] = None,
        loader_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """Search for modpacks on Modrinth"""
        cache_key = self._get_cache_key("search", query, minecraft_version, loader_type)
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        facets = [
            ["project_type:modpack"]
        ]
        
        if minecraft_version:
            facets.append([f"versions:{minecraft_version}"])
        
        if loader_type:
            facets.append([f"categories:{loader_type.lower()}"])
        
        params = {
            "query": query,
            "facets": json.dumps(facets),
            "limit": limit,
            "index": "relevance"
        }
        
        async with self.session.get(
            f"{self.BASE_URL}/search",
            headers=self.headers,
            params=params
        ) as response:
            if response.status == 200:
                data = await response.json()
                modpacks = self._format_modpacks(data.get("hits", []))
                self._set_cache(cache_key, modpacks)
                return modpacks
            else:
                raise Exception(f"Modrinth API error: {response.status}")
    
    async def get_modpack_details(self, modpack_id: str) -> Dict:
        """Get detailed information about a modpack"""
        cache_key = self._get_cache_key("details", modpack_id)
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        async with self.session.get(
            f"{self.BASE_URL}/project/{modpack_id}",
            headers=self.headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                modpack = self._format_modpack(data)
                self._set_cache(cache_key, modpack)
                return modpack
            else:
                raise Exception(f"Modrinth API error: {response.status}")
    
    async def get_modpack_versions(self, modpack_id: str) -> List[Dict]:
        """Get available versions for a modpack"""
        cache_key = self._get_cache_key("versions", modpack_id)
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        async with self.session.get(
            f"{self.BASE_URL}/project/{modpack_id}/version",
            headers=self.headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                versions = self._format_versions(data)
                self._set_cache(cache_key, versions)
                return versions
            else:
                raise Exception(f"Modrinth API error: {response.status}")
    
    def _format_modpack(self, data: Dict) -> Dict:
        """Format modpack data to standard format"""
        return {
            "id": data.get("id") or data.get("project_id"),
            "name": data.get("title"),
            "slug": data.get("slug"),
            "summary": data.get("description"),
            "description": data.get("body"),
            "icon_url": data.get("icon_url"),
            "author": data.get("author") or "Unknown",
            "download_count": data.get("downloads", 0),
            "date_created": data.get("published") or data.get("date_created"),
            "date_modified": data.get("updated") or data.get("date_modified"),
            "source": "modrinth"
        }
    
    def _format_modpacks(self, data_list: List[Dict]) -> List[Dict]:
        """Format list of modpacks"""
        return [self._format_modpack(data) for data in data_list]
    
    def _format_versions(self, data_list: List[Dict]) -> List[Dict]:
        """Format version list to standard format"""
        versions = []
        for data in data_list:
            # Get primary file (usually the server file)
            files = data.get("files", [])
            primary_file = next((f for f in files if f.get("primary")), files[0] if files else {})
            
            versions.append({
                "version_id": data.get("id"),
                "version_number": data.get("version_number"),
                "version_name": data.get("name"),
                "minecraft_versions": data.get("game_versions", []),
                "loaders": data.get("loaders", []),
                "release_type": data.get("version_type"),  # release, beta, alpha
                "date_published": data.get("date_published"),
                "downloads": data.get("downloads", 0),
                "file_name": primary_file.get("filename"),
                "file_size": primary_file.get("size"),
                "download_url": primary_file.get("url")
            })
        return versions


class FTBClient(ModpackAPIClient):
    """FTB (Feed The Beast) API Client"""
    
    BASE_URL = "https://api.modpacks.ch/public"
    
    async def get_all_modpacks(self) -> List[Dict]:
        """Get all FTB modpacks"""
        cache_key = self._get_cache_key("all_modpacks")
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        async with self.session.get(
            f"{self.BASE_URL}/modpack/all",
            headers={"Accept": "application/json"}
        ) as response:
            if response.status == 200:
                data = await response.json()
                modpacks = self._format_modpacks(data.get("packs", []))
                self._set_cache(cache_key, modpacks)
                return modpacks
            else:
                raise Exception(f"FTB API error: {response.status}")
    
    async def search_modpacks(self, query: str) -> List[Dict]:
        """Search FTB modpacks (client-side filtering)"""
        all_packs = await self.get_all_modpacks()
        query_lower = query.lower()
        return [
            pack for pack in all_packs
            if query_lower in pack["name"].lower() or
               query_lower in pack.get("summary", "").lower()
        ]
    
    async def get_modpack_details(self, modpack_id: str) -> Dict:
        """Get detailed information about an FTB modpack"""
        cache_key = self._get_cache_key("details", modpack_id)
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        async with self.session.get(
            f"{self.BASE_URL}/modpack/{modpack_id}",
            headers={"Accept": "application/json"}
        ) as response:
            if response.status == 200:
                data = await response.json()
                modpack = self._format_modpack(data)
                self._set_cache(cache_key, modpack)
                return modpack
            else:
                raise Exception(f"FTB API error: {response.status}")
    
    async def get_modpack_versions(self, modpack_id: str) -> List[Dict]:
        """Get available versions for an FTB modpack"""
        modpack = await self.get_modpack_details(modpack_id)
        versions = modpack.get("versions", [])
        return self._format_versions(versions, modpack_id)
    
    def _format_modpack(self, data: Dict) -> Dict:
        """Format modpack data to standard format"""
        return {
            "id": str(data.get("id")),
            "name": data.get("name"),
            "slug": data.get("name", "").lower().replace(" ", "-"),
            "summary": data.get("synopsis"),
            "description": data.get("description"),
            "icon_url": data.get("art", [{}])[0].get("url") if data.get("art") else None,
            "author": "Feed The Beast",
            "download_count": 0,  # FTB doesn't provide this
            "date_created": None,
            "date_modified": data.get("updated"),
            "versions": data.get("versions", []),
            "source": "ftb"
        }
    
    def _format_modpacks(self, data_list: List[Dict]) -> List[Dict]:
        """Format list of modpacks"""
        return [self._format_modpack(data) for data in data_list]
    
    def _format_versions(self, data_list: List[Dict], modpack_id: str) -> List[Dict]:
        """Format version list to standard format"""
        versions = []
        for data in data_list:
            versions.append({
                "version_id": str(data.get("id")),
                "version_number": data.get("name"),
                "minecraft_version": data.get("targets", [{}])[0].get("version") if data.get("targets") else "Unknown",
                "release_type": data.get("type"),
                "date_published": data.get("updated"),
                "server_download_url": f"{self.BASE_URL}/modpack/{modpack_id}/{data.get('id')}/server"
            })
        return versions


class ModpackDownloader:
    """Handles downloading and extracting modpack files"""
    
    def __init__(self, download_dir: str = "/tmp/loom_modpacks"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    async def download_file(
        self,
        url: str,
        destination: Path,
        progress_callback: Optional[callable] = None
    ) -> Path:
        """Download a file with progress tracking"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Download failed: HTTP {response.status}")
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(destination, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            await progress_callback(progress, downloaded, total_size)
        
        return destination
    
    async def extract_zip(
        self,
        zip_path: Path,
        extract_to: Path,
        progress_callback: Optional[callable] = None
    ) -> Path:
        """Extract a zip file with progress tracking"""
        extract_to.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            members = zip_ref.namelist()
            total_files = len(members)
            
            for i, member in enumerate(members):
                zip_ref.extract(member, extract_to)
                
                if progress_callback:
                    progress = int(((i + 1) / total_files) * 100)
                    await progress_callback(progress, i + 1, total_files)
        
        return extract_to
    
    def cleanup(self, path: Path):
        """Clean up downloaded/extracted files"""
        if path.exists():
            if path.is_file():
                path.unlink()
            else:
                shutil.rmtree(path)


class ModpackManager:
    """Main modpack management orchestrator"""
    
    def __init__(
        self,
        curseforge_api_key: Optional[str] = None,
        modrinth_api_key: Optional[str] = None
    ):
        self.curseforge_key = curseforge_api_key or os.getenv("CURSEFORGE_API_KEY")
        self.modrinth_key = modrinth_api_key or os.getenv("MODRINTH_API_KEY")
        self.downloader = ModpackDownloader()
    
    async def search_modpacks(
        self,
        query: str,
        source: str = "all",
        minecraft_version: Optional[str] = None,
        loader_type: Optional[str] = None
    ) -> List[Dict]:
        """Search for modpacks across multiple sources"""
        results = []
        
        if source in ["all", "curseforge"] and self.curseforge_key:
            async with CurseForgeClient(self.curseforge_key) as client:
                try:
                    cf_results = await client.search_modpacks(
                        query, minecraft_version, loader_type
                    )
                    results.extend(cf_results)
                except Exception as e:
                    print(f"CurseForge search error: {e}")
        
        if source in ["all", "modrinth"]:
            async with ModrinthClient(self.modrinth_key) as client:
                try:
                    mr_results = await client.search_modpacks(
                        query, minecraft_version, loader_type
                    )
                    results.extend(mr_results)
                except Exception as e:
                    print(f"Modrinth search error: {e}")
        
        if source in ["all", "ftb"]:
            async with FTBClient() as client:
                try:
                    ftb_results = await client.search_modpacks(query)
                    results.extend(ftb_results)
                except Exception as e:
                    print(f"FTB search error: {e}")
        
        return results
    
    async def get_modpack_details(self, source: str, modpack_id: str) -> Dict:
        """Get detailed information about a modpack"""
        if source == "curseforge" and self.curseforge_key:
            async with CurseForgeClient(self.curseforge_key) as client:
                return await client.get_modpack_details(modpack_id)
        
        elif source == "modrinth":
            async with ModrinthClient(self.modrinth_key) as client:
                return await client.get_modpack_details(modpack_id)
        
        elif source == "ftb":
            async with FTBClient() as client:
                return await client.get_modpack_details(modpack_id)
        
        else:
            raise ValueError(f"Unsupported source: {source}")
    
    async def get_modpack_versions(self, source: str, modpack_id: str) -> List[Dict]:
        """Get available versions for a modpack"""
        if source == "curseforge" and self.curseforge_key:
            async with CurseForgeClient(self.curseforge_key) as client:
                return await client.get_modpack_files(modpack_id)
        
        elif source == "modrinth":
            async with ModrinthClient(self.modrinth_key) as client:
                return await client.get_modpack_versions(modpack_id)
        
        elif source == "ftb":
            async with FTBClient() as client:
                return await client.get_modpack_versions(modpack_id)
        
        else:
            raise ValueError(f"Unsupported source: {source}")
    
    async def download_and_install_modpack(
        self,
        source: str,
        modpack_id: str,
        version_id: str,
        container_path: Path,
        progress_callback: Optional[callable] = None
    ) -> Path:
        """Download and install a modpack to a container directory"""
        # Get download URL
        download_url = await self._get_download_url(source, modpack_id, version_id)
        
        # Download file
        download_path = self.downloader.download_dir / f"{modpack_id}_{version_id}.zip"
        
        if progress_callback:
            await progress_callback("downloading", 0)
        
        await self.downloader.download_file(
            download_url,
            download_path,
            lambda p, d, t: progress_callback("downloading", p) if progress_callback else None
        )
        
        # Extract to container
        if progress_callback:
            await progress_callback("extracting", 50)
        
        await self.downloader.extract_zip(
            download_path,
            container_path,
            lambda p, d, t: progress_callback("extracting", 50 + int(p * 0.3)) if progress_callback else None
        )
        
        # Cleanup
        self.downloader.cleanup(download_path)
        
        if progress_callback:
            await progress_callback("complete", 100)
        
        return container_path
    
    async def _get_download_url(self, source: str, modpack_id: str, version_id: str) -> str:
        """Get download URL for a specific modpack version"""
        if source == "curseforge" and self.curseforge_key:
            async with CurseForgeClient(self.curseforge_key) as client:
                return await client.get_download_url(modpack_id, version_id)
        
        elif source == "modrinth":
            async with ModrinthClient(self.modrinth_key) as client:
                versions = await client.get_modpack_versions(modpack_id)
                version = next((v for v in versions if v["version_id"] == version_id), None)
                if version:
                    return version["download_url"]
                raise ValueError(f"Version {version_id} not found")
        
        elif source == "ftb":
            # FTB uses direct server download endpoint
            return f"{FTBClient.BASE_URL}/modpack/{modpack_id}/{version_id}/server"
        
        else:
            raise ValueError(f"Unsupported source: {source}")


# Singleton instance
_modpack_manager: Optional[ModpackManager] = None

def get_modpack_manager() -> ModpackManager:
    """Get or create the modpack manager singleton"""
    global _modpack_manager
    if _modpack_manager is None:
        _modpack_manager = ModpackManager()
    return _modpack_manager
