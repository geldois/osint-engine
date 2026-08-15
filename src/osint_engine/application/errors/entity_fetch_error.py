from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.application.errors.application_error import ApplicationError
from osint_engine.domain.errors.error_category import ErrorCategory

if TYPE_CHECKING:
    from datetime import datetime
    from uuid import UUID


class EntityFetchError(ApplicationError, error_code=None): ...


class AlreadyFetchedError(
    EntityFetchError,
    error_code="ENTITY_ALREADY_FETCHED",
    category=ErrorCategory.CONFLICT,
):
    entity_id: UUID
    provider: str
    fetched_at: datetime

    @override
    def __init__(self, *, entity_id: UUID, provider: str, fetched_at: datetime) -> None:
        super().__init__(entity_id=entity_id, provider=provider, fetched_at=fetched_at)

    @override
    def _build_message(self) -> str:
        return (
            f"Entity '{self.entity_id}' was already fetched from '{self.provider}' "
            f"at {self.fetched_at.isoformat()}. Pass force=true to fetch again."
        )
