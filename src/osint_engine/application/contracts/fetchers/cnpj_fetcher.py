from abc import ABC, abstractmethod

from osint_engine.domain.value_objects.graph import Graph


class CNPJFetcher(ABC):
    @abstractmethod
    async def fetch(self, cnpj: str, /) -> Graph: ...
