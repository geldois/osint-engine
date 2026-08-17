from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.application.auth.user import Role
from osint_engine.infrastructure.persistence.mem.default_pattern_sets import (
    DEFAULT_PATTERN_SETS,
)
from osint_engine.infrastructure.persistence.mem.mem_seeder import seed_mem_storage

if TYPE_CHECKING:
    from osint_engine.config.settings import Settings
    from osint_engine.infrastructure.hashers.argon2_password_hasher import (
        Argon2PasswordHasher,
    )
    from tests.conftest import MakeMemStorage


class TestMemSeederSeedingBehavior:
    def test_seeds_mem_storage_with_admin_user(
        self,
        make_mem_storage: MakeMemStorage,
        settings: Settings,
        argon2_password_hasher: Argon2PasswordHasher,
    ) -> None:
        mem_storage = make_mem_storage()

        admin = mem_storage.users.get("admin")

        assert admin is None

        seed_mem_storage(
            settings=settings,
            mem_storage=mem_storage,
            password_hasher=argon2_password_hasher,
        )

        admin = mem_storage.users.get("admin")

        assert admin is not None

        assert admin.role is Role.ADMIN

        assert admin.username == "admin"

    def test_seeds_mem_storage_with_the_default_pattern_sets(
        self,
        make_mem_storage: MakeMemStorage,
        settings: Settings,
        argon2_password_hasher: Argon2PasswordHasher,
    ) -> None:
        mem_storage = make_mem_storage()

        assert not mem_storage.pattern_sets

        seed_mem_storage(
            settings=settings,
            mem_storage=mem_storage,
            password_hasher=argon2_password_hasher,
        )

        assert mem_storage.pattern_sets == {
            pattern_set.id: pattern_set for pattern_set in DEFAULT_PATTERN_SETS
        }
