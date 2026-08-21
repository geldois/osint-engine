from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from osint_engine.application.auth.external_credential import ExternalCredential


class KipFlowRateLimiter(ABC):
    @abstractmethod
    async def acquire(self, *, credential: ExternalCredential) -> None:
        raise NotImplementedError

    @abstractmethod
    async def wait_seconds_for(
        self, *, credential: ExternalCredential, count: int
    ) -> int:
        raise NotImplementedError
