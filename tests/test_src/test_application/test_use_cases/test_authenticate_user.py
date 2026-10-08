from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from osint_engine.application.auth.user import User
from osint_engine.application.errors.auth_error import InvalidCredentialsError
from osint_engine.application.use_cases.authentication.authenticate_user import (
    AuthenticateUser,
)

if TYPE_CHECKING:
    from osint_engine.infrastructure.hashers.argon2_password_hasher import (
        Argon2PasswordHasher,
    )
    from tests.fakes.persistence import FakePgPool
    from tests.test_src.test_application.conftest import MakeHybridUoWFactory


class TestAuthenticateUserExecution:
    @pytest.mark.asyncio
    async def test_execute_returns_user_on_correct_credentials(
        self,
        fake_pg_pool: FakePgPool,
        make_hybrid_uow_factory: MakeHybridUoWFactory,
        argon2_password_hasher: Argon2PasswordHasher,
    ) -> None:
        hashed_password = argon2_password_hasher.hash_(password="test_password")
        fake_pg_pool.users["testuser"] = hashed_password

        use_case = AuthenticateUser(
            uow_factory=make_hybrid_uow_factory(),
            password_hasher=argon2_password_hasher,
            username="testuser",
            password="test_password",
        )

        result = await use_case.execute()

        assert result == User(hashed_password=hashed_password, username="testuser")

    @pytest.mark.asyncio
    async def test_execute_raises_invalid_credentials_error_when_user_not_found(
        self,
        make_hybrid_uow_factory: MakeHybridUoWFactory,
        argon2_password_hasher: Argon2PasswordHasher,
    ) -> None:
        use_case = AuthenticateUser(
            uow_factory=make_hybrid_uow_factory(),
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
        fake_pg_pool: FakePgPool,
        make_hybrid_uow_factory: MakeHybridUoWFactory,
        argon2_password_hasher: Argon2PasswordHasher,
    ) -> None:
        fake_pg_pool.users["alice"] = argon2_password_hasher.hash_(
            password="correct_password"
        )

        use_case = AuthenticateUser(
            uow_factory=make_hybrid_uow_factory(),
            password_hasher=argon2_password_hasher,
            username="alice",
            password="wrong_password",
        )

        with pytest.raises(InvalidCredentialsError) as exception:
            await use_case.execute()

        error = exception.value

        assert error.username == "alice"
        assert "alice" in str(error)
