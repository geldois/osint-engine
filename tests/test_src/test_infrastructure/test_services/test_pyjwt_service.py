from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest
from jwt import decode  # pyright: ignore[reportUnknownVariableType]

from osint_engine.infrastructure.errors.token_error import InvalidTokenError

if TYPE_CHECKING:
    from osint_engine.infrastructure.services.pyjwt_service import PyJWTService


class TestPyJWTServiceAlgorithmProperty:
    def test_algorithm_property_returns_jwt_algorithm(
        self, pyjwt_service: PyJWTService
    ) -> None:
        assert pyjwt_service.algorithm == "HS256"

    def test_algorithm_property_returns_string(
        self, pyjwt_service: PyJWTService
    ) -> None:
        algorithm = pyjwt_service.algorithm

        assert isinstance(algorithm, str)

        assert len(algorithm) > 0


class TestPyJWTServiceCreateAccessToken:
    def test_create_access_token_returns_string(
        self, pyjwt_service: PyJWTService
    ) -> None:
        token = pyjwt_service.create_access_token(username="alice", role="admin")

        assert isinstance(token, str)

        assert len(token) > 0

    def test_create_access_token_with_correct_data_produces_decodable_token(
        self, pyjwt_service: PyJWTService
    ) -> None:
        username = "alice"
        role = "admin"

        token = pyjwt_service.create_access_token(username=username, role=role)

        decoded = decode(
            jwt=token,
            key=pyjwt_service.secret_key,
            algorithms=[pyjwt_service.algorithm],
        )

        assert decoded["sub"] == username

        assert decoded["role"] == role

    def test_create_access_token_includes_expiration_time(
        self, pyjwt_service: PyJWTService
    ) -> None:
        token = pyjwt_service.create_access_token(username="bob", role="viewer")

        decoded = decode(
            jwt=token,
            key=pyjwt_service.secret_key,
            algorithms=[pyjwt_service.algorithm],
        )

        assert "exp" in decoded

        exp_timestamp = decoded["exp"]

        assert isinstance(exp_timestamp, int)

        expiration_time = datetime.fromtimestamp(exp_timestamp, tz=UTC)

        now = datetime.now(tz=UTC)

        time_diff = (expiration_time - now).total_seconds()

        assert 0 < time_diff < pyjwt_service.access_token_expire_minutes * 60 + 5

    def test_create_access_token_includes_username_as_sub_claim(
        self, pyjwt_service: PyJWTService
    ) -> None:
        username = "charlie"

        token = pyjwt_service.create_access_token(username=username, role="admin")

        decoded = decode(
            jwt=token,
            key=pyjwt_service.secret_key,
            algorithms=[pyjwt_service.algorithm],
        )

        assert decoded["sub"] == username

    def test_create_access_token_includes_role_claim(
        self, pyjwt_service: PyJWTService
    ) -> None:
        role = "editor"

        token = pyjwt_service.create_access_token(username="diana", role=role)

        decoded = decode(
            jwt=token,
            key=pyjwt_service.secret_key,
            algorithms=[pyjwt_service.algorithm],
        )

        assert decoded["role"] == role


class TestPyJWTServiceDecodeAccessToken:
    def test_decode_access_token_with_valid_token_returns_dict(
        self, pyjwt_service: PyJWTService
    ) -> None:
        token = pyjwt_service.create_access_token(username="eve", role="admin")

        decoded = pyjwt_service.decode_access_token(token=token)

        assert isinstance(decoded, dict)

    def test_decode_access_token_returns_sub_field(
        self, pyjwt_service: PyJWTService
    ) -> None:
        username = "frank"

        token = pyjwt_service.create_access_token(username=username, role="viewer")

        decoded = pyjwt_service.decode_access_token(token=token)

        assert "sub" in decoded

        assert decoded["sub"] == username

    def test_decode_access_token_returns_role_field(
        self, pyjwt_service: PyJWTService
    ) -> None:
        role = "admin"

        token = pyjwt_service.create_access_token(username="grace", role=role)

        decoded = pyjwt_service.decode_access_token(token=token)

        assert "role" in decoded

        assert decoded["role"] == role

    def test_decode_access_token_returns_exp_field(
        self, pyjwt_service: PyJWTService
    ) -> None:
        token = pyjwt_service.create_access_token(username="henry", role="admin")

        decoded = pyjwt_service.decode_access_token(token=token)

        assert "exp" in decoded

        assert isinstance(decoded["exp"], int)

    def test_decode_access_token_returns_valid_dict_with_all_fields(
        self, pyjwt_service: PyJWTService
    ) -> None:
        username = "iris"
        role = "editor"

        token = pyjwt_service.create_access_token(username=username, role=role)

        decoded = pyjwt_service.decode_access_token(token=token)

        assert isinstance(decoded, dict)

        assert "sub" in decoded

        assert "role" in decoded

        assert "exp" in decoded

        assert decoded["sub"] == username

        assert decoded["role"] == role

        assert isinstance(decoded["exp"], int)

    def test_decode_access_token_with_invalid_token_raises_invalid_token_error(
        self, pyjwt_service: PyJWTService
    ) -> None:
        invalid_token = "invalid.token.string"

        with pytest.raises(InvalidTokenError):
            pyjwt_service.decode_access_token(token=invalid_token)

    def test_decode_access_token_with_corrupted_token_raises_invalid_token_error(
        self, pyjwt_service: PyJWTService
    ) -> None:
        valid_token = pyjwt_service.create_access_token(username="jack", role="admin")

        corrupted_token = valid_token[:-5] + "xxxxx"

        with pytest.raises(InvalidTokenError):
            pyjwt_service.decode_access_token(token=corrupted_token)

    def test_decode_access_token_with_empty_token_raises_invalid_token_error(
        self, pyjwt_service: PyJWTService
    ) -> None:
        with pytest.raises(InvalidTokenError):
            pyjwt_service.decode_access_token(token="")

    def test_decode_access_token_with_token_signed_with_different_key_raises_error(
        self, pyjwt_service: PyJWTService
    ) -> None:
        token = pyjwt_service.create_access_token(username="kate", role="admin")

        modified_token = token[:-5] + "xxxxx"

        with pytest.raises(InvalidTokenError):
            pyjwt_service.decode_access_token(token=modified_token)
