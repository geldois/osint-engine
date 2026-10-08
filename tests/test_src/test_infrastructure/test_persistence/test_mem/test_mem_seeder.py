from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.infrastructure.persistence.mem.default_pattern_sets import (
    DEFAULT_PATTERN_SETS,
)
from osint_engine.infrastructure.persistence.mem.mem_seeder import seed_mem_storage

if TYPE_CHECKING:
    from tests.conftest import MakeMemStorage


class TestMemSeederSeedingBehavior:
    def test_seeds_no_user_of_any_kind(self, make_mem_storage: MakeMemStorage) -> None:
        mem_storage = make_mem_storage()

        seed_mem_storage(mem_storage=mem_storage)

        assert not mem_storage.users

    def test_seeds_mem_storage_with_the_default_pattern_sets(
        self, make_mem_storage: MakeMemStorage
    ) -> None:
        mem_storage = make_mem_storage()

        assert not mem_storage.pattern_sets

        seed_mem_storage(mem_storage=mem_storage)

        assert mem_storage.pattern_sets == {
            pattern_set.id: pattern_set for pattern_set in DEFAULT_PATTERN_SETS
        }
