from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from osint_engine.application.auth.user import Role, User
from osint_engine.config.settings import Settings
from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.infrastructure.hashers.argon2_password_hasher import (
    Argon2PasswordHasher,
)
from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage
from osint_engine.infrastructure.services.pyjwt_service import PyJWTService
from tests.fakes.domain import FakeEdge, FakeNode

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.domain.entities.bases.edge import Edge
    from osint_engine.domain.entities.bases.node import Node

type MakeFakeEdge = Callable[..., FakeEdge]
type MakeFakeNode = Callable[..., FakeNode]
type MakeGraph = Callable[..., Graph]
type MakeMemStorage = Callable[..., MemStorage]
type MakeUser = Callable[..., User]


@pytest.fixture(scope="session")
def argon2_password_hasher() -> Argon2PasswordHasher:
    """An Argon2id password hasher."""

    return Argon2PasswordHasher()


@pytest.fixture(scope="session")
def pyjwt_service(settings: Settings) -> PyJWTService:
    """A JWT service bound to the canonical test settings."""

    return PyJWTService(settings=settings)


@pytest.fixture(scope="session")
def settings() -> Settings:
    """The canonical application settings shared across the test dependency graph."""

    return Settings(
        access_token_expire_minutes=60,
        admin_password="admin_password",
        cors_origins=["http://localhost:3000"],
        debug=True,
        fetcher_connect_timeout=15,
        fetcher_read_timeout=30,
        host="127.0.0.1",
        log_level="info",
        port=8000,
        secret_key="a-secret-key-with-at-least-32-bytes-for-hs256",
    )


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
            edges={edge.id: edge for edge in edges} if edges is not None else {},
            graphs={graph.id: graph for graph in graphs} if graphs is not None else {},
            nodes={node.id: node for node in nodes} if nodes is not None else {},
            users={user.username: user for user in users} if users is not None else {},
        )

    return mem_storage


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
