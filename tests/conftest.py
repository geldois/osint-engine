from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Protocol
from uuid import UUID, uuid4

import pytest

from osint_engine.application.auth.user import Role, User
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.application.revision.policies.revision_merge_policy import (
    merge_by_filled_fields_policy,
)
from osint_engine.application.revision.policies.revision_selection_policy import (
    select_current_by_newest_fetched,
)
from osint_engine.config.container import Policies
from osint_engine.config.settings import Settings
from osint_engine.domain.entities.bases.entity import Entity
from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.infrastructure.hashers.argon2_password_hasher import (
    Argon2PasswordHasher,
)
from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage
from osint_engine.infrastructure.persistence.mem.mem_uow import MemUoW
from osint_engine.infrastructure.services.pyjwt_service import PyJWTService
from tests.fakes.domain import FakeEdge, FakeMergeableNode, FakeNode

if TYPE_CHECKING:
    from osint_engine.application.revision.policies.revision_merge_policy import (
        RevisionMergePolicy,
    )
    from osint_engine.application.revision.policies.revision_selection_policy import (
        RevisionSelectionPolicy,
    )
    from osint_engine.domain.entities.bases.edge import Edge
    from osint_engine.domain.entities.bases.node import Node


class MakeEntityRevision(Protocol):
    def __call__[Entity_: Entity[UUID]](
        self,
        *,
        entity: Entity_,
        fetched_at: datetime | None = None,
        merged_at: datetime | None = None,
    ) -> EntityRevision[Entity_]: ...


type MakeFakeEdge = Callable[..., FakeEdge]
type MakeFakeNode = Callable[..., FakeNode]
type MakeFakeMergeableNode = Callable[..., FakeMergeableNode]
type MakeGraph = Callable[..., Graph]
type MakeMemStorage = Callable[..., MemStorage]
type MakeMemUoW = Callable[..., MemUoW]
type MakePolicies = Callable[..., Policies]
type MakeUser = Callable[..., User]


def _entity_store[Entity_: Entity[UUID]](
    revisions: Iterable[EntityRevision[Entity_]] | None,
) -> defaultdict[UUID, dict[UUID, EntityRevision[Entity_]]] | None:
    if revisions is None:
        return None

    store: defaultdict[UUID, dict[UUID, EntityRevision[Entity_]]] = defaultdict(dict)

    for revision in revisions:
        store[revision.entity.id][revision.entity.content_id] = revision

    return store


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
def make_entity_revision() -> MakeEntityRevision:
    datetime_ = datetime(year=2026, month=1, day=1, tzinfo=UTC)

    def entity_revision[Entity_: Entity[UUID]](
        *,
        entity: Entity_,
        fetched_at: datetime | None = None,
        merged_at: datetime | None = None,
    ) -> EntityRevision[Entity_]:
        return EntityRevision(
            entity=entity,
            fetched_at=fetched_at if fetched_at is not None else datetime_,
            merged_at=merged_at,
        )

    return entity_revision


@pytest.fixture
def make_fake_edge() -> MakeFakeEdge:
    """
    *,
    source_id: UUID | None = None,
    target_id: UUID | None = None,
    content: str | None = None
    """

    def fake_edge(
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

    return fake_edge


@pytest.fixture
def make_fake_node() -> MakeFakeNode:
    """
    *,
    content: str | None = None
    """

    def fake_node(*, content: str | None = None) -> FakeNode:
        return FakeNode(content=content if content is not None else str(uuid4()))

    return fake_node


@pytest.fixture
def make_fake_mergeable_node() -> MakeFakeMergeableNode:
    """
    *,
    key: str | None = None,
    label: str | None = None
    """

    def fake_mergeable_node(
        *, key: str | None = None, label: str | None = None
    ) -> FakeMergeableNode:
        return FakeMergeableNode(
            key=key if key is not None else str(uuid4()), label=label
        )

    return fake_mergeable_node


@pytest.fixture
def make_graph(make_fake_edge: MakeFakeEdge, make_fake_node: MakeFakeNode) -> MakeGraph:
    """
    *,
    edges: Iterable[Edge[UUID, UUID, UUID]] | None = None,
    nodes: Iterable[Node[UUID]] | None = None,
    root_id: UUID | None = None
    """

    def graph(
        *,
        edges: Iterable[Edge[UUID, UUID, UUID]] | None = None,
        nodes: Iterable[Node[UUID]] | None = None,
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
    edges: Iterable[EntityRevision[Edge[UUID, UUID, UUID]]] | None = None,
    graphs: Iterable[EntityRevision[Graph]] | None = None,
    nodes: Iterable[EntityRevision[Node[UUID]]] | None = None,
    users: Iterable[User] | None = None
    """

    def mem_storage(
        *,
        edges: Iterable[EntityRevision[Edge[UUID, UUID, UUID]]] | None = None,
        graphs: Iterable[EntityRevision[Graph]] | None = None,
        nodes: Iterable[EntityRevision[Node[UUID]]] | None = None,
        users: Iterable[User] | None = None,
    ) -> MemStorage:
        return MemStorage(
            edges=_entity_store(edges),
            graphs=_entity_store(graphs),
            nodes=_entity_store(nodes),
            users={user.username: user for user in users}
            if users is not None
            else None,
        )

    return mem_storage


@pytest.fixture
def make_mem_uow(make_mem_storage: MakeMemStorage, policies: Policies) -> MakeMemUoW:
    """
    *,
    mem_storage: MemStorage | None = None,
    policies: Policies | None = None
    """

    default_policies = policies

    def mem_uow(
        *, mem_storage: MemStorage | None = None, policies: Policies | None = None
    ) -> MemUoW:
        storage = mem_storage if mem_storage is not None else make_mem_storage()
        resolved = policies if policies is not None else default_policies

        return MemUoW(
            mem_storage=storage,
            revision_merge_policy=resolved.revision_merge_policy,
            revision_selection_policy=resolved.revision_selection_policy,
        )

    return mem_uow


@pytest.fixture
def make_policies() -> MakePolicies:
    """
    *,
    revision_merge_policy: RevisionMergePolicy,
    revision_selection_policy: RevisionSelectionPolicy
    """

    def policies(
        *,
        revision_merge_policy: RevisionMergePolicy,
        revision_selection_policy: RevisionSelectionPolicy,
    ) -> Policies:
        return Policies(
            revision_merge_policy=revision_merge_policy,
            revision_selection_policy=revision_selection_policy,
        )

    return policies


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
def policies(make_policies: MakePolicies) -> Policies:
    """
    Canonical revision policies: merge by filled fields and select by newest fetched.
    """

    return make_policies(
        revision_merge_policy=merge_by_filled_fields_policy,
        revision_selection_policy=select_current_by_newest_fetched,
    )
