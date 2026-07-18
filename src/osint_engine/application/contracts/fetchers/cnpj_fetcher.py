from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.domain.entities.bases.graph import Graph


class CNPJFetcher(ABC):
    @abstractmethod
    async def fetch(self, *, cnpj: str) -> EntityRevision[Graph]:
        raise NotImplementedError
