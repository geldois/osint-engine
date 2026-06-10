from __future__ import annotations

from abc import abstractmethod
from contextlib import AbstractAsyncContextManager
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from types import TracebackType

    from osint_engine.application.contracts.repositories.edge_repository import (
        EdgeRepository,
    )
    from osint_engine.application.contracts.repositories.graph_repository import (
        GraphRepository,
    )
    from osint_engine.application.contracts.repositories.node_repository import (
        NodeRepository,
    )


class UoW(AbstractAsyncContextManager["UoW"]):
    @abstractmethod
    def __init__(
        self,
        *,
        edge_repo: EdgeRepository,
        graph_repo: GraphRepository,
        node_repo: NodeRepository,
    ) -> None:
        self.edge_repo = edge_repo
        self.graph_repo = graph_repo
        self.node_repo = node_repo

    async def __aenter__(self) -> Self:
        await self._prepare()

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
        /,
    ) -> None:
        if exc_type is None:
            await self.commit()
            await self._finish()

            return

        await self.rollback()
        await self._finish()

    @abstractmethod
    async def _prepare(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def _finish(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError
