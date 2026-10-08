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
    from tests.conftest import MakeMemStorage, MakeMemUoW, MakeUser
    from tests.test_src.test_application.conftest import MakeMemUoWFactory


class TestRegisterUserExecution:
    @pytest.mark.asyncio
    async def test_returns_the_new_user_and_stores_it(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
        argon2_password_hasher: Argon2PasswordHasher,
    ) -> None:
        mem_storage = make_mem_storage()
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = RegisterUser(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            password_hasher=argon2_password_hasher,
            username="alice",
            password="correct horse",
        )

        user = await use_case.execute()

        assert user.username == "alice"
        assert mem_storage.users == {"alice": user}

    @pytest.mark.asyncio
    async def test_never_stores_the_plaintext_password(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
        argon2_password_hasher: Argon2PasswordHasher,
    ) -> None:
        mem_storage = make_mem_storage()
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = RegisterUser(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            password_hasher=argon2_password_hasher,
            username="alice",
            password="correct horse",
        )

        user = await use_case.execute()

        assert "correct horse" not in user.hashed_password
        assert user.hashed_password.startswith("$argon2id$")
        assert argon2_password_hasher.verify(
            hash_=user.hashed_password, password="correct horse"
        )

    @pytest.mark.asyncio
    async def test_the_new_user_can_authenticate_with_the_chosen_password(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
        argon2_password_hasher: Argon2PasswordHasher,
    ) -> None:
        mem_storage = make_mem_storage()
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        uow_factory = make_mem_uow_factory(mem_uow=mem_uow)

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
        make_user: MakeUser,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
        argon2_password_hasher: Argon2PasswordHasher,
    ) -> None:
        existing = make_user(username="alice", hashed_password="original-hash")
        mem_storage = make_mem_storage(users=[existing])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = RegisterUser(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            password_hasher=argon2_password_hasher,
            username="alice",
            password="another password",
        )

        with pytest.raises(UsernameTakenError) as exception:
            await use_case.execute()

        assert exception.value.username == "alice"
        assert mem_storage.users == {"alice": existing}
