from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from osint_engine.domain.errors.text_pattern_error import FieldPatternGroupMismatchError

if TYPE_CHECKING:
    import re
    from collections.abc import Mapping
    from uuid import UUID

    from osint_engine.domain.entities.bases.node import Node
    from osint_engine.domain.value_objects.pattern_set_id import PatternSetID


@dataclass(frozen=True, kw_only=True)
class FieldPattern:
    node_type: type[Node[UUID]]
    regex: re.Pattern[str]
    checksum_validators: Mapping[str, Callable[[str], bool]] = field(
        default_factory=dict[str, Callable[[str], bool]]
    )

    def __post_init__(self) -> None:
        actual = frozenset(self.regex.groupindex)

        if actual != self.node_type.id_fields:
            raise FieldPatternGroupMismatchError(
                node_type=self.node_type,
                expected=self.node_type.id_fields,
                actual=actual,
            )


@dataclass(frozen=True, kw_only=True)
class TextPatternSet:
    id: PatternSetID
    patterns: tuple[FieldPattern, ...]
