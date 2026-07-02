from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.application.auth.user import Role, User

if TYPE_CHECKING:
    from osint_engine.application.contracts.hashers.auth_hasher import AuthHasher
    from osint_engine.config.settings import Settings
    from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage


def seed_mem_storage(
    *, settings: Settings, mem_storage: MemStorage, auth_hasher: AuthHasher
) -> None:
    user = User(
        hashed_password=auth_hasher.hash_(secret=settings.admin_password),
        role=Role.ADMIN,
        username="admin",
    )

    mem_storage.users[user.username] = user
