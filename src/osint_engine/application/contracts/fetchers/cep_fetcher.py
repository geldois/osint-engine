from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.domain.entities.nodes.address import Address


class CEPFetcher(ABC):
    @abstractmethod
    async def fetch(self, *, cep: str, number: str) -> EntityRevision[Address]:
        raise NotImplementedError
