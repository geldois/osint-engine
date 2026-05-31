from dataclasses import dataclass

from osint_engine.domain.entities.partner import Partner
from osint_engine.domain.entity_snapshot import EntitySnapshot
from osint_engine.domain.value_objects.address import Address
from osint_engine.domain.value_objects.cnae import CNAE
from osint_engine.domain.value_objects.sanction import Sanction


@dataclass(order=True, frozen=True, kw_only=True, slots=True)
class Company(EntitySnapshot):
    address: Address
    cnae: CNAE
    cnpj: str
    emails: set[str]
    name: str
    partners: set[Partner]
    phones: set[str]
    sanctions: set[Sanction]
    status: str
