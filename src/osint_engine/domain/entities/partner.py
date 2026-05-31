from dataclasses import dataclass

from osint_engine.domain.entity_snapshot import EntitySnapshot
from osint_engine.domain.value_objects.sanction import Sanction


@dataclass(order=True, frozen=True, kw_only=True, slots=True)
class Partner(EntitySnapshot):
    cpf: str
    name: str
    sanctions: set[Sanction]
