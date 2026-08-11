from __future__ import annotations

_CPF_LENGTH = 11
_CNPJ_LENGTH = 14
_CYCLE = (2, 3, 4, 5, 6, 7, 8, 9)
_REMAINDER_FLOOR = 2
_MODULUS = 11


def _digit_from_remainder(*, remainder: int) -> int:
    return 0 if remainder < _REMAINDER_FLOOR else _MODULUS - remainder


def _cpf_check_digit(*, base: str) -> int:
    weights = range(len(base) + 1, 1, -1)
    total = sum(
        int(digit) * weight for digit, weight in zip(base, weights, strict=True)
    )

    return _digit_from_remainder(remainder=total % _MODULUS)


def _cnpj_check_digit(*, base: str) -> int:
    weights = [
        _CYCLE[(len(base) - 1 - index) % len(_CYCLE)] for index in range(len(base))
    ]
    total = sum(
        int(digit) * weight for digit, weight in zip(base, weights, strict=True)
    )

    return _digit_from_remainder(remainder=total % _MODULUS)


def is_valid_cpf_checksum(*, digits: str) -> bool:
    if len(digits) != _CPF_LENGTH or not digits.isdigit() or len(set(digits)) == 1:
        return False

    first = _cpf_check_digit(base=digits[:9])
    second = _cpf_check_digit(base=digits[:9] + str(first))

    return digits[9:] == f"{first}{second}"


def is_valid_cnpj_checksum(*, digits: str) -> bool:
    if len(digits) != _CNPJ_LENGTH or not digits.isdigit() or len(set(digits)) == 1:
        return False

    first = _cnpj_check_digit(base=digits[:12])
    second = _cnpj_check_digit(base=digits[:12] + str(first))

    return digits[12:] == f"{first}{second}"
