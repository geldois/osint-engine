from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.domain.entities.bases.node import Node
    from osint_engine.domain.value_objects.text_pattern import TextPatternSet


@dataclass(frozen=True, kw_only=True)
class ExtractedMatch:
    node_type: type[Node[UUID]]
    field_values: tuple[tuple[str, str], ...]
    matched_field: str


def extract_matches(
    *, text: str, pattern_set: TextPatternSet
) -> frozenset[ExtractedMatch]:
    """
    Each pattern in the set is evaluated independently against the whole
    text: every match found becomes an extraction, regardless of whether any
    other pattern in the set matched anything. There is no all-or-nothing
    requirement across the set — that is `IngestText`'s job, which raises
    when the returned frozenset is empty.
    """

    matches: set[ExtractedMatch] = set()

    for field_pattern in pattern_set.patterns:
        for regex_match in field_pattern.regex.finditer(text):
            field_values = regex_match.groupdict()

            if not all(
                validator(field_values[field])
                for field, validator in field_pattern.checksum_validators.items()
            ):
                continue

            matches.add(
                ExtractedMatch(
                    node_type=field_pattern.node_type,
                    field_values=tuple(sorted(field_values.items())),
                    matched_field=",".join(sorted(field_values)),
                )
            )

    return frozenset(matches)
