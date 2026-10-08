from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.infrastructure.persistence.mem.default_pattern_sets import (
    DEFAULT_PATTERN_SETS,
)

if TYPE_CHECKING:
    from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage


def seed_mem_storage(*, mem_storage: MemStorage) -> None:
    for pattern_set in DEFAULT_PATTERN_SETS:
        mem_storage.pattern_sets[pattern_set.id] = pattern_set
