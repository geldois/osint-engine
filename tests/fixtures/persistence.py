from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, NamedTuple, cast
from uuid import UUID

import pytest

from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.domain.entities.bases.entity import Entity
from osint_engine.infrastructure.persistence.hybrid_uow import HybridUoW
from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage
from osint_engine.infrastructure.persistence.mem.mem_uow import MemUoW
from osint_engine.infrastructure.persistence.mem.repositories.mem_edge_repository import (  # noqa: E501
    MemEdgeRepository,
)
from osint_engine.infrastructure.persistence.mem.repositories.mem_entity_record_repository import (  # noqa: E501
    MemEntityRecordRepository,
)
from osint_engine.infrastructure.persistence.mem.repositories.mem_graph_repository import (  # noqa: E501
    MemGraphRepository,
)
from osint_engine.infrastructure.persistence.mem.repositories.mem_node_repository import (  # noqa: E501
    MemNodeRepository,
)
from tests.fakes.persistence import FakePgPool

if TYPE_CHECKING:
    from asyncpg import Pool

    from osint_engine.application.auth.external_credential import ExternalCredential
    from osint_engine.application.consumption.entity_record import EntityRecord
    from osint_engine.config.container import Policies
    from osint_engine.config.settings import Settings
    from osint_engine.domain.entities.bases.edge import Edge
    from osint_engine.domain.entities.bases.node import Node
    from osint_engine.domain.entities.graphs import CompositeGraph
    from osint_engine.domain.value_objects.text_pattern import TextPatternSet

type MakeHybridUoWFactory = Callable[[], Callable[[], HybridUoW]]
type MakeMemEdgeRepository = Callable[..., MemEdgeRepository]
type MakeMemEntityRecordRepository = Callable[..., MemEntityRecordRepository]
type MakeMemGraphRepository = Callable[..., MemGraphRepository]
type MakeMemNodeRepository = Callable[..., MemNodeRepository]
type MakeMemStorage = Callable[..., MemStorage]
type MakeMemUoW = Callable[..., MemUoW]
type MakeMemUoWFactory = Callable[..., MakeMemUoW]


def _entity_store[Entity_: Entity[UUID]](
    revisions: Iterable[EntityRevision[Entity_]] | None,
) -> defaultdict[UUID, dict[UUID, EntityRevision[Entity_]]] | None:
    if revisions is None:
        return None

    store: defaultdict[UUID, dict[UUID, EntityRevision[Entity_]]] = defaultdict(dict)

    for revision in revisions:
        store[revision.entity.id][revision.entity.content_id] = revision

    return store


class _GraphMembers(NamedTuple):
    edges: list[EntityRevision[Edge[UUID, UUID, UUID]]]
    nodes: list[EntityRevision[Node[UUID]]]


def _graph_members(
    graph_revisions: Iterable[EntityRevision[CompositeGraph]] | None,
) -> _GraphMembers:
    members = _GraphMembers(edges=[], nodes=[])

    for revision in graph_revisions or ():
        members.edges.extend(
            EntityRevision(
                entity=edge,
                fetched_at=revision.fetched_at,
                merged_at=revision.merged_at,
                provider=revision.provider,
            )
            for edge in revision.entity.edges
        )
        members.nodes.extend(
            EntityRevision(
                entity=node,
                fetched_at=revision.fetched_at,
                merged_at=revision.merged_at,
                provider=revision.provider,
            )
            for node in revision.entity.nodes
        )

    return members


@pytest.fixture
def fake_pg_pool() -> FakePgPool:
    return FakePgPool()


@pytest.fixture
def pg_pool(fake_pg_pool: FakePgPool) -> Pool:
    return cast("Pool", fake_pg_pool)


