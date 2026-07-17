from __future__ import annotations

from typing import TYPE_CHECKING, Literal, override

from osint_engine.application.errors.application_error import ApplicationError

if TYPE_CHECKING:
    from uuid import UUID


class RevisionError(ApplicationError): ...


class EntityIDMismatchError(RevisionError):
    left_id: UUID
    right_id: UUID

    @override
    def __init__(self, *, left_id: UUID, right_id: UUID) -> None:
        super().__init__(left_id=left_id, right_id=right_id)

    @override
    def _build_message(self) -> str:
        return (
            f"Cannot reconcile entities with different ids: "
            f"left.id={self.left_id}, right.id={self.right_id}."
        )


class NonUTCAttributeError(RevisionError):
    attribute: Literal["fetched_at", "merged_at"]
    tzinfo: str

    @override
    def __init__(
        self, *, attribute: Literal["fetched_at", "merged_at"], tzinfo: str
    ) -> None:
        super().__init__(attribute=attribute, tzinfo=tzinfo)

    @override
    def _build_message(self) -> str:
        return f"Revision.{self.attribute} must be UTC, got tzinfo={self.tzinfo}."


class EmptyRevisionSelectionError(RevisionError):
    @override
    def __init__(self) -> None:
        super().__init__()

    @override
    def _build_message(self) -> str:
        return "Cannot select a current revision from an empty set of revisions."
