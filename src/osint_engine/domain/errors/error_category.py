from __future__ import annotations

from enum import Enum, unique


@unique
class ErrorCategory(Enum):
    """Semantic classification of an error, independent of any delivery mechanism.

    Every layer's error hierarchy declares one of these; the HTTP interface (and
    any other delivery mechanism) maps a category to its own status vocabulary.
    Keeping the taxonomy here, in the innermost layer, lets the interface classify
    an error without importing the concrete error types of outer layers — so the
    dependency rule holds and interface never imports infrastructure.
    """

    NOT_FOUND = "not_found"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    RATE_LIMITED = "rate_limited"
    INVALID_INPUT = "invalid_input"
    UPSTREAM_FAILURE = "upstream_failure"
    INTERNAL = "internal"
