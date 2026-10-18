from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from osint_engine.application.auth.external_credential import ExternalCredential
    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.domain.entities.graphs import CompositeGraph


class LegalProcessFetcher(ABC):
    @abstractmethod
    async def fetch(
        self, *, cpf_or_cnpj: str, credential: ExternalCredential
    ) -> EntityRevision[CompositeGraph] | None:
        raise NotImplementedError
