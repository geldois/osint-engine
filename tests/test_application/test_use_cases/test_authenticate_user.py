from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from osint_engine.application.errors.auth_error import InvalidCredentialsError
from osint_engine.application.use_cases.authentication.authenticate_user import (
    AuthenticateUser,
)

if TYPE_CHECKING:
    from osint_engine.infrastructure.hashers.argon2_password_hasher import (
        Argon2PasswordHasher,
    )
    from tests.conftest import MakeMemStorage, MakeUser
    from tests.test_application.conftest import MakeMemUoW, MakeMemUoWFactory


class TestAuthenticateUserExecution:
    @pytest.mark.asyncio
    async def test_execute_returns_user_on_correct_credentials(
        self,
        make_user: MakeUser,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
        argon2_password_hasher: Argon2PasswordHasher,
    ) -> None:
        password = "test_password"
        hashed_password = argon2_password_hasher.hash_(password=password)
        user = make_user(username="testuser", hashed_password=hashed_password)
        mem_storage = make_mem_storage(users=[user])
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        uow_factory = make_mem_uow_factory(mem_uow=mem_uow)

        use_case = AuthenticateUser(
            uow_factory=uow_factory,
            password_hasher=argon2_password_hasher,
            username="testuser",
            password=password,
        )

        result = await use_case.execute()

        assert result == user

        assert result.username == "testuser"

    @pytest.mark.asyncio
    async def test_execute_raises_invalid_credentials_error_when_user_not_found(
        self,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
        argon2_password_hasher: Argon2PasswordHasher,
    ) -> None:
        mem_uow = make_mem_uow()
        uow_factory = make_mem_uow_factory(mem_uow=mem_uow)

        use_case = AuthenticateUser(
            uow_factory=uow_factory,
            password_hasher=argon2_password_hasher,
            username="nonexistent_user",
            password="any_password",
        )

        with pytest.raises(InvalidCredentialsError) as exception:
            await use_case.execute()

        assert exception.value.username == "nonexistent_user"

    @pytest.mark.asyncio
    async def test_execute_raises_invalid_credentials_error_when_password_wrong(
        self,
        make_user: MakeUser,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
        argon2_password_hasher: Argon2PasswordHasher,
    ) -> None:
        password = "correct_password"
        hashed_password = argon2_password_hasher.hash_(password=password)
        user = make_user(username="testuser", hashed_password=hashed_password)
        mem_storage = make_mem_storage(users=[user])
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        uow_factory = make_mem_uow_factory(mem_uow=mem_uow)

        use_case = AuthenticateUser(
            uow_factory=uow_factory,
            password_hasher=argon2_password_hasher,
            username="testuser",
            password="wrong_password",
        )

        with pytest.raises(InvalidCredentialsError) as exception:
            await use_case.execute()

        assert exception.value.username == "testuser"

    @pytest.mark.asyncio
    async def test_invalid_credentials_error_contains_correct_username(
        self,
        make_user: MakeUser,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
        argon2_password_hasher: Argon2PasswordHasher,
    ) -> None:
        password = "correct_password"
        hashed_password = argon2_password_hasher.hash_(password=password)
        user = make_user(username="alice", hashed_password=hashed_password)
        mem_storage = make_mem_storage(users=[user])
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        uow_factory = make_mem_uow_factory(mem_uow=mem_uow)

        use_case = AuthenticateUser(
            uow_factory=uow_factory,
            password_hasher=argon2_password_hasher,
            username="alice",
            password="wrong_password",
        )

        with pytest.raises(InvalidCredentialsError) as exception:
            await use_case.execute()

        error = exception.value

        assert error.username == "alice"

        assert "alice" in str(error)
