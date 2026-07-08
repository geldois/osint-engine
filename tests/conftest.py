from __future__ import annotations

import json
from collections.abc import AsyncGenerator, Callable
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from httpx2 import ASGITransport, AsyncClient, Timeout

from osint_engine.application.auth.user import Role, User
from osint_engine.config.croot import build_container
from osint_engine.config.settings import Settings
from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.infrastructure.hashers.argon2_password_hasher import (
    Argon2PasswordHasher,
)
from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage
from osint_engine.infrastructure.persistence.mem.mem_uow import MemUoW
from osint_engine.infrastructure.sources.payload import Payload
from osint_engine.interface.http.fastapi.fastapi import build_fastapi_app
from tests.fakes import FakeCNPJFetcher, FakeEdge, FakeEntity, FakeNode

if TYPE_CHECKING:
    from fastapi import FastAPI

    from osint_engine.config.container import Container
    from osint_engine.domain.entities.bases.edge import Edge
    from osint_engine.domain.entities.bases.node import Node

type MakeFakeCNPJFetcher = Callable[..., FakeCNPJFetcher]
type MakeFakeEdge = Callable[..., FakeEdge]
type MakeFakeEntity = Callable[..., FakeEntity]
type MakeFakeNode = Callable[..., FakeNode]
type MakeGraph = Callable[..., Graph]
type MakeMemStorage = Callable[..., MemStorage]
type MakeMemUoW = Callable[..., MemUoW]
type MakeMemUoWFactory = Callable[..., MakeMemUoW]
type MakePayload = Callable[..., Payload]
type MakeUser = Callable[..., User]


@pytest.fixture
def container(settings: Settings, http_client: AsyncClient) -> Container:
    """ """

    return build_container(settings=settings, http_client=http_client)


@pytest.fixture
def fastapi_app(container: Container) -> FastAPI:
    """ """

    return build_fastapi_app(container=container)


@pytest_asyncio.fixture(loop_scope="session")
async def fastapi_test_client(
    fastapi_app: FastAPI,
) -> AsyncGenerator[AsyncClient, None]:
    """ """

    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as fastapi_test_client:
        yield fastapi_test_client


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def http_client(
    http_client_timeout: Timeout,
) -> AsyncGenerator[AsyncClient, None]:
    """ """

    async with AsyncClient(timeout=http_client_timeout) as http_client:
        yield http_client


@pytest.fixture(scope="session")
def http_client_timeout(settings: Settings) -> Timeout:
    """ """

    return Timeout(
        timeout=None,
        connect=settings.fetcher_connect_timeout,
        read=settings.fetcher_read_timeout,
    )


@pytest.fixture
def make_fake_cnpj_fetcher(make_graph: MakeGraph) -> MakeFakeCNPJFetcher:
    """
    *,
    graph: Graph | None = None
    """

    def fake_cnpj_fetcher(*, graph: Graph | None = None) -> FakeCNPJFetcher:
        return FakeCNPJFetcher(graph=graph if graph is not None else make_graph())

    return fake_cnpj_fetcher


@pytest.fixture
def make_fake_edge() -> MakeFakeEdge:
    """
    *,
    source_id: UUID | None = None,
    target_id: UUID | None = None,
    content: str | None = None
    """

    def edge(
        *,
        source_id: UUID | None = None,
        target_id: UUID | None = None,
        content: str | None = None,
    ) -> FakeEdge:
        return FakeEdge(
            source_id=source_id if source_id is not None else uuid4(),
            target_id=target_id if target_id is not None else uuid4(),
            content=content if content is not None else str(uuid4()),
        )

    return edge


@pytest.fixture
def make_fake_entity() -> MakeFakeEntity:
    """
    *,
    content: str | None = None
    """

    def entity(*, content: str | None = None) -> FakeEntity:
        return FakeEntity(content=content if content is not None else str(uuid4()))

    return entity


@pytest.fixture
def make_fake_node() -> MakeFakeNode:
    """
    *,
    content: str | None = None
    """

    def node(*, content: str | None = None) -> FakeNode:
        return FakeNode(content=content if content is not None else str(uuid4()))

    return node


