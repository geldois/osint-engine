from __future__ import annotations

import re

from osint_engine.domain.errors.document_error import InvalidMaskedDocumentError

_NO_NUMBER_TOKENS = frozenset({"SN", "SEMNUMERO", "SEMNÚMERO"})
_NO_NUMBER_CANONICAL = "S/N"

_LEADING_DIGITS_PATTERN = re.compile(r"^0*(\d+)(.*)$")
_SUFFIX_SEPARATORS_PATTERN = re.compile(r"[\s\-/.]+")
_MASK = "*"
_SEPARATOR_PATTERN = re.compile(r"[\s.\-/]")


def normalize_address_number(*, value: str) -> str:
    cleaned = value.strip().upper()

    bare = _SUFFIX_SEPARATORS_PATTERN.sub("", cleaned).rstrip("º°")

    if not bare or bare in _NO_NUMBER_TOKENS:
        return _NO_NUMBER_CANONICAL

    match = _LEADING_DIGITS_PATTERN.match(cleaned)

    if match is None:
        return _SUFFIX_SEPARATORS_PATTERN.sub("-", cleaned).strip("-")

    digits, rest = match.groups()
    suffix = _SUFFIX_SEPARATORS_PATTERN.sub("", rest)

    return f"{digits}-{suffix}" if suffix else digits


def normalize_str_to_digits_only(*, value: str) -> str:
    return "".join(char for char in value if char.isdigit())


def normalize_masked_document(*, value: str, expected_length: int = 11) -> str:
    cleaned = _SEPARATOR_PATTERN.sub("", value)

    if any(char != _MASK and not char.isdigit() for char in cleaned):
        raise InvalidMaskedDocumentError(
            raw_value=value,
            expected_length=expected_length,
            actual_length=len(cleaned),
        )

    if len(cleaned) != expected_length:
        raise InvalidMaskedDocumentError(
            raw_value=value,
            expected_length=expected_length,
            actual_length=len(cleaned),
        )

    return cleaned
