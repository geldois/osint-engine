from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from osint_engine.application.errors.revision_error import NonUTCAttributeError
from osint_engine.application.revision.entity_revision import EntityRevision
from tests.fakes.domain import FakeNode

_NODE = FakeNode(content="entity-revision-subject")
_OTHER_NODE = FakeNode(content="other-entity")

_UTC = datetime(2026, 1, 1, tzinfo=UTC)
_LATER_UTC = datetime(2026, 6, 1, tzinfo=UTC)
_NAIVE = datetime(2026, 1, 1)  # noqa: DTZ001
_OFFSET = datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=-3)))
_ZONEINFO_UTC = datetime(2026, 1, 1, tzinfo=ZoneInfo("UTC"))


# TESTS


class TestEntityRevisionFetchedAtUTCInvariant:
    def test_accepts_the_utc_singleton(self) -> None:
        revision = EntityRevision(entity=_NODE, fetched_at=_UTC, merged_at=None)

        assert revision.fetched_at is _UTC

    @pytest.mark.parametrize("non_utc", [_NAIVE, _OFFSET], ids=["naive", "offset"])
    def test_rejects_naive_or_offset(self, non_utc: datetime) -> None:
        with pytest.raises(NonUTCAttributeError) as exception:
            EntityRevision(entity=_NODE, fetched_at=non_utc, merged_at=None)

        assert exception.value.attribute == "fetched_at"

    def test_rejects_utc_equivalent_zone_that_is_not_the_utc_singleton(self) -> None:
        with pytest.raises(NonUTCAttributeError) as exception:
            EntityRevision(entity=_NODE, fetched_at=_ZONEINFO_UTC, merged_at=None)

        assert exception.value.attribute == "fetched_at"


class TestEntityRevisionMergedAtUTCInvariant:
    def test_accepts_none_as_the_unmerged_state(self) -> None:
        revision = EntityRevision(entity=_NODE, fetched_at=_UTC, merged_at=None)

        assert revision.merged_at is None

    def test_accepts_the_utc_singleton(self) -> None:
        revision = EntityRevision(entity=_NODE, fetched_at=_UTC, merged_at=_LATER_UTC)

        assert revision.merged_at is _LATER_UTC

    @pytest.mark.parametrize(
        "non_utc",
        [_NAIVE, _OFFSET, _ZONEINFO_UTC],
        ids=["naive", "offset", "utc_equivalent_zone"],
    )
    def test_rejects_non_utc(self, non_utc: datetime) -> None:
        with pytest.raises(NonUTCAttributeError) as exception:
            EntityRevision(entity=_NODE, fetched_at=_UTC, merged_at=non_utc)

        assert exception.value.attribute == "merged_at"


class TestEntityRevisionImmutability:
    @pytest.mark.parametrize("attribute", ["entity", "fetched_at", "merged_at"])
    def test_attributes_cannot_be_rebound(self, attribute: str) -> None:
        revision = EntityRevision(entity=_NODE, fetched_at=_UTC, merged_at=None)

        with pytest.raises(FrozenInstanceError):
            setattr(revision, attribute, None)


class TestEntityRevisionValueSemantics:
    def test_revisions_with_equal_fields_are_equal_and_hash_alike(self) -> None:
        left = EntityRevision(entity=_NODE, fetched_at=_UTC, merged_at=None)
        right = EntityRevision(entity=_NODE, fetched_at=_UTC, merged_at=None)

        assert left == right

        assert hash(left) == hash(right)

        assert len({left, right}) == 1

    def test_differs_by_entity(self) -> None:
        base = EntityRevision(entity=_NODE, fetched_at=_UTC, merged_at=None)
        other = EntityRevision(entity=_OTHER_NODE, fetched_at=_UTC, merged_at=None)

        assert base != other

    def test_differs_by_fetched_at(self) -> None:
        base = EntityRevision(entity=_NODE, fetched_at=_UTC, merged_at=None)
        other = EntityRevision(entity=_NODE, fetched_at=_LATER_UTC, merged_at=None)

        assert base != other

    def test_differs_by_merged_at(self) -> None:
        base = EntityRevision(entity=_NODE, fetched_at=_UTC, merged_at=None)
        other = EntityRevision(entity=_NODE, fetched_at=_UTC, merged_at=_LATER_UTC)

        assert base != other
