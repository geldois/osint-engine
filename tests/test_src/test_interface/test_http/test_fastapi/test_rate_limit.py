from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from starlette.requests import Request

from osint_engine.interface.http.fastapi.rate_limit import build_user_bucket_key

if TYPE_CHECKING:
    from osint_engine.config.container import Container
    from osint_engine.infrastructure.services.pyjwt_service import PyJWTService


def _request(*, authorization: str | None) -> Request:
    headers = (
        [(b"authorization", authorization.encode())]
        if authorization is not None
        else []
    )

    return Request({"type": "http", "headers": headers})


class TestBuildUserBucketKey:
    def test_a_valid_token_keys_the_bucket_by_its_username(
        self, container: Container, pyjwt_service: PyJWTService
    ) -> None:
        key = build_user_bucket_key(container=container, scope="expansion:cnpj")
        token = pyjwt_service.create_access_token(username="alice")

        assert (
            key(_request(authorization=f"Bearer {token}"))
            == "expansion:cnpj:user:alice"
        )

    def test_two_users_never_share_a_bucket(
        self, container: Container, pyjwt_service: PyJWTService
    ) -> None:
        key = build_user_bucket_key(container=container, scope="expansion:cnpj")
        alice = pyjwt_service.create_access_token(username="alice")
        bob = pyjwt_service.create_access_token(username="bob")

        assert key(_request(authorization=f"Bearer {alice}")) != key(
            _request(authorization=f"Bearer {bob}")
        )

    def test_the_same_user_gets_a_different_bucket_per_scope(
        self, container: Container, pyjwt_service: PyJWTService
    ) -> None:
        token = pyjwt_service.create_access_token(username="alice")
        request = _request(authorization=f"Bearer {token}")

        assert build_user_bucket_key(container=container, scope="expansion:cnpj")(
            request
        ) != build_user_bucket_key(container=container, scope="expansion:cpf")(request)

    def test_the_bearer_scheme_is_matched_case_insensitively(
        self, container: Container, pyjwt_service: PyJWTService
    ) -> None:
        key = build_user_bucket_key(container=container, scope="s")
        token = pyjwt_service.create_access_token(username="alice")

        assert key(_request(authorization=f"bEaReR {token}")) == "s:user:alice"

    @pytest.mark.parametrize(
        "authorization",
        [None, "", "Bearer", "Bearer ", "Basic abc", "Bearer not.a.jwt", "token"],
    )
    def test_a_missing_or_unusable_credential_falls_back_to_one_anonymous_bucket(
        self, container: Container, authorization: str | None
    ) -> None:
        key = build_user_bucket_key(container=container, scope="s")

        assert key(_request(authorization=authorization)) == "s:anonymous"

    def test_a_tampered_token_cannot_claim_another_users_bucket(
        self, container: Container, pyjwt_service: PyJWTService
    ) -> None:
        key = build_user_bucket_key(container=container, scope="s")
        token = pyjwt_service.create_access_token(username="alice")
        tampered = token[:-5] + "xxxxx"

        assert key(_request(authorization=f"Bearer {tampered}")) == "s:anonymous"

    def test_a_user_named_anonymous_never_shares_the_fallback_bucket(
        self, container: Container, pyjwt_service: PyJWTService
    ) -> None:
        key = build_user_bucket_key(container=container, scope="s")
        token = pyjwt_service.create_access_token(username="anonymous")

        assert key(_request(authorization=f"Bearer {token}")) != key(
            _request(authorization=None)
        )
