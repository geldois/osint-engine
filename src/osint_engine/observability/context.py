from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

correlation_id: ContextVar[UUID | None] = ContextVar("correlation_id", default=None)
