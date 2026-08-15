from __future__ import annotations

from typing import override

from osint_engine.application.errors.application_error import ApplicationError
from osint_engine.domain.errors.error_category import ErrorCategory


class TextIngestionError(ApplicationError, error_code=None): ...


class NoPatternMatchedError(
    TextIngestionError,
    error_code="TEXT_INGESTION_NO_PATTERN_MATCHED",
    category=ErrorCategory.INVALID_INPUT,
):
    requested_patterns: frozenset[str]

    @override
    def __init__(self, *, requested_patterns: frozenset[str]) -> None:
        super().__init__(requested_patterns=requested_patterns)

    @override
    def _build_message(self) -> str:
        return (
            f"No pattern among {sorted(self.requested_patterns)} matched anything "
            f"in the given text."
        )


class UnknownPatternNameError(
    TextIngestionError,
    error_code="TEXT_INGESTION_UNKNOWN_PATTERN_NAME",
    category=ErrorCategory.INVALID_INPUT,
):
    names: frozenset[str]

    @override
    def __init__(self, *, names: frozenset[str]) -> None:
        super().__init__(names=names)

    @override
    def _build_message(self) -> str:
        return f"No atomic pattern or bundle registered under {sorted(self.names)}."


class UnsupportedPatternNodeTypeError(
    TextIngestionError,
    error_code="TEXT_INGESTION_UNSUPPORTED_PATTERN_NODE_TYPE",
    category=ErrorCategory.INTERNAL,
):
    node_type: type

    @override
    def __init__(self, *, node_type: type) -> None:
        super().__init__(node_type=node_type)

    @override
    def _build_message(self) -> str:
        return (
            f"'{self.node_type.__name__}' has no stub builder or mention-edge "
            f"mapping wired in IngestText."
        )
