"""
Docker Manager Service
Handles all Docker container operations including lifecycle management,
Traefik integration, and resource monitoring.

This is the core service that interfaces with the Docker Engine API.
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
    Manager class for Docker operations.
    
    Handles:
    - Container lifecycle (create, start, stop, delete)
    - Traefik label generation for automatic routing
    - Resource monitoring (CPU, memory, network)
    - Mock mode for development without Docker
    """
    
    def __init__(self):
        """
        Initialize Docker client and check availability.
        
        Falls back to mock mode if Docker is not available,
        allowing development and testing without Docker installed.
        """
        try:
            # Connect to Docker daemon via socket or TCP
            self.client = docker.DockerClient(base_url=settings.DOCKER_HOST)
            self.api_client = docker.APIClient(base_url=settings.DOCKER_HOST)
            logger.info(f"Docker client initialized: {self.client.version()['Version']}")
            self.docker_available = True
        except DockerException as e:
            # Graceful fallback to mock mode for development
            logger.warning(f"Docker client not available: {e}")
            logger.warning("Running in mock mode - container operations will be simulated")
            self.client = None
            self.api_client = None
            self.docker_available = False
    
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
        if not self.docker_available:
            # Mock implementation for demo
            import uuid
            mock_id = str(uuid.uuid4())[:12]
            logger.info(f"Mock: Creating container: {name} (ID: {mock_id})")
            return {
                "id": mock_id,
                "name": name,
                "status": "created",
                "image": f"{image}:{tag}",
            }

        try:
            full_image = f"{image}:{tag}"

            # Pull image from Docker Hub if not cached locally
            logger.info(f"Pulling image: {full_image}")
            await asyncio.to_thread(self.client.images.pull, image, tag=tag)

            # Generate Traefik labels for automatic routing
            # Traefik watches Docker labels and auto-configures routes
            traefik_labels = {
                "traefik.enable": "true",  # Tell Traefik to route this container
                # Route rule: subdomain.domain.com -> this container
                f"traefik.http.routers.{name}.rule": f"Host(`{subdomain}.{settings.TRAEFIK_DOMAIN}`)",
                f"traefik.http.routers.{name}.entrypoints": "web",  # Use HTTP entrypoint
                # Tell Traefik which port the app listens on
                f"traefik.http.services.{name}.loadbalancer.server.port": str(internal_port),
                "traefik.docker.network": settings.DOCKER_NETWORK,  # Network to use
            }

            # Merge with any custom labels provided
            if labels:
                traefik_labels.update(labels)

            # Configure direct port mapping if requested (bypasses Traefik)
            ports = {}
            if external_port:
                ports[f"{internal_port}/tcp"] = external_port

            # Configure restart policy (important for production)
            restart_policy_config = {"Name": restart_policy}

            # Build host configuration with network and restart policy
            host_config_params = {
                "restart_policy": restart_policy_config,
                "network_mode": settings.DOCKER_NETWORK,  # Connect to loom_network
            }

            # Add resource limits if specified (prevents resource hogging)
            if memory_limit:
                host_config_params["mem_limit"] = memory_limit

            if cpu_limit:
                # Convert CPU limit to nanocpus (Docker's internal format)
                # 1.0 = 1 full CPU core, 0.5 = half a core
                host_config_params["nano_cpus"] = int(float(cpu_limit) * 1e9)

            if ports:
                host_config_params["port_bindings"] = ports

            if volumes:
                host_config_params["binds"] = volumes

            # Create the container (doesn't start it yet)
            # Using asyncio.to_thread to avoid blocking the event loop
            logger.info(f"Creating container: {name}")
            container = await asyncio.to_thread(
                self.client.containers.create,
                full_image,
                name=name,
                environment=environment or {},
                labels=traefik_labels,  # Critical: Traefik reads these
                command=command,
                detach=True,  # Run in background
                **host_config_params
            )

            logger.info(f"Container created: {name} ({container.id[:12]})")

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
        """
        Start a created container.
        
        Once started, Traefik will automatically detect it and
        configure routing based on the labels we set during creation.
        """
        if not self.docker_available:
            logger.info(f"Mock: Starting container: {container_id}")
            return {
                "id": container_id,
                "name": f"mock-{container_id[:8]}",
                "status": "running",
            }

        try:
            container = self.client.containers.get(container_id)
            await asyncio.to_thread(container.start)
            logger.info(f"Container started: {container.name}")

            return {
                "id": container.id,
                "name": container.name,
                "status": "running",
            }
        except NotFound:
            logger.error(f"Container not found: {container_id}")
            raise
        except DockerException as e:
            logger.error(f"Failed to start container: {e}")
            raise
    
    async def stop_container(self, container_id: str, timeout: int = 10) -> Dict[str, Any]:
        """
        Stop a running container gracefully.
        
        Sends SIGTERM, waits for timeout, then sends SIGKILL if needed.
        Traefik automatically removes routing when container stops.
        """
        if not self.docker_available:
            logger.info(f"Mock: Stopping container: {container_id}")
            return {
                "id": container_id,
                "name": f"mock-{container_id[:8]}",
                "status": "stopped",
            }

        try:
            container = self.client.containers.get(container_id)
            await asyncio.to_thread(container.stop, timeout=timeout)
            logger.info(f"Container stopped: {container.name}")

            return {
                "id": container.id,
                "name": container.name,
                "status": "stopped",
            }
        except NotFound:
            logger.error(f"Container not found: {container_id}")
            raise
        except DockerException as e:
            logger.error(f"Failed to stop container: {e}")
            raise
    
    async def restart_container(self, container_id: str, timeout: int = 10) -> Dict[str, Any]:
        """Restart a container"""
        try:
            container = self.client.containers.get(container_id)
            await asyncio.to_thread(container.restart, timeout=timeout)
            logger.info(f"Container restarted: {container.name}")
            
            return {
                "id": container.id,
                "name": container.name,
                "status": "running",
            }
        except NotFound:
            logger.error(f"Container not found: {container_id}")
            raise
        except DockerException as e:
            logger.error(f"Failed to restart container: {e}")
            raise
    
    async def delete_container(self, container_id: str, force: bool = False) -> bool:
        """Delete a container"""
        try:
            container = self.client.containers.get(container_id)
            container_name = container.name
            await asyncio.to_thread(container.remove, force=force)
            logger.info(f"Container deleted: {container_name}")
            return True
        except NotFound:
            logger.error(f"Container not found: {container_id}")
            raise
        except DockerException as e:
            logger.error(f"Failed to delete container: {e}")
            raise
    
    async def get_container_stats(self, container_id: str) -> Dict[str, Any]:
        """
        Get real-time container resource usage statistics.
        
        Calculates CPU percentage, memory usage, and network I/O.
        Used for monitoring and displaying resource usage in the dashboard.
        """
        try:
            container = self.client.containers.get(container_id)
            # Get stats snapshot (stream=False for single reading)
            stats = await asyncio.to_thread(container.stats, stream=False)
            
            # Calculate CPU usage percentage
            # Docker provides cumulative CPU time, we need to calculate delta
            cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                       stats["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                          stats["precpu_stats"]["system_cpu_usage"]
            cpu_usage = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0.0
            
            # Memory usage in bytes
            memory_usage = stats["memory_stats"]["usage"]
            memory_limit = stats["memory_stats"]["limit"]
            
            # Network I/O (received and transmitted bytes)
            return {
                "cpu_usage": round(cpu_usage, 2),  # Percentage
                "memory_usage": memory_usage,  # Bytes
                "memory_limit": memory_limit,  # Bytes
                "network_rx": stats["networks"]["eth0"]["rx_bytes"] if "networks" in stats else 0,
                "network_tx": stats["networks"]["eth0"]["tx_bytes"] if "networks" in stats else 0,
            }
        except NotFound:
            logger.error(f"Container not found: {container_id}")
            raise
        except DockerException as e:
            logger.error(f"Failed to get container stats: {e}")
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
        """
        Get Docker host system information.
        
        Returns Docker version, container counts, available resources.
        Useful for dashboard overview and capacity planning.
        """
        if not self.docker_available:
            # Return mock data for development
            logger.info("🎭 Mock: Getting system info")
            return {
                "docker_version": "Mock 24.0.0",
                "containers": 0,
                "containers_running": 0,
                "containers_stopped": 0,
                "images": 0,
                "memory_total": 8 * 1024**3,  # 8GB in bytes
                "cpus": 4,
            }

        try:
            # Get system info and Docker version
            info = await asyncio.to_thread(self.client.info)
            version = await asyncio.to_thread(self.client.version)

            return {
                "docker_version": version["Version"],
                "containers": info["Containers"],  # Total containers
                "containers_running": info["ContainersRunning"],
                "containers_stopped": info["ContainersStopped"],
                "images": info["Images"],  # Cached images
                "memory_total": info["MemTotal"],  # Total RAM in bytes
                "cpus": info["NCPU"],  # Number of CPU cores
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


# Create singleton instance - shared across the application
# This ensures we only have one Docker client connection
docker_manager = DockerManager()
