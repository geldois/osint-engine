from __future__ import annotations

from enum import Enum, unique


@unique
class ErrorCategory(Enum):
    NOT_FOUND = "not_found"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    RATE_LIMITED = "rate_limited"
    INVALID_INPUT = "invalid_input"
    UPSTREAM_FAILURE = "upstream_failure"
    INTERNAL = "internal"
