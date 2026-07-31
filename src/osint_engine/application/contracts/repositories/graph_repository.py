from __future__ import annotations

from osint_engine.application.contracts.repositories.entity_repository import (
    EntityRepository,
)
from osint_engine.domain.entities.bases.graph import Graph


class GraphRepository(EntityRepository[Graph]):
    """
    `merge`/`merge_many` must also cascade-merge every node and edge the
    graph carries into their own `NodeRepository`/`EdgeRepository`, so they
    stay individually addressable by id — never only reachable as part of
    the graph's own opaque blob. Every implementation of this contract must
    uphold this, not just the current in-memory one.
    """
