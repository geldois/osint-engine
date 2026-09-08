from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from osint_engine.application.consumption.entity_record import EntityRecord
from osint_engine.application.contracts.use_case import UseCaseRegistry
from osint_engine.application.errors.entity_fetch_error import AlreadyFetchedError

if TYPE_CHECKING:
    from datetime import datetime
    from uuid import UUID

    from osint_engine.application.contracts.uow import UoW
    from osint_engine.application.contracts.use_case import UseCase

ALREADY_FETCHED_OUTCOMES = frozenset({"empty", "expanded"})


async def _find_previous_attempt(
    *, uow: UoW, entity_id: UUID, provider: str
) -> EntityRecord | None:
    records = await uow.entity_records.list_by_entity_id(entity_id=entity_id)

    return next(
        (
            record
            for record in records
            if record.provider == provider
            and record.outcome in ALREADY_FETCHED_OUTCOMES
        ),
        None,
    )


async def find_already_fetched_error(  # noqa: PLR0913
    *,
    uow: UoW,
    entity_id: UUID,
    use_case: type[UseCase[object]],
    force: bool,
    requested_at: datetime,
    username: str,
) -> AlreadyFetchedError | None:
    provider = UseCaseRegistry.billing_for(use_case).provider

    if force:
        return None

    previous = await _find_previous_attempt(
        uow=uow, entity_id=entity_id, provider=provider
    )

    if previous is None:
        return None

    await uow.entity_records.save(
        record=EntityRecord(
            id=uuid4(),
            entity_id=entity_id,
            entity_ref=previous.entity_ref,
            outcome="already_fetched",
            provider=provider,
            requested_at=requested_at,
            username=username,
        )
    )

    return AlreadyFetchedError(
        entity_id=entity_id, provider=provider, fetched_at=previous.requested_at
    )


async def is_already_fetched(
    *, uow: UoW, entity_id: UUID, use_case: type[UseCase[object]]
) -> bool:
    provider = UseCaseRegistry.billing_for(use_case).provider

    previous = await _find_previous_attempt(
        uow=uow, entity_id=entity_id, provider=provider
    )

    return previous is not None
