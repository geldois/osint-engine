from __future__ import annotations

from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.auth.user import User
from osint_engine.application.contracts.use_case import Query
from osint_engine.application.errors.auth_error import InvalidCredentialsError

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.contracts.hashers.password_hasher import (
        PasswordHasher,
    )
    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()


class AuthenticateUser(Query[User]):
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
    async def execute(self) -> User:
        _logger.info("user.authentication.start", username=self.username)

        async with self.uow_factory() as uow:
            user = await uow.users.find(username=self.username)

            result: bool = self.password_hasher.verify(
                hash_=user.hashed_password if user is not None else None,
                password=self.password,
            )

            if user is None or not result:
                _logger.warning("authentication_failure", username=self.username)

                raise InvalidCredentialsError(username=self.username)

        _logger.info("user.authentication.end", username=self.username)

        return user
