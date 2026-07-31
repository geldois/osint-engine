from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.application.errors.application_error import ApplicationError
from osint_engine.domain.errors.error_category import ErrorCategory

if TYPE_CHECKING:
    from osint_engine.domain.value_objects.pattern_set_id import PatternSetID


class TextIngestionError(ApplicationError, error_code=None): ...


class NoPatternMatchedError(
    TextIngestionError,
    error_code="TEXT_INGESTION_NO_PATTERN_MATCHED",
    category=ErrorCategory.INVALID_INPUT,
):
    pattern_set_id: PatternSetID

    @override
    def __init__(self, *, pattern_set_id: PatternSetID) -> None:
        super().__init__(pattern_set_id=pattern_set_id)

    @override
    def _build_message(self) -> str:
        return (
            f"No pattern in pattern set '{self.pattern_set_id}' matched anything "
            f"in the given text."
        )


class PatternSetNotFoundError(
    TextIngestionError,
    error_code="TEXT_INGESTION_PATTERN_SET_NOT_FOUND",
    category=ErrorCategory.NOT_FOUND,
):
    pattern_set_id: PatternSetID

    @override
    def __init__(self, *, pattern_set_id: PatternSetID) -> None:
        super().__init__(pattern_set_id=pattern_set_id)

    @override
    def _build_message(self) -> str:
        return f"No pattern set found with id '{self.pattern_set_id}'."


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