@pytest.fixture
def make_mem_storage() -> MakeMemStorage:

    def mem_storage(
        *,
        edges: Iterable[EntityRevision[Edge[UUID, UUID, UUID]]] | None = None,
        entity_records: Iterable[EntityRecord] | None = None,
        external_credentials: Iterable[ExternalCredential] | None = None,
        graphs: Iterable[EntityRevision[CompositeGraph]] | None = None,
        nodes: Iterable[EntityRevision[Node[UUID]]] | None = None,
        pattern_sets: Iterable[TextPatternSet] | None = None,
    ) -> MemStorage:
        graph_revisions = tuple(graphs) if graphs is not None else None
        members = _graph_members(graph_revisions)

        return MemStorage(
            edges=_entity_store(
                [*(edges or ()), *members.edges]
                if edges is not None or graph_revisions is not None
                else None
            ),
            entity_records=list(entity_records) if entity_records is not None else None,
            external_credentials={
                (credential.username, credential.provider): credential
                for credential in external_credentials
            }
            if external_credentials is not None
            else None,
            graphs=_entity_store(
                [
                    EntityRevision(
                        entity=revision.entity.flatten(),
                        fetched_at=revision.fetched_at,
                        merged_at=revision.merged_at,
                        provider=revision.provider,
                    )
                    for revision in graph_revisions
                ]
                if graph_revisions is not None
                else None
            ),
            nodes=_entity_store(
                [*(nodes or ()), *members.nodes]
                if nodes is not None or graph_revisions is not None
                else None
            ),
            pattern_sets={pattern_set.id: pattern_set for pattern_set in pattern_sets}
            if pattern_sets is not None
            else None,
        )

    return mem_storage


@pytest.fixture
def make_mem_uow(make_mem_storage: MakeMemStorage, policies: Policies) -> MakeMemUoW:

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
def make_hybrid_uow_factory(
    fake_pg_pool: FakePgPool,
    make_mem_storage: MakeMemStorage,
    policies: Policies,
    settings: Settings,
) -> MakeHybridUoWFactory:

    def hybrid_uow_factory() -> Callable[[], HybridUoW]:
        mem_storage = make_mem_storage()

        return lambda: HybridUoW(
            mem_storage=mem_storage,
            pg_pool=cast("Pool", fake_pg_pool),
            encryption_key=settings.external_credential_encryption_key,
            revision_merge_policy=policies.revision_merge_policy,
            revision_selection_policy=policies.revision_selection_policy,
        )

    return hybrid_uow_factory


@pytest.fixture
def make_mem_uow_factory(make_mem_uow: MakeMemUoW) -> MakeMemUoWFactory:

    def mem_uow_factory(mem_uow: MemUoW | None = None) -> MakeMemUoW:
        mem_uow = mem_uow if mem_uow is not None else make_mem_uow()

        return lambda: mem_uow

    return mem_uow_factory


@pytest.fixture
def make_mem_node_repository(policies: Policies) -> MakeMemNodeRepository:

    def mem_node_repository(
        *, mem_storage: MemStorage, policies_override: Policies | None = None
    ) -> MemNodeRepository:
        resolved = policies_override if policies_override is not None else policies

        return MemNodeRepository(
            mem_storage=mem_storage,
            revision_merge_policy=resolved.revision_merge_policy,
            revision_selection_policy=resolved.revision_selection_policy,
        )

    return mem_node_repository


@pytest.fixture
def make_mem_edge_repository(policies: Policies) -> MakeMemEdgeRepository:

    def mem_edge_repository(
        *, mem_storage: MemStorage, policies_override: Policies | None = None
    ) -> MemEdgeRepository:
        resolved = policies_override if policies_override is not None else policies

        return MemEdgeRepository(
            mem_storage=mem_storage,
            revision_merge_policy=resolved.revision_merge_policy,
            revision_selection_policy=resolved.revision_selection_policy,
        )

    return mem_edge_repository


@pytest.fixture
def make_mem_entity_record_repository() -> MakeMemEntityRecordRepository:

    def mem_entity_record_repository(
        *, mem_storage: MemStorage
    ) -> MemEntityRecordRepository:
        return MemEntityRecordRepository(mem_storage=mem_storage)

    return mem_entity_record_repository


@pytest.fixture
def make_mem_graph_repository(policies: Policies) -> MakeMemGraphRepository:

    def mem_graph_repository(
        *, mem_storage: MemStorage, policies_override: Policies | None = None
    ) -> MemGraphRepository:
        resolved = policies_override if policies_override is not None else policies

        return MemGraphRepository(
            mem_storage=mem_storage,
            revision_merge_policy=resolved.revision_merge_policy,
            revision_selection_policy=resolved.revision_selection_policy,
            node_repository=MemNodeRepository(
                mem_storage=mem_storage,
                revision_merge_policy=resolved.revision_merge_policy,
                revision_selection_policy=resolved.revision_selection_policy,
            ),
            edge_repository=MemEdgeRepository(
                mem_storage=mem_storage,
                revision_merge_policy=resolved.revision_merge_policy,
                revision_selection_policy=resolved.revision_selection_policy,
            ),
        )

    return mem_graph_repository
