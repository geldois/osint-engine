from __future__ import annotations

from datetime import datetime  # noqa: TC003

from pydantic import BaseModel


class RevisionSchema(BaseModel):
    fetched_at: datetime
    merged_at: datetime | None
    provider: str
