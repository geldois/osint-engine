from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest

from osint_engine.application.errors.revision_error import EntityIDMismatchError
from osint_engine.application.revision.policies.revision_merge_policy import (
    merge_by_filled_fields_policy,
)

if TYPE_CHECKING:
    from tests.conftest import (
        MakeEntityRevision,
        MakeFakeMergeableNode,
        MakeFakeNode,
    )


_EARLY = datetime(2026, 1, 1, tzinfo=UTC)
_LATE = datetime(2026, 6, 1, tzinfo=UTC)


# TESTS


class TestMergeIdentityGuard:
    def test_rejects_revisions_of_distinct_entities(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
    ) -> None:
        left = make_entity_revision(entity=make_fake_node(content="a"))
        right = make_entity_revision(entity=make_fake_node(content="b"))

        with pytest.raises(EntityIDMismatchError) as exception:
            merge_by_filled_fields_policy(left, right)

        assert str(left.entity.id) in str(exception.value)

        assert str(right.entity.id) in str(exception.value)


class TestMergeShortCircuit:
    def test_identical_content_returns_the_newest_revision_untouched(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
    ) -> None:
        node = make_fake_node()
        older = make_entity_revision(entity=node, fetched_at=_EARLY)
        newer = make_entity_revision(entity=node, fetched_at=_LATE)

        merged = merge_by_filled_fields_policy(older, newer)

        assert merged is newer

        assert merged.merged_at is None


class TestMergeReconciliation:
    def test_newest_non_null_field_wins(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_mergeable_node: MakeFakeMergeableNode,
    ) -> None:
        older = make_entity_revision(
            entity=make_fake_mergeable_node(key="k", label="stale"),
            fetched_at=_EARLY,
        )
        newer = make_entity_revision(
            entity=make_fake_mergeable_node(key="k", label="fresh"),
            fetched_at=_LATE,
        )

        merged = merge_by_filled_fields_policy(older, newer)

        assert merged.entity.label == "fresh"

    def test_field_null_in_newest_is_filled_from_oldest(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_mergeable_node: MakeFakeMergeableNode,
    ) -> None:
        older = make_entity_revision(
            entity=make_fake_mergeable_node(key="k", label="preserved"),
            fetched_at=_EARLY,
        )
        newer = make_entity_revision(
            entity=make_fake_mergeable_node(key="k", label=None),
            fetched_at=_LATE,
        )

        merged = merge_by_filled_fields_policy(older, newer)

        assert merged.entity.label == "preserved"

        assert merged.entity.key == "k"

    def test_result_carries_newest_fetched_at_and_a_fresh_utc_merged_at(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_mergeable_node: MakeFakeMergeableNode,
    ) -> None:
        older = make_entity_revision(
            entity=make_fake_mergeable_node(key="k", label="a"), fetched_at=_EARLY
        )
        newer = make_entity_revision(
            entity=make_fake_mergeable_node(key="k", label="b"), fetched_at=_LATE
        )

        merged = merge_by_filled_fields_policy(older, newer)

        assert merged.fetched_at == _LATE

        assert merged.merged_at is not None

        assert merged.merged_at.tzinfo is UTC

    def test_reconciliation_is_independent_of_argument_order(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_mergeable_node: MakeFakeMergeableNode,
    ) -> None:
        older = make_entity_revision(
            entity=make_fake_mergeable_node(key="k", label="old"), fetched_at=_EARLY
        )
        newer = make_entity_revision(
            entity=make_fake_mergeable_node(key="k", label=None), fetched_at=_LATE
        )

        left_first = merge_by_filled_fields_policy(older, newer)
        right_first = merge_by_filled_fields_policy(newer, older)

        assert left_first.entity.label == right_first.entity.label == "old"


class TestMergeEqualFetchedAtTiebreak:
    def test_equal_fetched_at_treats_the_left_argument_as_newest(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_mergeable_node: MakeFakeMergeableNode,
    ) -> None:
        left = make_entity_revision(
            entity=make_fake_mergeable_node(key="k", label="left"), fetched_at=_EARLY
        )
        right = make_entity_revision(
            entity=make_fake_mergeable_node(key="k", label="right"), fetched_at=_EARLY
        )

        merged = merge_by_filled_fields_policy(left, right)

        assert merged.entity.label == "left"
