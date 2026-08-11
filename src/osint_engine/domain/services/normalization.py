from __future__ import annotations

import re

_NO_NUMBER_TOKENS = frozenset({"SN", "SEMNUMERO", "SEMNÚMERO"})
_NO_NUMBER_CANONICAL = "S/N"

_LEADING_DIGITS_PATTERN = re.compile(r"^0*(\d+)(.*)$")
_SUFFIX_SEPARATORS_PATTERN = re.compile(r"[\s\-/.]+")
_NON_DIGIT_OR_MASK_PATTERN = re.compile(r"[^\d*]")


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


def normalize_masked_document(*, value: str) -> str:
    return _NON_DIGIT_OR_MASK_PATTERN.sub("", value)
