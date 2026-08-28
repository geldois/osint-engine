from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from osint_engine.application.consumption.entity_record import EntityRecord
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.person import Person

if TYPE_CHECKING:
    from datetime import datetime

    from osint_engine.application.contracts.uow import UoW
    from osint_engine.domain.entities.bases.graph import Graph


async def ensure_person_logged(  # noqa: PLR0913
    *,
    uow: UoW,
    cpf: str,
    provider: str,
    username: str,
    requested_at: datetime,
    revision: EntityRevision[Graph] | None,
) -> None:
    stub = Person(
        age_range=None,
        birthdate=None,
        cpf=cpf,
        name=None,
        registration_date=None,
        registration_status=None,
    )
    stub_revision = EntityRevision(
        entity=stub, fetched_at=requested_at, merged_at=None, provider=provider
    )
    await uow.nodes.merge(revision=stub_revision)

    await uow.entity_records.save(
        record=EntityRecord(
            id=uuid4(),
            entity_id=stub.id,
            entity_ref=stub_revision.ref,
            outcome="empty" if revision is None else "expanded",
            provider=provider,
            requested_at=requested_at,
            username=username,
        )
    )


async def ensure_company_logged(  # noqa: PLR0913
    *,
    uow: UoW,
    cnpj: str,
    provider: str,
    username: str,
    requested_at: datetime,
    revision: EntityRevision[Graph] | None,
) -> None:
    stub = Company(
        activity_start_date=None,
        cnpj=cnpj,
        is_headquarters=None,
        legal_name=None,
        legal_nature=None,
        registration_status=None,
        registration_status_date=None,
        registration_status_reason=None,
        share_capital=None,
        size_category=None,
        trade_name=None,
    )
    stub_revision = EntityRevision(
        entity=stub, fetched_at=requested_at, merged_at=None, provider=provider
    )
    await uow.nodes.merge(revision=stub_revision)

    await uow.entity_records.save(
        record=EntityRecord(
            id=uuid4(),
            entity_id=stub.id,
            entity_ref=stub_revision.ref,
            outcome="empty" if revision is None else "expanded",
            provider=provider,
            requested_at=requested_at,
            username=username,
        )
    )
