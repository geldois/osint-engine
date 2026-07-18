from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.application.contracts.fetchers.cnpj_fetcher import CNPJFetcher

if TYPE_CHECKING:
    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.domain.entities.bases.graph import Graph


class FakeCNPJFetcher(CNPJFetcher):
    def __init__(self, *, revision: EntityRevision[Graph]) -> None:
        self.revision = revision

    @override
    async def fetch(self, *, cnpj: str) -> EntityRevision[Graph]:
        return self.revision
