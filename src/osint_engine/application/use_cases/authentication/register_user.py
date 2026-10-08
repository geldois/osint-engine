from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.auth.user import User
from osint_engine.application.contracts.use_case import Command
from osint_engine.application.errors.auth_error import UsernameTakenError

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.contracts.hashers.password_hasher import (
        PasswordHasher,
    )
    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()


class RegisterUser(Command):
    uow_factory: Callable[[], UoW]
    password_hasher: PasswordHasher
    username: str
    password: str

    @override
    def __init__(
        self,
        *,
        uow_factory: Callable[[], UoW],
        password_hasher: PasswordHasher,
        username: str,
        password: str,
    ) -> None:
        super().__init__(
            uow_factory=uow_factory,
            password_hasher=password_hasher,
            username=username,
            password=password,
        )

    @override
    async def execute(self) -> None:
        _logger.info("user.registration.start", username=self.username)

        hashed_password = await asyncio.to_thread(
            self.password_hasher.hash_, password=self.password
        )
        user = User(hashed_password=hashed_password, username=self.username)

        async with self.uow_factory() as uow:
            inserted = await uow.users.save(user=user)

        if not inserted:
            _logger.warning("user.registration.username_taken", username=self.username)

            raise UsernameTakenError(username=self.username)

        _logger.info("user.registration.end", username=self.username)
