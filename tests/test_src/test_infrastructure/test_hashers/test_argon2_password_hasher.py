from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from osint_engine.infrastructure.hashers.argon2_password_hasher import (
        Argon2PasswordHasher,
    )


class TestArgon2PasswordHasherHashMethod:
    def test_hash_same_password_produces_valid_hashes_on_multiple_calls(
        self, argon2_password_hasher: Argon2PasswordHasher
    ) -> None:
        password = "test_password"
        hash_a = argon2_password_hasher.hash_(password=password)
        hash_b = argon2_password_hasher.hash_(password=password)

        assert argon2_password_hasher.verify(hash_=hash_a, password=password) is True

        assert argon2_password_hasher.verify(hash_=hash_b, password=password) is True

    def test_hash_different_passwords_produce_different_hashes(
        self, argon2_password_hasher: Argon2PasswordHasher
    ) -> None:
        password_a = "test_password_a"
        password_b = "test_password_b"

        hash1 = argon2_password_hasher.hash_(password=password_a)
        hash2 = argon2_password_hasher.hash_(password=password_b)

        assert hash1 != hash2


class TestArgon2PasswordHasherVerifyMethod:
    def test_verify_returns_true_for_hash_of_matching_password(
        self, argon2_password_hasher: Argon2PasswordHasher
    ) -> None:
        password = "correct_password"

        hash_ = argon2_password_hasher.hash_(password=password)

        assert argon2_password_hasher.verify(hash_=hash_, password=password) is True

    def test_verify_returns_false_for_hash_with_mismatching_password(
        self, argon2_password_hasher: Argon2PasswordHasher
    ) -> None:
        password = "correct_password"

        hash_ = argon2_password_hasher.hash_(password=password)

        assert (
            argon2_password_hasher.verify(hash_=hash_, password="wrong_password")
            is False
        )

    def test_verify_returns_bool_false_for_invalid_hash_format(
        self, argon2_password_hasher: Argon2PasswordHasher
    ) -> None:
        invalid_hash = "not_an_argon2_hash_at_all"
        password = "any_password"

        result = argon2_password_hasher.verify(hash_=invalid_hash, password=password)

        assert isinstance(result, bool)

        assert result is False

    def test_verify_returns_false_when_hash_is_none(
        self, argon2_password_hasher: Argon2PasswordHasher
    ) -> None:
        password = "any_password"

        result = argon2_password_hasher.verify(hash_=None, password=password)

        assert result is False

    def test_verify_none_hash_and_wrong_password_have_indistinguishable_timing(
        self, argon2_password_hasher: Argon2PasswordHasher
    ) -> None:
        correct_password = "correct_password"
        wrong_password = "wrong_password"

        hash_ = argon2_password_hasher.hash_(password=correct_password)

        samples_none: list[float] = []
        samples_wrong: list[float] = []

        for _ in range(10):
            start = time.perf_counter()
            argon2_password_hasher.verify(hash_=None, password=correct_password)
            samples_none.append(time.perf_counter() - start)

            start = time.perf_counter()
            argon2_password_hasher.verify(hash_=hash_, password=wrong_password)
            samples_wrong.append(time.perf_counter() - start)

        median_none = sorted(samples_none)[len(samples_none) // 2]
        median_wrong = sorted(samples_wrong)[len(samples_wrong) // 2]

        ratio = max(median_none, median_wrong) / min(median_none, median_wrong)

        assert ratio < 3, (
            f"Timing attack vulnerability: "
            f"None hash median={median_none:.6f}s, "
            f"wrong password median={median_wrong:.6f}s, "
            f"ratio={ratio:.2f}x (should be <3x)"
        )
