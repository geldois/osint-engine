from __future__ import annotations

import time
from typing import override

from osint_engine.application.contracts.hashers.password_hasher import PasswordHasher


class RecordingPasswordHasher(PasswordHasher):
    def __init__(self, *, events: list[str], block_seconds: float) -> None:
        self.events = events
        self.block_seconds = block_seconds

    @override
    def hash_(self, *, password: str) -> str:
        self.events.append("hash:start")
        time.sleep(self.block_seconds)
        self.events.append("hash:end")

        return f"hashed:{password}"

    @override
    def verify(self, *, hash_: str | None, password: str) -> bool:
        self.events.append("verify:start")
        time.sleep(self.block_seconds)
        self.events.append("verify:end")

        return True
