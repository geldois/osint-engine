from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.application.contracts.uow import UoW
from osint_engine.infrastructure.errors.uow_error import (
    UoWAlreadyPreparedError,
    UoWNotPreparedError,
)
from osint_engine.infrastructure.persistence.mem.mem_uow import MemUoW
from osint_engine.infrastructure.persistence.pg.repositories.pg_external_credential_repository import (  # noqa: E501
    PgExternalCredentialRepository,
)

if TYPE_CHECKING:
    from asyncpg import Pool

    from osint_engine.application.revision.policies.revision_merge_policy import (
        RevisionMergePolicy,
    )
    from osint_engine.application.revision.policies.revision_selection_policy import (
        RevisionSelectionPolicy,
    )
    from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage


class HybridUoW(UoW):
    @override
    def __init__(
        self,
        *,
        mem_storage: MemStorage,
        pg_pool: Pool,
        encryption_key: str,
        revision_merge_policy: RevisionMergePolicy,
        revision_selection_policy: RevisionSelectionPolicy,
    ) -> None:
        self._pg_pool = pg_pool
        self._encryption_key = encryption_key
        self.revision_merge_policy = revision_merge_policy
        self.revision_selection_policy = revision_selection_policy
        self._mem_uow = MemUoW(
            mem_storage=mem_storage,
            revision_merge_policy=revision_merge_policy,
            revision_selection_policy=revision_selection_policy,
        )

    def _is_prepared(self) -> bool:
        return all(
            hasattr(self, attribute)
            for attribute in (
                "edges",
                "external_credentials",
                "graphs",
                "nodes",
                "pattern_sets",
                "users",
            )
        )

    @override
    async def _prepare(self) -> None:
        if self._is_prepared():
            raise UoWAlreadyPreparedError(subject=type(self))

        external_credentials = PgExternalCredentialRepository(
            pool=self._pg_pool, encryption_key=self._encryption_key
        )
        await self._mem_uow._prepare()  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]

        self.edges = self._mem_uow.edges
        self.external_credentials = external_credentials
        self.graphs = self._mem_uow.graphs
        self.nodes = self._mem_uow.nodes
        self.pattern_sets = self._mem_uow.pattern_sets
        self.users = self._mem_uow.users

    @override
    async def _finish(self) -> None:
        if not self._is_prepared():
            raise UoWNotPreparedError(subject=type(self))

        await self._mem_uow._finish()  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]

        del self.edges
        del self.external_credentials
        del self.graphs
        del self.nodes
        del self.pattern_sets
        del self.users

    @override
    async def commit(self) -> None:
        if not self._is_prepared():
            raise UoWNotPreparedError(subject=type(self))

        await self._mem_uow.commit()

    @override
    async def rollback(self) -> None:
        await self._mem_uow.rollback()
