from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from osint_engine.application.auth.external_credential import ExternalCredential
    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.domain.entities.bases.graph import Graph


class CPFFetcher(ABC):
    """Assumes the source treats an unknown CPF as a fetch failure (e.g. 404),
    not a 200 with an empty/absent body — unlike CEISFetcher/CNEPFetcher,
    which return `EntityRevision | None` for exactly that empty-result case."""

    @abstractmethod
    async def fetch(
        self, *, cpf: str, credential: ExternalCredential
    ) -> EntityRevision[Graph]:
        raise NotImplementedError
