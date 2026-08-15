from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from osint_engine.domain.entities.nodes.address import Address
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.errors.text_pattern_error import FieldPatternGroupMismatchError
from osint_engine.domain.services.document_checksum import (
    is_valid_cnpj_checksum,
    is_valid_cpf_checksum,
)
from osint_engine.domain.services.normalization import normalize_str_to_digits_only

if TYPE_CHECKING:
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


def _checks_cpf(value: str, /) -> bool:
    return is_valid_cpf_checksum(digits=normalize_str_to_digits_only(value=value))


def _checks_cnpj(value: str, /) -> bool:
    return is_valid_cnpj_checksum(digits=normalize_str_to_digits_only(value=value))


class TextPatternName(Enum):
    CPF_LOOSE = FieldPattern(
        node_type=Person,
        regex=re.compile(r"\b(?P<cpf>\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})\b"),
        checksum_validators={"cpf": _checks_cpf},
    )
    CPF_LABELED = FieldPattern(
        node_type=Person,
        regex=re.compile(r"CPF\s*[:\-]?\s*(?P<cpf>\d{11})\b", re.IGNORECASE),
        checksum_validators={"cpf": _checks_cpf},
    )
    CNPJ_LOOSE = FieldPattern(
        node_type=Company,
        regex=re.compile(r"\b(?P<cnpj>\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{14})\b"),
        checksum_validators={"cnpj": _checks_cnpj},
    )
    CNPJ_LABELED = FieldPattern(
        node_type=Company,
        regex=re.compile(r"CNPJ\s*[:\-]?\s*(?P<cnpj>\d{14})\b", re.IGNORECASE),
        checksum_validators={"cnpj": _checks_cnpj},
    )
    CEP_AND_NUMBER = FieldPattern(
        node_type=Address,
        regex=re.compile(
            r"CEP\s*(?P<cep>\d{5}-?\d{3})[^\d.!?\n]{1,40}?n(?:[uú]mero)?[.º°]?\s*"
            r"(?P<number>\d+)",
            re.IGNORECASE,
        ),
    )


@dataclass(frozen=True, kw_only=True)
class TextPatternSet:
    id: PatternSetID
    patterns: frozenset[TextPatternName]
