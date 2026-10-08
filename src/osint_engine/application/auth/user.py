from __future__ import annotations

from dataclasses import dataclass


@dataclass(eq=True, frozen=True, kw_only=True)
class User:
    hashed_password: str
    username: str
