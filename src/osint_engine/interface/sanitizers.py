from __future__ import annotations

from osint_engine.interface.errors.sanitization_error import (
    InvalidCNPJError,
    InvalidCPFOrCNPJError,
)


def sanitize_cnpj(cnpj: str, /) -> str:
    sanitized = "".join(char for char in cnpj if char.isdecimal())
    cnpj_len = 14

    if len(sanitized) != cnpj_len:
        raise InvalidCNPJError(input_value=cnpj, digit_count=len(sanitized))

    return sanitized


def sanitize_cpf_or_cnpj(cpf_or_cnpj: str, /) -> str:
    sanitized = "".join(char for char in cpf_or_cnpj if char.isdecimal())
    cpf_len = 11
    cnpj_len = 14

    if len(sanitized) not in (cpf_len, cnpj_len):
        raise InvalidCPFOrCNPJError(input_value=cpf_or_cnpj, digit_count=len(sanitized))

    return sanitized
