from __future__ import annotations

from os import environ
from pathlib import Path


def load_dotenv() -> None:
    path = Path(".env")

    if not path.exists():
        return

    with path.open(encoding="utf-8") as file:
        for line in file:
            ln = line.strip()

            if not ln or ln.startswith("#") or "=" not in ln:
                continue

            k, _, v = ln.partition("=")

            if not k or not (k[0].isalpha() or k[0] == "_"):
                continue

            k = k.strip().upper()
            v = v.strip()

            environ.setdefault(key=k, value=v)
