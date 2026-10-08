from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from osint_engine.application.errors.auth_error import UsernameTakenError
from osint_engine.application.use_cases.authentication.authenticate_user import (
    AuthenticateUser,
)
from osint_engine.application.use_cases.authentication.register_user import (
    RegisterUser,
)

if TYPE_CHECKING:
    from osint_engine.infrastructure.hashers.argon2_password_hasher import (
        Argon2PasswordHasher,
    )
    from tests.fakes.persistence import FakePgPool
    from tests.test_src.test_application.conftest import MakeHybridUoWFactory


class TestRegisterUserExecution:
    @pytest.mark.asyncio
    async def test_stores_the_new_user_and_returns_nothing(
        self,
        fake_pg_pool: FakePgPool,
        make_hybrid_uow_factory: MakeHybridUoWFactory,
        argon2_password_hasher: Argon2PasswordHasher,
    ) -> None:
        use_case = RegisterUser(
            uow_factory=make_hybrid_uow_factory(),
            password_hasher=argon2_password_hasher,
            username="alice",
            password="correct horse",
        )

        result = await use_case.execute()

        assert result is None
        assert set(fake_pg_pool.users) == {"alice"}

    @pytest.mark.asyncio
    async def test_never_stores_the_plaintext_password(
        self,
        fake_pg_pool: FakePgPool,
        make_hybrid_uow_factory: MakeHybridUoWFactory,
        argon2_password_hasher: Argon2PasswordHasher,
    ) -> None:
        await RegisterUser(
            uow_factory=make_hybrid_uow_factory(),
            password_hasher=argon2_password_hasher,
            username="alice",
            password="correct horse",
        ).execute()

        stored = fake_pg_pool.users["alice"]

        assert "correct horse" not in stored
        assert stored.startswith("$argon2id$")
        assert argon2_password_hasher.verify(hash_=stored, password="correct horse")

    @pytest.mark.asyncio
    async def test_the_new_user_can_authenticate_with_the_chosen_password(
        self,
        make_hybrid_uow_factory: MakeHybridUoWFactory,
        argon2_password_hasher: Argon2PasswordHasher,
    ) -> None:
        uow_factory = make_hybrid_uow_factory()

        await RegisterUser(
            uow_factory=uow_factory,
            password_hasher=argon2_password_hasher,
            username="alice",
            password="correct horse",
        ).execute()

        authenticated = await AuthenticateUser(
            uow_factory=uow_factory,
            password_hasher=argon2_password_hasher,
            username="alice",
            password="correct horse",
        ).execute()

        assert authenticated.username == "alice"

    @pytest.mark.asyncio
    async def test_raises_username_taken_and_keeps_the_original_hash(
        self,
        fake_pg_pool: FakePgPool,
        make_hybrid_uow_factory: MakeHybridUoWFactory,
        argon2_password_hasher: Argon2PasswordHasher,
    ) -> None:
        fake_pg_pool.users["alice"] = "original-hash"

        use_case = RegisterUser(
            uow_factory=make_hybrid_uow_factory(),
            password_hasher=argon2_password_hasher,
            username="alice",
            password="another password",
        )

        with pytest.raises(UsernameTakenError) as exception:
            await use_case.execute()

        assert exception.value.username == "alice"
        assert fake_pg_pool.users == {"alice": "original-hash"}
