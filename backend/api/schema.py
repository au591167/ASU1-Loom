"""
GraphQL Schema for ASU1-Loom API

Defines the GraphQL API using Strawberry.
This is the interface between the frontend and backend, providing:
- Queries: Read operations (get containers, stats, system info)
- Mutations: Write operations (create, start, stop, delete containers)
- Types: Data structures returned to the frontend
"""

import strawberry
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select
from database.connection import get_db
from models.container import Container
from services.docker_manager import docker_manager
from services.modpack_service import get_modpack_manager
from loguru import logger

# JSON scalar type for flexible data structures (environment vars, labels, etc.)
JSON = strawberry.scalars.JSON


# ============================================================================
# GraphQL Types - Define the shape of data returned to frontend
# ============================================================================

@strawberry.type
class ContainerType:
    """
    Container data structure returned to frontend.
    
    Maps database Container model to GraphQL type.
    Includes all container configuration and status information.
    """
    id: strawberry.ID  # Database ID
    container_id: Optional[str]  # Docker container ID (12-char hash)
    name: str  # Unique container name
    image: str  # Docker image (e.g., "nginx", "minecraft-server")
    tag: str  # Image version tag
    subdomain: str  # Subdomain for Traefik routing
    internal_port: int  # Port app listens on inside container
    external_port: Optional[int]  # Optional direct port mapping
    environment_vars: JSON  # Environment variables as JSON
    volumes: JSON  # Volume mounts as JSON
    command: Optional[str]  # Custom command override
    memory_limit: Optional[str]  # RAM limit (e.g., "512m")
    cpu_limit: Optional[str]  # CPU limit (e.g., "0.5")
    status: str  # Container status (created, running, stopped)
    restart_policy: str  # Restart policy (unless-stopped, always, no)
    description: Optional[str]  # User description
    labels: JSON  # Docker labels as JSON
    created_at: datetime  # When container was created
    updated_at: datetime  # Last update time
    started_at: Optional[datetime]  # When last started
    stopped_at: Optional[datetime]  # When last stopped
    user_id: Optional[int]  # Owner user ID (for multi-user support)
    
    @strawberry.field
    def port(self) -> int:
        """
        Alias for internal_port for frontend compatibility.
        Some frontend code uses 'port' instead of 'internal_port'.
        """
        return self.internal_port


@strawberry.type
class UserType:
    """GraphQL type for User"""
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]


@strawberry.type
class ContainerStatsType:
    """GraphQL type for Container Statistics"""
    cpu_usage: float
    memory_usage: float
    memory_limit: float
    network_rx: float
    network_tx: float


@strawberry.type
class SystemInfoType:
    """GraphQL type for System Information"""
    total_containers: int
    running_containers: int
    stopped_containers: int
    total_images: int
    docker_version: str
    system_memory: str
    system_cpu: str


@strawberry.type
class ModpackType:
    """GraphQL type for Modpack"""
    id: str
    name: str
    slug: str
    summary: Optional[str]
    description: Optional[str]
    icon_url: Optional[str]
    author: str
    download_count: int
    date_created: Optional[str]
    date_modified: Optional[str]
    source: str  # curseforge, modrinth, ftb


@strawberry.type
class ModpackVersionType:
    """GraphQL type for Modpack Version"""
    version_id: str
    version_number: Optional[str]
    version_name: Optional[str]
    minecraft_versions: Optional[List[str]]
    loaders: Optional[List[str]]
    release_type: Optional[str]
    date_published: Optional[str]
    downloads: Optional[int]
    file_name: Optional[str]
    file_size: Optional[int]
    download_url: Optional[str]


@strawberry.type
class ModpackDownloadProgressType:
    """GraphQL type for Modpack Download Progress"""
    container_id: int
    modpack_id: str
    status: str  # pending, downloading, extracting, installing, complete, failed
    progress: int  # 0-100
    message: Optional[str]
    error_message: Optional[str]


# Input Types
@strawberry.input
class CreateContainerInput:
    """Input type for creating a container"""
    name: str
    image: str
    tag: str = "latest"
    subdomain: str
    internal_port: int
    external_port: Optional[int] = None
    environment_vars: Optional[JSON] = None
    volumes: Optional[JSON] = None
    command: Optional[str] = None
    memory_limit: Optional[str] = None
    cpu_limit: Optional[str] = None
    restart_policy: str = "unless-stopped"
    description: Optional[str] = None
    labels: Optional[JSON] = None


