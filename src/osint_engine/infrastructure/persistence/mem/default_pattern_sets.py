from __future__ import annotations

from osint_engine.domain.value_objects.pattern_set_id import PatternSetID
from osint_engine.domain.value_objects.text_pattern import (
    TextPatternName,
    TextPatternSet,
)

BRAZILIAN_DOCUMENTS_V1 = TextPatternSet(
    id=PatternSetID("brazilian_documents_v1"),
    patterns=frozenset({TextPatternName.CPF_LOOSE}),
)

DEFAULT_PATTERN_SETS: tuple[TextPatternSet, ...] = (BRAZILIAN_DOCUMENTS_V1,)
