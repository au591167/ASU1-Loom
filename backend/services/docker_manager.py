"""
Docker Manager Service
Handles all Docker container operations
"""

import docker
from docker.errors import DockerException, NotFound, APIError
from typing import Dict, List, Optional, Any
from loguru import logger
import asyncio
from datetime import datetime

from config.settings import settings


class DockerManager:
    """
    Manager class for Docker operations
    Handles container lifecycle, networking, and monitoring
    """
    
    def __init__(self):
        """Initialize Docker client"""
        try:
            self.client = docker.DockerClient(base_url=settings.DOCKER_HOST)
            self.api_client = docker.APIClient(base_url=settings.DOCKER_HOST)
            logger.info(f"✅ Docker client initialized: {self.client.version()['Version']}")
        except DockerException as e:
            logger.error(f"❌ Failed to initialize Docker client: {e}")
            raise
    
    async def create_container(
        self,
        name: str,
        image: str,
        tag: str = "latest",
        subdomain: str = "",
        internal_port: int = 80,
        external_port: Optional[int] = None,
        environment: Optional[Dict[str, str]] = None,
        volumes: Optional[Dict[str, Dict[str, str]]] = None,
        command: Optional[str] = None,
        memory_limit: Optional[str] = None,
        cpu_limit: Optional[str] = None,
        restart_policy: str = "unless-stopped",
        labels: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new Docker container with Traefik labels
        
        Args:
            name: Container name
            image: Docker image name
            tag: Image tag
            subdomain: Subdomain for Traefik routing
            internal_port: Internal container port
            external_port: External port mapping (optional)
            environment: Environment variables
            volumes: Volume mappings
            command: Custom command to run
            memory_limit: Memory limit (e.g., "512m")
            cpu_limit: CPU limit (e.g., "0.5")
            restart_policy: Restart policy
            labels: Custom labels
        
        Returns:
            Dictionary with container information
        """
        try:
            full_image = f"{image}:{tag}"
            
            # Pull image if not exists
            logger.info(f"Pulling image: {full_image}")
            await asyncio.to_thread(self.client.images.pull, image, tag=tag)
            
            # Prepare Traefik labels
            traefik_labels = {
                "traefik.enable": "true",
                f"traefik.http.routers.{name}.rule": f"Host(`{subdomain}.{settings.TRAEFIK_DOMAIN}`)",
                f"traefik.http.routers.{name}.entrypoints": "web",
                f"traefik.http.services.{name}.loadbalancer.server.port": str(internal_port),
                "traefik.docker.network": settings.DOCKER_NETWORK,
            }
            
            # Merge with custom labels
            if labels:
                traefik_labels.update(labels)
            
            # Prepare port bindings
            ports = {}
            if external_port:
                ports[f"{internal_port}/tcp"] = external_port
            
            # Prepare restart policy
            restart_policy_config = {"Name": restart_policy}
            
            # Prepare resource limits
            host_config_params = {
                "restart_policy": restart_policy_config,
                "network_mode": settings.DOCKER_NETWORK,
            }
            
            if memory_limit:
                host_config_params["mem_limit"] = memory_limit
            
            if cpu_limit:
                host_config_params["nano_cpus"] = int(float(cpu_limit) * 1e9)
            
            if ports:
                host_config_params["port_bindings"] = ports
            
            if volumes:
                host_config_params["binds"] = volumes
            
            # Create container
            logger.info(f"Creating container: {name}")
            container = await asyncio.to_thread(
                self.client.containers.create,
                full_image,
                name=name,
                environment=environment or {},
                labels=traefik_labels,
                command=command,
                detach=True,
                **host_config_params
            )
            
            logger.info(f"✅ Container created: {name} ({container.id[:12]})")
            
            return {
                "id": container.id,
                "name": name,
                "status": "created",
                "image": full_image,
            }
            
        except DockerException as e:
            logger.error(f"❌ Failed to create container {name}: {e}")
            raise
    
    async def start_container(self, container_id: str) -> Dict[str, Any]:
        """Start a container"""
        try:
            container = self.client.containers.get(container_id)
            await asyncio.to_thread(container.start)
            logger.info(f"✅ Container started: {container.name}")
            
            return {
                "id": container.id,
                "name": container.name,
                "status": "running",
            }
        except NotFound:
            logger.error(f"❌ Container not found: {container_id}")
            raise
        except DockerException as e:
            logger.error(f"❌ Failed to start container: {e}")
            raise
    
    async def stop_container(self, container_id: str, timeout: int = 10) -> Dict[str, Any]:
        """Stop a container"""
        try:
            container = self.client.containers.get(container_id)
            await asyncio.to_thread(container.stop, timeout=timeout)
            logger.info(f"✅ Container stopped: {container.name}")
            
            return {
                "id": container.id,
                "name": container.name,
                "status": "stopped",
            }
        except NotFound:
            logger.error(f"❌ Container not found: {container_id}")
            raise
        except DockerException as e:
            logger.error(f"❌ Failed to stop container: {e}")
            raise
    
    async def restart_container(self, container_id: str, timeout: int = 10) -> Dict[str, Any]:
        """Restart a container"""
        try:
            container = self.client.containers.get(container_id)
            await asyncio.to_thread(container.restart, timeout=timeout)
            logger.info(f"✅ Container restarted: {container.name}")
            
            return {
                "id": container.id,
                "name": container.name,
                "status": "running",
            }
        except NotFound:
            logger.error(f"❌ Container not found: {container_id}")
            raise
        except DockerException as e:
            logger.error(f"❌ Failed to restart container: {e}")
            raise
    
    async def delete_container(self, container_id: str, force: bool = False) -> bool:
        """Delete a container"""
        try:
            container = self.client.containers.get(container_id)
            container_name = container.name
            await asyncio.to_thread(container.remove, force=force)
            logger.info(f"✅ Container deleted: {container_name}")
            return True
        except NotFound:
            logger.error(f"❌ Container not found: {container_id}")
            raise
        except DockerException as e:
            logger.error(f"❌ Failed to delete container: {e}")
            raise
    
    async def get_container_stats(self, container_id: str) -> Dict[str, Any]:
        """Get container statistics"""
        try:
            container = self.client.containers.get(container_id)
            stats = await asyncio.to_thread(container.stats, stream=False)
            
            # Parse stats
            cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                       stats["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                          stats["precpu_stats"]["system_cpu_usage"]
            cpu_usage = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0.0
            
            memory_usage = stats["memory_stats"]["usage"]
            memory_limit = stats["memory_stats"]["limit"]
            
            return {
                "cpu_usage": round(cpu_usage, 2),
                "memory_usage": memory_usage,
                "memory_limit": memory_limit,
                "network_rx": stats["networks"]["eth0"]["rx_bytes"] if "networks" in stats else 0,
                "network_tx": stats["networks"]["eth0"]["tx_bytes"] if "networks" in stats else 0,
            }
        except NotFound:
            logger.error(f"❌ Container not found: {container_id}")
            raise
        except DockerException as e:
            logger.error(f"❌ Failed to get container stats: {e}")
            raise
    
    async def list_containers(self, all: bool = True) -> List[Dict[str, Any]]:
        """List all containers"""
        try:
            containers = await asyncio.to_thread(self.client.containers.list, all=all)
            return [
                {
                    "id": c.id,
                    "name": c.name,
                    "status": c.status,
                    "image": c.image.tags[0] if c.image.tags else "unknown",
                }
                for c in containers
            ]
        except DockerException as e:
            logger.error(f"❌ Failed to list containers: {e}")
            raise
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get Docker system information"""
        try:
            info = await asyncio.to_thread(self.client.info)
            version = await asyncio.to_thread(self.client.version)
            
            return {
                "docker_version": version["Version"],
                "containers": info["Containers"],
                "containers_running": info["ContainersRunning"],
                "containers_stopped": info["ContainersStopped"],
                "images": info["Images"],
                "memory_total": info["MemTotal"],
                "cpus": info["NCPU"],
            }
        except DockerException as e:
            logger.error(f"❌ Failed to get system info: {e}")
            raise
    
    def close(self):
        """Close Docker client"""
        try:
            self.client.close()
            logger.info("Docker client closed")
        except Exception as e:
            logger.error(f"Error closing Docker client: {e}")


# Create singleton instance
docker_manager = DockerManager()
