from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from osint_engine.application.auth.user import Role
from osint_engine.infrastructure.errors.token_error import InvalidTokenError
from osint_engine.interface.errors.authorization_error import InsufficientRoleError
from osint_engine.interface.http.fastapi.dependencies.jwt_guard import (
    build_jwt_guard,
    build_role_guard,
)

if TYPE_CHECKING:
    from osint_engine.config.container import Container
    from osint_engine.infrastructure.services.pyjwt_service import PyJWTService


# TESTS


class TestJwtGuardWithValidToken:
    @pytest.mark.asyncio
    async def test_valid_token_passes_without_error(
        self, container: Container, pyjwt_service: PyJWTService
    ) -> None:
        token = pyjwt_service.create_access_token(username="admin", role="admin")
        guard = build_jwt_guard(container=container)

        await guard(token)

    @pytest.mark.asyncio
    async def test_valid_token_returns_decoded_claims(
        self, container: Container, pyjwt_service: PyJWTService
    ) -> None:
        token = pyjwt_service.create_access_token(username="admin", role="admin")
        guard = build_jwt_guard(container=container)

        claims = await guard(token)

        assert claims["sub"] == "admin"

        assert claims["role"] == "admin"


class TestJwtGuardWithInvalidToken:
    @pytest.mark.asyncio
    async def test_malformed_token_raises_invalid_token_error(
        self, container: Container
    ) -> None:
        guard = build_jwt_guard(container=container)

        with pytest.raises(InvalidTokenError):
            await guard("not.a.valid.token")

    @pytest.mark.asyncio
    async def test_empty_token_raises_invalid_token_error(
        self, container: Container
    ) -> None:
        guard = build_jwt_guard(container=container)

        with pytest.raises(InvalidTokenError):
            await guard("")

    @pytest.mark.asyncio
    async def test_corrupted_token_raises_invalid_token_error(
        self, container: Container, pyjwt_service: PyJWTService
    ) -> None:
        valid_token = pyjwt_service.create_access_token(username="admin", role="admin")
        corrupted = valid_token[:-5] + "xxxxx"
        guard = build_jwt_guard(container=container)

        with pytest.raises(InvalidTokenError):
            await guard(corrupted)


class TestRoleGuardWithAllowedRole:
    @pytest.mark.asyncio
    async def test_allowed_role_passes_without_error(
        self, container: Container, pyjwt_service: PyJWTService
    ) -> None:
        token = pyjwt_service.create_access_token(username="admin", role=Role.ADMIN)
        guard = build_role_guard(
            container=container, allowed_roles=frozenset({Role.ADMIN})
        )

        await guard(token)

    @pytest.mark.asyncio
    async def test_allowed_role_returns_decoded_claims(
        self, container: Container, pyjwt_service: PyJWTService
    ) -> None:
        token = pyjwt_service.create_access_token(username="visitor", role=Role.VIEWER)
        guard = build_role_guard(
            container=container, allowed_roles=frozenset({Role.ADMIN, Role.VIEWER})
        )

        claims = await guard(token)

        assert claims["sub"] == "visitor"

        assert claims["role"] == Role.VIEWER


class TestRoleGuardWithDisallowedRole:
    @pytest.mark.asyncio
    async def test_role_outside_allowed_set_raises_insufficient_role_error(
        self, container: Container, pyjwt_service: PyJWTService
    ) -> None:
        token = pyjwt_service.create_access_token(username="visitor", role=Role.VIEWER)
        guard = build_role_guard(
            container=container, allowed_roles=frozenset({Role.ADMIN})
        )

        with pytest.raises(InsufficientRoleError):
            await guard(token)

    @pytest.mark.asyncio
    async def test_disallowed_role_error_carries_offending_role(
        self, container: Container, pyjwt_service: PyJWTService
    ) -> None:
        token = pyjwt_service.create_access_token(username="visitor", role=Role.VIEWER)
        guard = build_role_guard(
            container=container, allowed_roles=frozenset({Role.ADMIN})
        )

        with pytest.raises(InsufficientRoleError) as exc_info:
            await guard(token)

        assert exc_info.value.role == Role.VIEWER