# Duplicate input type for frontend compatibility (frontend uses ContainerInput)
@strawberry.input
class ContainerInput:
    """Input type for creating a container (frontend compatibility alias)"""
    name: str
    image: str
    tag: str = "latest"
    subdomain: str
    internal_port: int
    external_port: Optional[int] = None
    environment_vars: Optional[JSON] = None
    volumes: Optional[JSON] = None
    command: Optional[str] = None
    memory_limit: Optional[str] = None
    cpu_limit: Optional[str] = None
    restart_policy: str = "unless-stopped"
    description: Optional[str] = None
    labels: Optional[JSON] = None


@strawberry.input
class UpdateContainerInput:
    """Input type for updating a container"""
    name: Optional[str] = None
    environment_vars: Optional[JSON] = None
    memory_limit: Optional[str] = None
    cpu_limit: Optional[str] = None
    description: Optional[str] = None
    labels: Optional[JSON] = None


# Query
@strawberry.type
class Query:
    """GraphQL Queries"""

    @strawberry.field
    async def containers(self) -> List[ContainerType]:
        """Get all containers"""
        async for session in get_db():
            try:
                result = await session.execute(
                    select(Container).order_by(Container.created_at.desc())
                )
                containers = result.scalars().all()
                return [
                    ContainerType(
                        id=c.id,
                        container_id=c.container_id,
                        name=c.name,
                        image=c.image,
                        tag=c.tag,
                        subdomain=c.subdomain,
                        internal_port=c.internal_port,
                        external_port=c.external_port,
                        environment_vars=c.environment_vars,
                        volumes=c.volumes,
                        command=c.command,
                        memory_limit=c.memory_limit,
                        cpu_limit=c.cpu_limit,
                        status=c.status,
                        restart_policy=c.restart_policy,
                        description=c.description,
                        labels=c.labels,
                        created_at=c.created_at,
                        updated_at=c.updated_at,
                        started_at=c.started_at,
                        stopped_at=c.stopped_at,
                        user_id=c.user_id,
                    )
                    for c in containers
                ]
            except Exception as e:
                logger.error(f"Error fetching containers: {e}")
                return []
    
    @strawberry.field
    async def container(self, id: strawberry.ID) -> Optional[ContainerType]:
        """Get container by ID"""
        try:
            container_id = int(id)
        except ValueError:
            return None

        async for session in get_db():
            try:
                result = await session.execute(
                    select(Container).where(Container.id == container_id)
                )
                c = result.scalar_one_or_none()
                if c:
                    return ContainerType(
                        id=c.id,
                        container_id=c.container_id,
                        name=c.name,
                        image=c.image,
                        tag=c.tag,
                        subdomain=c.subdomain,
                        internal_port=c.internal_port,
                        external_port=c.external_port,
                        environment_vars=c.environment_vars,
                        volumes=c.volumes,
                        command=c.command,
                        memory_limit=c.memory_limit,
                        cpu_limit=c.cpu_limit,
                        status=c.status,
                        restart_policy=c.restart_policy,
                        description=c.description,
                        labels=c.labels,
                        created_at=c.created_at,
                        updated_at=c.updated_at,
                        started_at=c.started_at,
                        stopped_at=c.stopped_at,
                        user_id=c.user_id,
                    )
            except Exception as e:
                logger.error(f"Error fetching container {id}: {e}")
            return None

    @strawberry.field
    async def container_by_name(self, name: str) -> Optional[ContainerType]:
        """Get container by name"""
        async for session in get_db():
            try:
                result = await session.execute(
                    select(Container).where(Container.name == name)
                )
                c = result.scalar_one_or_none()
                if c:
                    return ContainerType(
                        id=c.id,
                        container_id=c.container_id,
                        name=c.name,
                        image=c.image,
                        tag=c.tag,
                        subdomain=c.subdomain,
                        internal_port=c.internal_port,
                        external_port=c.external_port,
                        environment_vars=c.environment_vars,
                        volumes=c.volumes,
                        command=c.command,
                        memory_limit=c.memory_limit,
                        cpu_limit=c.cpu_limit,
                        status=c.status,
                        restart_policy=c.restart_policy,
                        description=c.description,
                        labels=c.labels,
                        created_at=c.created_at,
                        updated_at=c.updated_at,
                        started_at=c.started_at,
                        stopped_at=c.stopped_at,
                        user_id=c.user_id,
                    )
            except Exception as e:
                logger.error(f"Error fetching container by name {name}: {e}")
            return None

    @strawberry.field
    async def container_stats(self, id: strawberry.ID) -> Optional[ContainerStatsType]:
        """Get container statistics"""
        try:
            container_id = int(id)
        except ValueError:
            return None

        async for session in get_db():
            try:
                result = await session.execute(
                    select(Container).where(Container.id == container_id)
                )
                c = result.scalar_one_or_none()
                if c and c.container_id:
                    stats = await docker_manager.get_container_stats(c.container_id)
                    return ContainerStatsType(
                        cpu_usage=stats["cpu_usage"],
                        memory_usage=stats["memory_usage"],
                        memory_limit=stats["memory_limit"],
                        network_rx=stats["network_rx"],
                        network_tx=stats["network_tx"],
                    )
            except Exception as e:
                logger.error(f"Error fetching container stats {id}: {e}")
            return None

    @strawberry.field
    async def system_info(self) -> SystemInfoType:
        """Get system information"""
        try:
            info = await docker_manager.get_system_info()
            return SystemInfoType(
                total_containers=info["containers"],
                running_containers=info["containers_running"],
                stopped_containers=info["containers_stopped"],
                total_images=info["images"],
                docker_version=info["docker_version"],
                system_memory=f"{info['memory_total'] // (1024**3)} GB",
                system_cpu=str(info["cpus"]),
            )
        except Exception as e:
            logger.error(f"Error fetching system info: {e}")
            return SystemInfoType(
                total_containers=0,
                running_containers=0,
                stopped_containers=0,
                total_images=0,
                docker_version="unknown",
                system_memory="unknown",
                system_cpu="unknown",
            )
    
    @strawberry.field
    async def search_modpacks(
        self,
        query: str,
        source: str = "all",
        minecraft_version: Optional[str] = None,
        loader_type: Optional[str] = None
    ) -> List[ModpackType]:
        """Search for modpacks across multiple sources"""
        try:
            modpack_manager = get_modpack_manager()
            results = await modpack_manager.search_modpacks(
                query=query,
                source=source,
                minecraft_version=minecraft_version,
                loader_type=loader_type
            )
            return [
                ModpackType(
                    id=r["id"],
                    name=r["name"],
                    slug=r["slug"],
                    summary=r.get("summary"),
                    description=r.get("description"),
                    icon_url=r.get("icon_url"),
                    author=r["author"],
                    download_count=r["download_count"],
                    date_created=r.get("date_created"),
                    date_modified=r.get("date_modified"),
                    source=r["source"]
                )
                for r in results
            ]
        except Exception as e:
            logger.error(f"Error searching modpacks: {e}")
            return []
    
    @strawberry.field
    async def get_modpack(self, source: str, modpack_id: str) -> Optional[ModpackType]:
        """Get detailed information about a modpack"""
        # TODO: Implement
        return None
    
    @strawberry.field
    async def get_modpack_versions(
        self,
        source: str,
        modpack_id: str
    ) -> List[ModpackVersionType]:
        """Get available versions for a modpack"""
        # TODO: Implement
        return []


