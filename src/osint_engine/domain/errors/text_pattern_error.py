from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.domain.errors.domain_error import DomainError
from osint_engine.domain.errors.error_category import ErrorCategory

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.domain.entities.bases.node import Node


class TextPatternError(DomainError, error_code=None): ...


class FieldPatternGroupMismatchError(
    TextPatternError,
    error_code="FIELD_PATTERN_GROUP_MISMATCH",
    category=ErrorCategory.INVALID_INPUT,
):
    node_type: type[Node[UUID]]
    expected: frozenset[str]
    actual: frozenset[str]

    @override
    def __init__(
        self,
        *,
        node_type: type[Node[UUID]],
        expected: frozenset[str],
        actual: frozenset[str],
    ) -> None:
        super().__init__(node_type=node_type, expected=expected, actual=actual)

    @override
    def _build_message(self) -> str:
        return (
            f"'{self.node_type.__name__}' pattern regex named groups {self.actual} "
            f"must exactly match its id_fields {self.expected}."
        )
