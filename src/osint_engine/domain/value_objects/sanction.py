from dataclasses import dataclass
from typing import Literal

from osint_engine.domain.entity_snapshot import EntitySnapshot


@dataclass(order=True, frozen=True, kw_only=True, slots=True)
class Sanction(EntitySnapshot):
    description: str
    source: Literal["CEIS", "CNEP"]
