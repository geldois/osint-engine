from __future__ import annotations

from osint_engine.application.contracts.repositories.entity_repository import (
    EntityRepository,
)
from osint_engine.domain.entities.bases.graph import Graph


class GraphRepository(EntityRepository[Graph]): ...
