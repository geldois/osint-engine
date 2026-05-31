from dataclasses import dataclass

from src.osint_engine.domain.entity_snapshot import EntitySnapshot


@dataclass(order=True, frozen=True, kw_only=True, slots=True)
class CNAE(EntitySnapshot):
    principal: str
    secondary: set[str] | None
