from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Protocol
from uuid import UUID, uuid4

import pytest

from osint_engine.application.auth.external_credential import (
    ExternalCredential,
    Provider,
)
from osint_engine.application.auth.user import User
from osint_engine.application.consumption.entity_record import EntityRecord
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.application.revision.policies.revision_merge_policy import (
    keep_incoming_policy,
)
from osint_engine.application.revision.policies.revision_selection_policy import (
    select_current_by_newest_fetched,
)
from osint_engine.config.container import Policies
from osint_engine.domain.entities.bases.entity import Entity

if TYPE_CHECKING:
    from osint_engine.application.consumption.entity_record import ConsumptionOutcome
    from osint_engine.application.revision.policies.revision_merge_policy import (
        RevisionMergePolicy,
    )
    from osint_engine.application.revision.policies.revision_selection_policy import (
        RevisionSelectionPolicy,
    )
    from osint_engine.domain.value_objects.entity_ref import EntityRef


class MakeEntityRevision(Protocol):
    def __call__[Entity_: Entity[UUID]](
        self,
        *,
        entity: Entity_,
        fetched_at: datetime | None = None,
        merged_at: datetime | None = None,
        provider: str = "test_provider",
    ) -> EntityRevision[Entity_]: ...


type MakeEntityRecord = Callable[..., EntityRecord]
type MakeExternalCredential = Callable[..., ExternalCredential]
type MakePolicies = Callable[..., Policies]
type MakeUser = Callable[..., User]


@pytest.fixture
def make_entity_revision() -> MakeEntityRevision:
    datetime_ = datetime(year=2026, month=1, day=1, tzinfo=UTC)

    def entity_revision[Entity_: Entity[UUID]](
        *,
        entity: Entity_,
        fetched_at: datetime | None = None,
        merged_at: datetime | None = None,
        provider: str = "test_provider",
    ) -> EntityRevision[Entity_]:
        return EntityRevision(
            entity=entity,
            fetched_at=fetched_at if fetched_at is not None else datetime_,
            merged_at=merged_at,
            provider=provider,
        )

    return entity_revision


@pytest.fixture
def make_entity_record() -> MakeEntityRecord:
    datetime_ = datetime(year=2026, month=1, day=1, tzinfo=UTC)

    def entity_record(
        *,
        entity_id: UUID | None = None,
        entity_ref: EntityRef | None = None,
        outcome: ConsumptionOutcome = "expanded",
        provider: str = "test_provider",
        requested_at: datetime | None = None,
        username: str = "alice",
    ) -> EntityRecord:
        return EntityRecord(
            id=uuid4(),
            entity_id=entity_id if entity_id is not None else uuid4(),
            entity_ref=entity_ref,
            outcome=outcome,
            provider=provider,
            requested_at=requested_at if requested_at is not None else datetime_,
            username=username,
        )

    return entity_record


@pytest.fixture
def make_policies() -> MakePolicies:

    def policies(
        *,
        revision_merge_policy: RevisionMergePolicy,
        revision_selection_policy: RevisionSelectionPolicy,
    ) -> Policies:
        return Policies(
            revision_merge_policy=revision_merge_policy,
            revision_selection_policy=revision_selection_policy,
        )

    return policies


@pytest.fixture
def make_external_credential() -> MakeExternalCredential:

    def external_credential(
        *,
        api_key: str | None = None,
        provider: Provider = Provider.PORTAL_TRANSPARENCIA,
        username: str | None = None,
    ) -> ExternalCredential:
        return ExternalCredential(
            api_key=api_key if api_key is not None else str(uuid4()),
            provider=provider,
            username=username if username is not None else str(uuid4()),
        )

    return external_credential


@pytest.fixture
def make_user() -> MakeUser:

    def user(
        *,
        username: str | None = None,
        hashed_password: str | None = None,
    ) -> User:
        return User(
            username=username if username is not None else str(uuid4()),
            hashed_password=hashed_password
            if hashed_password is not None
            else str(uuid4()),
        )

    return user


@pytest.fixture
def policies(make_policies: MakePolicies) -> Policies:

    return make_policies(
        revision_merge_policy=keep_incoming_policy,
        revision_selection_policy=select_current_by_newest_fetched,
    )
