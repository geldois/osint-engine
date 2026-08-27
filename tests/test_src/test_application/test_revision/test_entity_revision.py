from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from osint_engine.application.errors.revision_error import (
    EmptyProviderError,
    NonUTCAttributeError,
)
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.value_objects.entity_ref import EntityRef
from tests.fakes.domain import FakeNode

_NODE = FakeNode(content="entity-revision-subject")
_OTHER_NODE = FakeNode(content="other-entity")
_PERSON = Person(
    age_range="31 a 40 anos",
    birthdate="1990-01-01",
    cpf="123.456.789-09",
    name="João Silva",
    registration_date="2010-05-20",
    registration_status="REGULAR",
)

_UTC = datetime(2026, 1, 1, tzinfo=UTC)
_LATER_UTC = datetime(2026, 6, 1, tzinfo=UTC)
_NAIVE = datetime(2026, 1, 1)  # noqa: DTZ001
_OFFSET = datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=-3)))
_ZONEINFO_UTC = datetime(2026, 1, 1, tzinfo=ZoneInfo("UTC"))


class TestEntityRevisionFetchedAtUTCInvariant:
    def test_accepts_the_utc_singleton(self) -> None:
        revision = EntityRevision(
            entity=_NODE, fetched_at=_UTC, merged_at=None, provider="test_provider"
        )

        assert revision.fetched_at is _UTC

    @pytest.mark.parametrize("non_utc", [_NAIVE, _OFFSET], ids=["naive", "offset"])
    def test_rejects_naive_or_offset(self, non_utc: datetime) -> None:
        with pytest.raises(NonUTCAttributeError) as exception:
            EntityRevision(
                entity=_NODE,
                fetched_at=non_utc,
                merged_at=None,
                provider="test_provider",
            )

        assert exception.value.attribute == "fetched_at"

    def test_rejects_utc_equivalent_zone_that_is_not_the_utc_singleton(self) -> None:
        with pytest.raises(NonUTCAttributeError) as exception:
            EntityRevision(
                entity=_NODE,
                fetched_at=_ZONEINFO_UTC,
                merged_at=None,
                provider="test_provider",
            )

        assert exception.value.attribute == "fetched_at"


class TestEntityRevisionMergedAtUTCInvariant:
    def test_accepts_none_as_the_unmerged_state(self) -> None:
        revision = EntityRevision(
            entity=_NODE, fetched_at=_UTC, merged_at=None, provider="test_provider"
        )

        assert revision.merged_at is None

    def test_accepts_the_utc_singleton(self) -> None:
        revision = EntityRevision(
            entity=_NODE,
            fetched_at=_UTC,
            merged_at=_LATER_UTC,
            provider="test_provider",
        )

        assert revision.merged_at is _LATER_UTC

    @pytest.mark.parametrize(
        "non_utc",
        [_NAIVE, _OFFSET, _ZONEINFO_UTC],
        ids=["naive", "offset", "utc_equivalent_zone"],
    )
    def test_rejects_non_utc(self, non_utc: datetime) -> None:
        with pytest.raises(NonUTCAttributeError) as exception:
            EntityRevision(
                entity=_NODE,
                fetched_at=_UTC,
                merged_at=non_utc,
                provider="test_provider",
            )

        assert exception.value.attribute == "merged_at"


class TestEntityRevisionSourceInvariant:
    @pytest.mark.parametrize(
        "empty_source", ["", "   ", "\t\n"], ids=["empty", "spaces", "whitespace"]
    )
    def test_rejects_empty_or_whitespace_only_provider(self, empty_source: str) -> None:
        with pytest.raises(EmptyProviderError):
            EntityRevision(
                entity=_NODE, fetched_at=_UTC, merged_at=None, provider=empty_source
            )

    def test_accepts_a_non_empty_provider(self) -> None:
        revision = EntityRevision(
            entity=_NODE,
            fetched_at=_UTC,
            merged_at=None,
            provider="portal_transparencia",
        )

        assert revision.provider == "portal_transparencia"


class TestEntityRevisionImmutability:
    @pytest.mark.parametrize("attribute", ["entity", "fetched_at", "merged_at"])
    def test_attributes_cannot_be_rebound(self, attribute: str) -> None:
        revision = EntityRevision(
            entity=_NODE, fetched_at=_UTC, merged_at=None, provider="test_provider"
        )

        with pytest.raises(FrozenInstanceError):
            setattr(revision, attribute, None)


class TestEntityRevisionValueSemantics:
    def test_revisions_with_equal_fields_are_equal_and_hash_alike(self) -> None:
        left = EntityRevision(
            entity=_NODE, fetched_at=_UTC, merged_at=None, provider="test_provider"
        )
        right = EntityRevision(
            entity=_NODE, fetched_at=_UTC, merged_at=None, provider="test_provider"
        )

        assert left == right

        assert hash(left) == hash(right)

        assert len({left, right}) == 1

    def test_differs_by_entity(self) -> None:
        base = EntityRevision(
            entity=_NODE, fetched_at=_UTC, merged_at=None, provider="test_provider"
        )
        other = EntityRevision(
            entity=_OTHER_NODE,
            fetched_at=_UTC,
            merged_at=None,
            provider="test_provider",
        )

        assert base != other

    def test_differs_by_fetched_at(self) -> None:
        base = EntityRevision(
            entity=_NODE, fetched_at=_UTC, merged_at=None, provider="test_provider"
        )
        other = EntityRevision(
            entity=_NODE,
            fetched_at=_LATER_UTC,
            merged_at=None,
            provider="test_provider",
        )

        assert base != other

    def test_differs_by_merged_at(self) -> None:
        base = EntityRevision(
            entity=_NODE, fetched_at=_UTC, merged_at=None, provider="test_provider"
        )
        other = EntityRevision(
            entity=_NODE,
            fetched_at=_UTC,
            merged_at=_LATER_UTC,
            provider="test_provider",
        )

        assert base != other

    def test_differs_by_provider(self) -> None:
        base = EntityRevision(
            entity=_NODE, fetched_at=_UTC, merged_at=None, provider="test_provider"
        )
        other = EntityRevision(
            entity=_NODE, fetched_at=_UTC, merged_at=None, provider="other_source"
        )

        assert base != other


class TestEntityRevisionRef:
    def test_ref_carries_the_entitys_own_id_and_content_id(self) -> None:
        assert _PERSON.id != _PERSON.content_id

        revision = EntityRevision(
            entity=_PERSON, fetched_at=_UTC, merged_at=None, provider="test_provider"
        )

        assert revision.ref == EntityRef(id=_PERSON.id, content_id=_PERSON.content_id)

    def test_ref_never_swaps_id_and_content_id(self) -> None:
        revision = EntityRevision(
            entity=_PERSON, fetched_at=_UTC, merged_at=None, provider="test_provider"
        )

        assert revision.ref.id == _PERSON.id
        assert revision.ref.content_id == _PERSON.content_id
        assert revision.ref.id != revision.ref.content_id

    def test_ref_is_not_a_dataclass_field(self) -> None:
        assert "ref" not in {
            field.name for field in EntityRevision.__dataclass_fields__.values()
        }
