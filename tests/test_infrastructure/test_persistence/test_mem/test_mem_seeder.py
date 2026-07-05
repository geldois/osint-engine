from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.application.auth.user import Role
from osint_engine.infrastructure.persistence.mem.mem_seeder import seed_mem_storage

if TYPE_CHECKING:
    from osint_engine.config.settings import Settings
    from osint_engine.infrastructure.hashers.password_hasher import PasswordHasher
    from tests.conftest import MakeMemStorage


class TestMemSeederSeedingBehavior:
    def test_seeds_mem_storage_with_admin_user(
        self,
        make_mem_storage: MakeMemStorage,
        settings: Settings,
        password_hasher: PasswordHasher,
    ) -> None:
        mem_storage = make_mem_storage()

        admin = mem_storage.users.get("admin")

        assert admin is None

        seed_mem_storage(
            settings=settings, mem_storage=mem_storage, auth_hasher=password_hasher
        )

        admin = mem_storage.users.get("admin")

        assert admin is not None

        assert admin.role is Role.ADMIN

        assert admin.username == "admin"
