from __future__ import annotations

from typing import override

from osint_engine.interface.errors.interface_error import InterfaceError


class RateLimitError(InterfaceError, error_code=None): ...


class RateLimitExceededError(RateLimitError, error_code="RATE_LIMIT_EXCEEDED"):
    retry_after_seconds: int

    @override
    def __init__(self, *, retry_after_seconds: int) -> None:
        super().__init__(retry_after_seconds=retry_after_seconds)

    @override
    def _build_message(self) -> str:
        return f"Rate limit exceeded, retry after {self.retry_after_seconds}s"
