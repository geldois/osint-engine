from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.application.contracts.uow import UoW
from osint_engine.infrastructure.errors.uow_error import (
    UoWAlreadyPreparedError,
    UoWNotPreparedError,
)
from osint_engine.infrastructure.persistence.mem.mem_storage import (
    MemStorage,
    MemStorageSnapshot,
)
from osint_engine.infrastructure.persistence.mem.repositories.mem_edge_repository import (  # noqa: E501
    MemEdgeRepository,
)
from osint_engine.infrastructure.persistence.mem.repositories.mem_external_credential_repository import (  # noqa: E501
    MemExternalCredentialRepository,
)
from osint_engine.infrastructure.persistence.mem.repositories.mem_graph_repository import (  # noqa: E501
    MemGraphRepository,
)
from osint_engine.infrastructure.persistence.mem.repositories.mem_node_repository import (  # noqa: E501
    MemNodeRepository,
)
from osint_engine.infrastructure.persistence.mem.repositories.mem_user_repository import (  # noqa: E501
    MemUserRepository,
)

if TYPE_CHECKING:
    from osint_engine.application.revision.policies.revision_merge_policy import (
        RevisionMergePolicy,
    )
    from osint_engine.application.revision.policies.revision_selection_policy import (
        RevisionSelectionPolicy,
    )


class MemUoW(UoW):
    @override
    def __init__(
        self,
        *,
        mem_storage: MemStorage,
        revision_merge_policy: RevisionMergePolicy,
        revision_selection_policy: RevisionSelectionPolicy,
    ) -> None:
        self._mem_storage = mem_storage
        self.revision_merge_policy = revision_merge_policy
        self.revision_selection_policy = revision_selection_policy

    def _is_prepared(self) -> bool:
        return all(
            hasattr(self, attribute)
            for attribute in (
                "_snapshot",
                "edges",
                "external_credentials",
                "graphs",
                "nodes",
                "users",
            )
        )

    @override
    async def _prepare(self) -> None:
        if self._is_prepared():
            raise UoWAlreadyPreparedError(subject=type(self))

        self._snapshot = MemStorageSnapshot(mem_storage=self._mem_storage)

        self.edges = MemEdgeRepository(
            mem_storage=self._snapshot,
            revision_merge_policy=self.revision_merge_policy,
            revision_selection_policy=self.revision_selection_policy,
        )
        self.external_credentials = MemExternalCredentialRepository(
            mem_storage=self._snapshot
        )
        self.graphs = MemGraphRepository(
            mem_storage=self._snapshot,
            revision_merge_policy=self.revision_merge_policy,
            revision_selection_policy=self.revision_selection_policy,
        )
        self.nodes = MemNodeRepository(
            mem_storage=self._snapshot,
            revision_merge_policy=self.revision_merge_policy,
            revision_selection_policy=self.revision_selection_policy,
        )
        self.users = MemUserRepository(mem_storage=self._snapshot)

    @override
    async def _finish(self) -> None:
        if not self._is_prepared():
            raise UoWNotPreparedError(subject=type(self))

        self._snapshot.clear_snapshot()

        del self._snapshot

        del self.edges

        del self.external_credentials

        del self.graphs

        del self.nodes

        del self.users

    @override
    async def commit(self) -> None:
        if not self._is_prepared():
            raise UoWNotPreparedError(subject=type(self))

        self._snapshot.commit_to_storage()

    @override
    async def rollback(self) -> None:
        """
        All operations against an isolated snapshot; rollback is implicit.
        """
