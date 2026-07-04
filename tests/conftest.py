from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import pytest

from osint_engine.application.auth.user import Role, User
from osint_engine.config.settings import Settings
from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.infrastructure.hashers.password_hasher import PasswordHasher
from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage
from tests.fakes import FakeEdge, FakeEntity, FakeNode

if TYPE_CHECKING:
    from osint_engine.domain.entities.bases.edge import Edge
    from osint_engine.domain.entities.bases.node import Node

type MakeEdge = Callable[..., FakeEdge]
type MakeEntity = Callable[..., FakeEntity]
type MakeGraph = Callable[..., Graph]
type MakeMemStorage = Callable[..., MemStorage]
type MakeNode = Callable[..., FakeNode]
type MakeUser = Callable[..., User]


@pytest.fixture
def make_edge() -> MakeEdge:
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
def make_entity() -> MakeEntity:
    """
    *,
    content: str | None = None
    """

    def entity(*, content: str | None = None) -> FakeEntity:
        return FakeEntity(content=content if content is not None else str(uuid4()))

    return entity


@pytest.fixture
def make_graph(make_edge: MakeEdge, make_node: MakeNode) -> MakeGraph:
    """
    *,
    edges: list[Edge[UUID]] | None = None,
    nodes: list[Node[UUID]] | None = None,
    root_id: UUID | None = None
    """

    def graph(
        *,
        edges: list[Edge[UUID]] | None = None,
        nodes: list[Node[UUID]] | None = None,
        root_id: UUID | None = None,
    ) -> Graph:
        edge = make_edge()
        node = make_node()

        return Graph(
            edges=frozenset(edges) if edges is not None else frozenset({edge}),
            nodes=frozenset(nodes) if nodes is not None else frozenset({node}),
            root_id=root_id if root_id is not None else node.id,
        )

    return graph


@pytest.fixture
def make_mem_storage() -> MakeMemStorage:
    """
    *,
    edges: list[Edge[UUID]] | None = None,
    graphs: list[Graph] | None = None,
    nodes: list[Node[UUID]] | None = None,
    users: list[User] | None = None
    """

    def mem_storage(
        *,
        edges: list[Edge[UUID]] | None = None,
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
def make_node() -> MakeNode:
    """
    *,
    content: str | None = None
    """

    def node(*, content: str | None = None) -> FakeNode:
        return FakeNode(content=content if content is not None else str(uuid4()))

    return node


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
def password_hasher() -> PasswordHasher:
    return PasswordHasher()


@pytest.fixture(scope="session")
def settings() -> Settings:
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
