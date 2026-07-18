from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from osint_engine.application.auth.external_credential import (
        ExternalCredential,
        Provider,
    )


class ExternalCredentialRepository(ABC):
    @abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def find(
        self, *, username: str, provider: Provider
    ) -> ExternalCredential | None:
        raise NotImplementedError

    @abstractmethod
    async def save(self, *, credential: ExternalCredential) -> None:
        raise NotImplementedError
