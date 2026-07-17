from __future__ import annotations


def digits_only(*, value: str) -> str:
    return "".join(char for char in value if char.isdigit())
