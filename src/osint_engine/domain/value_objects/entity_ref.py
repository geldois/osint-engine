from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID


@dataclass(eq=True, frozen=True, kw_only=True)
class EntityRef:
    id: UUID
    content_id: UUID