@pytest.fixture
def make_graph(make_fake_edge: MakeFakeEdge, make_fake_node: MakeFakeNode) -> MakeGraph:
    """
    *,
    edges: list[Edge[UUID, UUID, UUID]] | None = None,
    nodes: list[Node[UUID]] | None = None,
    root_id: UUID | None = None
    """

    def graph(
        *,
        edges: list[Edge[UUID, UUID, UUID]] | None = None,
        nodes: list[Node[UUID]] | None = None,
        root_id: UUID | None = None,
    ) -> Graph:
        node_a = make_fake_node()
        node_b = make_fake_node()
        edge = make_fake_edge(source_id=node_a.id, target_id=node_b.id)

        return Graph(
            edges=frozenset(edges) if edges is not None else frozenset({edge}),
            nodes=frozenset(nodes)
            if nodes is not None
            else frozenset({node_a, node_b}),
            root_id=root_id if root_id is not None else node_a.id,
        )

    return graph


@pytest.fixture
def make_mem_storage() -> MakeMemStorage:
    """
    *,
    edges: list[Edge[UUID, UUID, UUID]] | None = None,
    graphs: list[Graph] | None = None,
    nodes: list[Node[UUID]] | None = None,
    users: list[User] | None = None
    """

    def mem_storage(
        *,
        edges: list[Edge[UUID, UUID, UUID]] | None = None,
        graphs: list[Graph] | None = None,
        nodes: list[Node[UUID]] | None = None,
        users: list[User] | None = None,
    ) -> MemStorage:
        return MemStorage(
            edges={e.id: e for e in edges} if edges is not None else {},
            graphs={g.id: g for g in graphs} if graphs is not None else {},
            nodes={n.id: n for n in nodes} if nodes is not None else {},
            users={u.username: u for u in users} if users is not None else {},
        )

    return mem_storage


@pytest.fixture
def make_mem_uow(make_mem_storage: MakeMemStorage) -> MakeMemUoW:
    """
    *,
    mem_storage: MemStorage | None = None
    """

    def mem_uow(*, mem_storage: MemStorage | None = None) -> MemUoW:
        storage = mem_storage if mem_storage is not None else make_mem_storage()

        return MemUoW(mem_storage=storage)

    return mem_uow


@pytest.fixture
def make_mem_uow_factory(make_mem_uow: MakeMemUoW) -> MakeMemUoWFactory:
    """
    *,
    mem_uow: MemUoW | None = None
    """

    def mem_uow_factory(mem_uow: MemUoW | None = None) -> MakeMemUoW:
        mem_uow = mem_uow if mem_uow is not None else make_mem_uow()

        return lambda: mem_uow

    return mem_uow_factory


@pytest.fixture
def make_payload() -> MakePayload:
    """
    *,
    source: str,
    data: dict[str, object] | Path
    """

    def payload(*, source: str, data: dict[str, object] | Path) -> Payload:
        if isinstance(data, Path):
            with Path.open(data) as file:
                data_: dict[str, object] = json.load(file)

                return Payload(source=source, data=data_)

        return Payload(source=source, data=data)

    return payload


@pytest.fixture
def make_user() -> MakeUser:
    """
    *,
    username: str | None = None,
    hashed_password: str | None = None,
    role: Role = Role.VIEWER
    """

    def user(
        *,
        username: str | None = None,
        hashed_password: str | None = None,
        role: Role = Role.VIEWER,
    ) -> User:
        return User(
            username=username if username is not None else str(uuid4()),
            hashed_password=hashed_password
            if hashed_password is not None
            else str(uuid4()),
            role=role,
        )

    return user


@pytest.fixture
def password_hasher() -> Argon2PasswordHasher:
    """ """

    return Argon2PasswordHasher()


@pytest.fixture(scope="session")
def settings() -> Settings:
    """ """

    return Settings(
        access_token_expire_minutes=60,
        admin_password="admin_password",  # noqa: S106
        cors_origins=["http://localhost:3000"],
        debug=True,
        fetcher_connect_timeout=15,
        fetcher_read_timeout=30,
        host="127.0.0.1",
        log_level="info",
        port=8000,
        secret_key="secret_key",  # noqa: S106
    )
