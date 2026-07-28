from __future__ import annotations

from osint_engine.interface.errors.sanitization_error import (
    InvalidCNPJError,
    InvalidCPFError,
    InvalidCPFOrCNPJError,
)


def _digits_only(value: str, /) -> str:
    return "".join(char for char in value if char.isdecimal())


def sanitize_cnpj(cnpj: str, /) -> str:
    sanitized = _digits_only(cnpj)
    cnpj_len = 14

    if len(sanitized) != cnpj_len:
        raise InvalidCNPJError(input_value=cnpj, digit_count=len(sanitized))

    return sanitized


def sanitize_cpf(cpf: str, /) -> str:
    sanitized = _digits_only(cpf)
    cpf_len = 11

    if len(sanitized) != cpf_len:
        raise InvalidCPFError(input_value=cpf, digit_count=len(sanitized))

    return sanitized


def sanitize_cpf_or_cnpj(cpf_or_cnpj: str, /) -> str:
    sanitized = _digits_only(cpf_or_cnpj)
    cpf_len = 11
    cnpj_len = 14

    if len(sanitized) not in (cpf_len, cnpj_len):
        raise InvalidCPFOrCNPJError(input_value=cpf_or_cnpj, digit_count=len(sanitized))

    return sanitized
