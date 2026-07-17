from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest

from osint_engine.application.errors.revision_error import EmptyRevisionSelectionError
from osint_engine.application.revision.policies.revision_selection_policy import (
    select_current_by_newest_fetched,
)

if TYPE_CHECKING:
    from tests.conftest import MakeEntityRevision, MakeFakeNode


_EARLY = datetime(2026, 1, 1, tzinfo=UTC)
_LATE = datetime(2026, 6, 1, tzinfo=UTC)
_LATER = datetime(2026, 9, 1, tzinfo=UTC)


# TESTS


class TestSelectionByFetchedAt:
    def test_highest_fetched_at_wins(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
    ) -> None:
        node = make_fake_node()
        older = make_entity_revision(entity=node, fetched_at=_EARLY)
        newer = make_entity_revision(entity=node, fetched_at=_LATE)

        assert select_current_by_newest_fetched([older, newer]) is newer

    def test_single_revision_is_returned(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
    ) -> None:
        only = make_entity_revision(entity=make_fake_node())

        assert select_current_by_newest_fetched([only]) is only


class TestSelectionTiebreak:
    def test_merged_revision_beats_raw_fetch_at_equal_fetched_at(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
    ) -> None:
        node = make_fake_node()
        raw = make_entity_revision(entity=node, fetched_at=_EARLY, merged_at=None)
        merged = make_entity_revision(entity=node, fetched_at=_EARLY, merged_at=_LATE)

        assert select_current_by_newest_fetched([raw, merged]) is merged

    def test_higher_merged_at_wins_among_merged_revisions(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
    ) -> None:
        node = make_fake_node()
        merged_earlier = make_entity_revision(
            entity=node, fetched_at=_EARLY, merged_at=_LATE
        )
        merged_later = make_entity_revision(
            entity=node, fetched_at=_EARLY, merged_at=_LATER
        )

        assert (
            select_current_by_newest_fetched([merged_earlier, merged_later])
            is merged_later
        )


class TestSelectionEmptyInput:
    def test_empty_iterable_raises_semantic_error(self) -> None:
        with pytest.raises(EmptyRevisionSelectionError):
            select_current_by_newest_fetched([])
