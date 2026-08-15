from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.interface.http.schemas.text_ingestion_schema import (
    TextPatternCatalogSchema,
    TextPatternNameSchema,
    TextPatternSetSchema,
)

if TYPE_CHECKING:
    from osint_engine.domain.value_objects.text_pattern import (
        TextPatternName,
        TextPatternSet,
    )


def _text_pattern_name_to_schema(
    *, pattern_name: TextPatternName
) -> TextPatternNameSchema:
    field_pattern = pattern_name.value

    return TextPatternNameSchema(
        name=pattern_name.name,
        node_type=field_pattern.node_type.__name__,
        fields=sorted(field_pattern.node_type.id_fields),
    )


def _text_pattern_set_to_schema(*, pattern_set: TextPatternSet) -> TextPatternSetSchema:
    return TextPatternSetSchema(
        id=pattern_set.id,
        pattern_names=sorted(
            pattern_name.name for pattern_name in pattern_set.patterns
        ),
    )


def text_pattern_catalog_to_schema(
    *, patterns: tuple[TextPatternName, ...], bundles: tuple[TextPatternSet, ...]
) -> TextPatternCatalogSchema:
    return TextPatternCatalogSchema(
        patterns=[
            _text_pattern_name_to_schema(pattern_name=pattern_name)
            for pattern_name in patterns
        ],
        bundles=[
            _text_pattern_set_to_schema(pattern_set=pattern_set)
            for pattern_set in bundles
        ],
    )
