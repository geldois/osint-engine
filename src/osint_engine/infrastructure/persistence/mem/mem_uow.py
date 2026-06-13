from __future__ import annotations

from typing import override

from osint_engine.application.contracts.uow import UoW
from osint_engine.infrastructure.errors.uow_error import (
    AlreadyPreparedUoWError,
    NotPreparedUoWError,
)
from osint_engine.infrastructure.persistence.mem.mem_storage import (
    MemStorage,
    MemStorageSnapshot,
)
from osint_engine.infrastructure.persistence.mem.repositories.mem_edge_repository import (  # noqa: E501
    MemEdgeRepository,
)
from osint_engine.infrastructure.persistence.mem.repositories.mem_graph_repository import (  # noqa: E501
    MemGraphRepository,
)
from osint_engine.infrastructure.persistence.mem.repositories.mem_node_repository import (  # noqa: E501
    MemNodeRepository,
)


class MemUoW(UoW):
    @override
    def __init__(self, *, mem_storage: MemStorage) -> None:
        self._mem_storage = mem_storage

    def _is_prepared(self) -> bool:
        return all(
            hasattr(self, attribute)
            for attribute in ("_snapshot", "edges", "graphs", "nodes")
        )

    @override
    async def _prepare(self) -> None:
        if self._is_prepared():
            raise AlreadyPreparedUoWError(subject=type(self))

        self._snapshot = MemStorageSnapshot(mem_storage=self._mem_storage)

        self.edges = MemEdgeRepository(mem_storage=self._snapshot)
        self.graphs = MemGraphRepository(mem_storage=self._snapshot)
        self.nodes = MemNodeRepository(mem_storage=self._snapshot)

    @override
    async def _finish(self) -> None:
        if not self._is_prepared():
            raise NotPreparedUoWError(subject=type(self))

        self._snapshot.clear_snapshot()

        del self._snapshot

        del self.edges

        del self.graphs

        del self.nodes

    @override
    async def commit(self) -> None:
        if not self._is_prepared():
            raise NotPreparedUoWError(subject=type(self))

        self._snapshot.commit_to_storage()

    @override
    async def rollback(self) -> None:
        pass
