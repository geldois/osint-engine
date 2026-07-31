from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.interface.http.schemas.text_ingestion_schema import (
    FieldPatternSummarySchema,
    TextPatternSetSchema,
)

if TYPE_CHECKING:
    from osint_engine.domain.value_objects.text_pattern import (
        FieldPattern,
        TextPatternSet,
    )


def _field_pattern_to_schema(
    *, field_pattern: FieldPattern
) -> FieldPatternSummarySchema:
    return FieldPatternSummarySchema(
        node_type=field_pattern.node_type.__name__,
        fields=sorted(field_pattern.node_type.id_fields),
    )


def text_pattern_set_to_schema(*, pattern_set: TextPatternSet) -> TextPatternSetSchema:
    return TextPatternSetSchema(
        id=pattern_set.id,
        patterns=[
            _field_pattern_to_schema(field_pattern=field_pattern)
            for field_pattern in pattern_set.patterns
        ],
    )
