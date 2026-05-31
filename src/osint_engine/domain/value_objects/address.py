from dataclasses import dataclass

from osint_engine.domain.entity_snapshot import EntitySnapshot


@dataclass(order=True, frozen=True, kw_only=True, slots=True)
class Address(EntitySnapshot):
    cep: str
