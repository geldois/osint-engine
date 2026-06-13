from __future__ import annotations

from abc import abstractmethod
from contextlib import AbstractAsyncContextManager
from typing import TYPE_CHECKING, Self, final

if TYPE_CHECKING:
    from types import TracebackType


class UoW(AbstractAsyncContextManager["UoW"]):
    @abstractmethod
    def __init__(self) -> None: ...

    @final
    async def __aenter__(self) -> Self:
        await self._prepare()

        return self

    @final
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
