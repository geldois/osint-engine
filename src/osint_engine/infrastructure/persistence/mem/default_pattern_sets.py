from __future__ import annotations

import re

from osint_engine.domain.entities.nodes.address import Address
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.services.document_checksum import (
    is_valid_cnpj_checksum,
    is_valid_cpf_checksum,
)
from osint_engine.domain.services.normalization import (
    normalize_str_to_digits_only,
)
from osint_engine.domain.value_objects.pattern_set_id import PatternSetID
from osint_engine.domain.value_objects.text_pattern import FieldPattern, TextPatternSet

_CPF_FORMATTED_PATTERN = re.compile(r"(?P<cpf>\d{3}\.\d{3}\.\d{3}-\d{2})")
_CPF_BARE_PATTERN = re.compile(r"CPF\s*[:\-]?\s*(?P<cpf>\d{11})\b", re.IGNORECASE)

_CNPJ_FORMATTED_PATTERN = re.compile(r"(?P<cnpj>\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})")
_CNPJ_BARE_PATTERN = re.compile(r"CNPJ\s*[:\-]?\s*(?P<cnpj>\d{14})\b", re.IGNORECASE)

_CEP_AND_NUMBER_PATTERN = re.compile(
    r"CEP\s*(?P<cep>\d{5}-?\d{3})[^\d.!?\n]{1,40}?n(?:[uú]mero)?[.º°]?\s*"
    r"(?P<number>\d+)",
    re.IGNORECASE,
)


def _checks_cpf(value: str, /) -> bool:
    return is_valid_cpf_checksum(digits=normalize_str_to_digits_only(value=value))


def _checks_cnpj(value: str, /) -> bool:
    return is_valid_cnpj_checksum(digits=normalize_str_to_digits_only(value=value))


BRAZILIAN_DOCUMENT_PATTERNS = TextPatternSet(
    id=PatternSetID("brazilian_documents_v1"),
    patterns=(
        FieldPattern(
            node_type=Person,
            regex=_CPF_FORMATTED_PATTERN,
            checksum_validators={"cpf": _checks_cpf},
        ),
        FieldPattern(
            node_type=Person,
            regex=_CPF_BARE_PATTERN,
            checksum_validators={"cpf": _checks_cpf},
        ),
        FieldPattern(
            node_type=Company,
            regex=_CNPJ_FORMATTED_PATTERN,
            checksum_validators={"cnpj": _checks_cnpj},
        ),
        FieldPattern(
            node_type=Company,
            regex=_CNPJ_BARE_PATTERN,
            checksum_validators={"cnpj": _checks_cnpj},
        ),
        FieldPattern(node_type=Address, regex=_CEP_AND_NUMBER_PATTERN),
    ),
)
