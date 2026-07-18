from __future__ import annotations

from typing import override

from osint_engine.infrastructure.errors.infrastructure_error import InfrastructureError


class TokenError(InfrastructureError, error_code=None): ...


class InvalidTokenError(TokenError, error_code="TOKEN_INVALID"):
    detail: str

    @override
    def __init__(self, *, detail: str) -> None:
        super().__init__(detail=detail)

    @override
    def _build_message(self) -> str:
        return self.detail
