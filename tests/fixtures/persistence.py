from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, cast
from uuid import UUID

import pytest

from osint_engine.domain.entities.bases.entity import Entity
from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage
from osint_engine.infrastructure.persistence.mem.mem_uow import MemUoW
from tests.fakes.persistence import FakePgPool

if TYPE_CHECKING:
    from asyncpg import Pool

    from osint_engine.application.auth.external_credential import ExternalCredential
    from osint_engine.application.consumption.entity_record import EntityRecord
    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.config.container import Policies
    from osint_engine.domain.entities.bases.edge import Edge
    from osint_engine.domain.entities.bases.graph import Graph
    from osint_engine.domain.entities.bases.node import Node
    from osint_engine.domain.value_objects.text_pattern import TextPatternSet

type MakeMemStorage = Callable[..., MemStorage]
type MakeMemUoW = Callable[..., MemUoW]


def _entity_store[Entity_: Entity[UUID]](
    revisions: Iterable[EntityRevision[Entity_]] | None,
) -> defaultdict[UUID, dict[UUID, EntityRevision[Entity_]]] | None:
    if revisions is None:
        return None

    store: defaultdict[UUID, dict[UUID, EntityRevision[Entity_]]] = defaultdict(dict)

    for revision in revisions:
        store[revision.entity.id][revision.entity.content_id] = revision

    return store


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
        graphs: Iterable[EntityRevision[Graph]] | None = None,
        nodes: Iterable[EntityRevision[Node[UUID]]] | None = None,
        pattern_sets: Iterable[TextPatternSet] | None = None,
    ) -> MemStorage:
        return MemStorage(
            edges=_entity_store(edges),
            entity_records=list(entity_records) if entity_records is not None else None,
            external_credentials={
                (credential.username, credential.provider): credential
                for credential in external_credentials
            }
            if external_credentials is not None
            else None,
            graphs=_entity_store(graphs),
            nodes=_entity_store(nodes),
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
