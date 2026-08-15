from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.domain.entities.bases.node import Node
    from osint_engine.domain.value_objects.text_pattern import TextPatternName


@dataclass(frozen=True, kw_only=True)
class ExtractedMatch:
    node_type: type[Node[UUID]]
    field_values: tuple[tuple[str, str], ...]
    matched_field: str
    pattern_name: TextPatternName


def extract_matches(
    *, text: str, pattern_names: frozenset[TextPatternName]
) -> frozenset[ExtractedMatch]:

    matches: set[ExtractedMatch] = set()

    for pattern_name in pattern_names:
        field_pattern = pattern_name.value
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
                    pattern_name=pattern_name,
                )
            )

    return frozenset(matches)
