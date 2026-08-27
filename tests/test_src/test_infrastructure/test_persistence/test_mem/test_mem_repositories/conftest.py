from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import pytest

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

if TYPE_CHECKING:
    from osint_engine.config.container import Policies
    from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage


type MakeMemNodeRepository = Callable[..., MemNodeRepository]
type MakeMemEdgeRepository = Callable[..., MemEdgeRepository]
type MakeMemEntityRecordRepository = Callable[..., MemEntityRecordRepository]
type MakeMemGraphRepository = Callable[..., MemGraphRepository]


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