# Mutation
@strawberry.type
class Mutation:
    """GraphQL Mutations"""

    @strawberry.mutation
    async def create_container(self, input: ContainerInput) -> ContainerType:
        """
        Create a new container - the main mutation called from frontend.
        
        This is a two-step process:
        1. Create container in Docker (via docker_manager)
        2. Save metadata to PostgreSQL database
        
        This ensures we have both the running container and persistent metadata.
        """
        async for session in get_db():
            try:
                # Step 1: Create container in Docker
                # This calls docker_manager.create_container() which:
                # - Pulls the image if needed
                # - Generates Traefik labels for routing
                # - Creates the container (but doesn't start it)
                docker_result = await docker_manager.create_container(
                    name=input.name,
                    image=input.image,
                    tag=input.tag,
                    subdomain=input.subdomain,
                    internal_port=input.internal_port,
                    external_port=input.external_port,
                    environment=input.environment_vars,
                    volumes=input.volumes,
                    command=input.command,
                    memory_limit=input.memory_limit,
                    cpu_limit=input.cpu_limit,
                    restart_policy=input.restart_policy,
                    labels=input.labels,
                )

                # Step 2: Save container metadata to database
                # This allows us to track containers even if Docker restarts
                # and provides additional metadata not stored in Docker
                container = Container(
                    container_id=docker_result["id"],  # Docker's container ID
                    name=input.name,
                    image=input.image,
                    tag=input.tag,
                    subdomain=input.subdomain,
                    internal_port=input.internal_port,
                    external_port=input.external_port,
                    environment_vars=input.environment_vars or {},
                    volumes=input.volumes or [],
                    command=input.command,
                    memory_limit=input.memory_limit,
                    cpu_limit=input.cpu_limit,
                    status="created",  # Initial status
                    restart_policy=input.restart_policy,
                    description=input.description,
                    labels=input.labels or {},
                )
                session.add(container)
                await session.commit()  # Persist to database
                await session.refresh(container)  # Get auto-generated fields (id, timestamps)

                logger.info(f"Created container: {input.name}")

                # Return ContainerType to frontend
                return ContainerType(
                    id=container.id,
                    container_id=container.container_id,
                    name=container.name,
                    image=container.image,
                    tag=container.tag,
                    subdomain=container.subdomain,
                    internal_port=container.internal_port,
                    external_port=container.external_port,
                    environment_vars=container.environment_vars,
                    volumes=container.volumes,
                    command=container.command,
                    memory_limit=container.memory_limit,
                    cpu_limit=container.cpu_limit,
                    status=container.status,
                    restart_policy=container.restart_policy,
                    description=container.description,
                    labels=container.labels,
                    created_at=container.created_at,
                    updated_at=container.updated_at,
                    started_at=container.started_at,
                    stopped_at=container.stopped_at,
                    user_id=container.user_id,
                )
            except Exception as e:
                # Rollback database changes if anything fails
                await session.rollback()
                logger.error(f"Error creating container: {e}")
                raise  # Re-raise to return error to frontend
    
    @strawberry.mutation
    async def update_container(self, id: strawberry.ID, input: UpdateContainerInput) -> ContainerType:
        """Update an existing container"""
        async for session in get_db():
            try:
                result = await session.execute(
                    select(Container).where(Container.id == int(id))
                )
                container = result.scalar_one_or_none()
                if not container:
                    raise ValueError(f"Container {id} not found")

                # Update fields
                if input.name is not None:
                    container.name = input.name
                if input.environment_vars is not None:
                    container.environment_vars = input.environment_vars
                if input.memory_limit is not None:
                    container.memory_limit = input.memory_limit
                if input.cpu_limit is not None:
                    container.cpu_limit = input.cpu_limit
                if input.description is not None:
                    container.description = input.description
                if input.labels is not None:
                    container.labels = input.labels

                await session.commit()
                await session.refresh(container)

                logger.info(f"Updated container: {container.name}")

                return ContainerType(
                    id=container.id,
                    container_id=container.container_id,
                    name=container.name,
                    image=container.image,
                    tag=container.tag,
                    subdomain=container.subdomain,
                    internal_port=container.internal_port,
                    external_port=container.external_port,
                    environment_vars=container.environment_vars,
                    volumes=container.volumes,
                    command=container.command,
                    memory_limit=container.memory_limit,
                    cpu_limit=container.cpu_limit,
                    status=container.status,
                    restart_policy=container.restart_policy,
                    description=container.description,
                    labels=container.labels,
                    created_at=container.created_at,
                    updated_at=container.updated_at,
                    started_at=container.started_at,
                    stopped_at=container.stopped_at,
                    user_id=container.user_id,
                )
            except Exception as e:
                await session.rollback()
                logger.error(f"Error updating container {id}: {e}")
                raise

    @strawberry.mutation
    async def delete_container(self, id: strawberry.ID) -> bool:
        """Delete a container"""
        async for session in get_db():
            try:
                result = await session.execute(
                    select(Container).where(Container.id == int(id))
                )
                container = result.scalar_one_or_none()
                if not container:
                    return False

                # Delete from Docker if it exists
                if container.container_id:
                    try:
                        await docker_manager.delete_container(container.container_id, force=True)
                    except Exception as e:
                        logger.warning(f"Failed to delete container from Docker: {e}")

                # Delete from database
                await session.delete(container)
                await session.commit()

                logger.info(f"Deleted container: {container.name}")
                return True
            except Exception as e:
                await session.rollback()
                logger.error(f"Error deleting container {id}: {e}")
                return False

    @strawberry.mutation
    async def start_container(self, id: strawberry.ID) -> ContainerType:
        """Start a container"""
        async for session in get_db():
            try:
                result = await session.execute(
                    select(Container).where(Container.id == int(id))
                )
                container = result.scalar_one_or_none()
                if not container or not container.container_id:
                    raise ValueError(f"Container {id} not found or has no container_id")

                # Start in Docker
                await docker_manager.start_container(container.container_id)

                # Update database
                container.status = "running"
                container.started_at = datetime.utcnow()
                container.stopped_at = None
                await session.commit()
                await session.refresh(container)

                logger.info(f"Started container: {container.name}")

                return ContainerType(
                    id=container.id,
                    container_id=container.container_id,
                    name=container.name,
                    image=container.image,
                    tag=container.tag,
                    subdomain=container.subdomain,
                    internal_port=container.internal_port,
                    external_port=container.external_port,
                    environment_vars=container.environment_vars,
                    volumes=container.volumes,
                    command=container.command,
                    memory_limit=container.memory_limit,
                    cpu_limit=container.cpu_limit,
                    status=container.status,
                    restart_policy=container.restart_policy,
                    description=container.description,
                    labels=container.labels,
                    created_at=container.created_at,
                    updated_at=container.updated_at,
                    started_at=container.started_at,
                    stopped_at=container.stopped_at,
                    user_id=container.user_id,
                )
            except Exception as e:
                await session.rollback()
                logger.error(f"Error starting container {id}: {e}")
                raise

    @strawberry.mutation
    async def stop_container(self, id: strawberry.ID) -> ContainerType:
        """Stop a container"""
        async for session in get_db():
            try:
                result = await session.execute(
                    select(Container).where(Container.id == int(id))
                )
                container = result.scalar_one_or_none()
                if not container or not container.container_id:
                    raise ValueError(f"Container {id} not found or has no container_id")

                # Stop in Docker
                await docker_manager.stop_container(container.container_id)

                # Update database
                container.status = "stopped"
                container.stopped_at = datetime.utcnow()
                await session.commit()
                await session.refresh(container)

                logger.info(f"Stopped container: {container.name}")

                return ContainerType(
                    id=container.id,
                    container_id=container.container_id,
                    name=container.name,
                    image=container.image,
                    tag=container.tag,
                    subdomain=container.subdomain,
                    internal_port=container.internal_port,
                    external_port=container.external_port,
                    environment_vars=container.environment_vars,
                    volumes=container.volumes,
                    command=container.command,
                    memory_limit=container.memory_limit,
                    cpu_limit=container.cpu_limit,
                    status=container.status,
                    restart_policy=container.restart_policy,
                    description=container.description,
                    labels=container.labels,
                    created_at=container.created_at,
                    updated_at=container.updated_at,
                    started_at=container.started_at,
                    stopped_at=container.stopped_at,
                    user_id=container.user_id,
                )
            except Exception as e:
                await session.rollback()
                logger.error(f"Error stopping container {id}: {e}")
                raise

    @strawberry.mutation
    async def restart_container(self, id: strawberry.ID) -> ContainerType:
        """Restart a container"""
        async for session in get_db():
            try:
                result = await session.execute(
                    select(Container).where(Container.id == int(id))
                )
                container = result.scalar_one_or_none()
                if not container or not container.container_id:
                    raise ValueError(f"Container {id} not found or has no container_id")

                # Restart in Docker
                await docker_manager.restart_container(container.container_id)

                # Update database
                container.status = "running"
                container.started_at = datetime.utcnow()
                container.stopped_at = None
                await session.commit()
                await session.refresh(container)

                logger.info(f"Restarted container: {container.name}")

                return ContainerType(
                    id=container.id,
                    container_id=container.container_id,
                    name=container.name,
                    image=container.image,
                    tag=container.tag,
                    subdomain=container.subdomain,
                    internal_port=container.internal_port,
                    external_port=container.external_port,
                    environment_vars=container.environment_vars,
                    volumes=container.volumes,
                    command=container.command,
                    memory_limit=container.memory_limit,
                    cpu_limit=container.cpu_limit,
                    status=container.status,
                    restart_policy=container.restart_policy,
                    description=container.description,
                    labels=container.labels,
                    created_at=container.created_at,
                    updated_at=container.updated_at,
                    started_at=container.started_at,
                    stopped_at=container.stopped_at,
                    user_id=container.user_id,
                )
            except Exception as e:
                await session.rollback()
                logger.error(f"Error restarting container {id}: {e}")
                raise
    
    @strawberry.mutation
    async def create_container_with_modpack(
        self,
        name: str,
        subdomain: str,
        source: str,
        modpack_id: str,
        version_id: str,
        memory_limit: Optional[str] = None,
        cpu_limit: Optional[str] = None
    ) -> ContainerType:
        """Create a container with a modpack pre-installed"""
        # TODO: Implement
        raise NotImplementedError("create_container_with_modpack not yet implemented")
