from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from osint_engine.application.consumption.entity_record import EntityRecord
from osint_engine.application.consumption.entity_stub import company_stub, person_stub
from osint_engine.application.revision.entity_revision import EntityRevision

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
    stub = person_stub(cpf)
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
    stub = company_stub(cnpj)
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
