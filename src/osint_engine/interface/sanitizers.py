from __future__ import annotations

from osint_engine.interface.errors.sanitization_error import InvalidCNPJError


def sanitize_cnpj(cnpj: str, /) -> str:
    sanitized = "".join(char for char in cnpj if char.isdecimal())
    cnpj_len = 14

    if len(sanitized) != cnpj_len:
        raise InvalidCNPJError(input_value=cnpj, digit_count=len(sanitized))

    return sanitized
