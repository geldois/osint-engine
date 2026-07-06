from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from osint_engine.infrastructure.hashers.argon2_password_hasher import (
        Argon2PasswordHasher,
    )


class TestArgon2PasswordHasherHashMethod:
    def test_hash_same_password_produces_valid_hashes_on_multiple_calls(
        self, password_hasher: Argon2PasswordHasher
    ) -> None:
        password = "test_password"  # noqa: S105
        hash_a = password_hasher.hash_(password=password)
        hash_b = password_hasher.hash_(password=password)

        assert password_hasher.verify(hash_=hash_a, password=password) is True

        assert password_hasher.verify(hash_=hash_b, password=password) is True

    def test_hash_different_passwords_produce_different_hashes(
        self, password_hasher: Argon2PasswordHasher
    ) -> None:
        password_a = "test_password_a"  # noqa: S105
        password_b = "test_password_b"  # noqa: S105

        hash1 = password_hasher.hash_(password=password_a)
        hash2 = password_hasher.hash_(password=password_b)

        assert hash1 != hash2


class TestArgon2PasswordHasherVerifyMethod:
    def test_verify_returns_true_for_hash_of_matching_password(
        self, password_hasher: Argon2PasswordHasher
    ) -> None:
        password = "correct_password"  # noqa: S105

        hash_ = password_hasher.hash_(password=password)

        assert password_hasher.verify(hash_=hash_, password=password) is True

    def test_verify_returns_false_for_hash_with_mismatching_password(
        self, password_hasher: Argon2PasswordHasher
    ) -> None:
        password = "correct_password"  # noqa: S105

        hash_ = password_hasher.hash_(password=password)

        assert password_hasher.verify(hash_=hash_, password="wrong_password") is False  # noqa: S106

    def test_verify_returns_bool_false_for_invalid_hash_format(
        self, password_hasher: Argon2PasswordHasher
    ) -> None:
        invalid_hash = "not_an_argon2_hash_at_all"
        password = "any_password"  # noqa: S105

        result = password_hasher.verify(hash_=invalid_hash, password=password)

        assert isinstance(result, bool)

        assert result is False
