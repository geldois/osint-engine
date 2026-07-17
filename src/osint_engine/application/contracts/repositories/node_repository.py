from __future__ import annotations

from uuid import UUID

from osint_engine.application.contracts.repositories.entity_repository import (
    EntityRepository,
)
from osint_engine.domain.entities.bases.node import Node


class NodeRepository(EntityRepository[Node[UUID]]): ...
