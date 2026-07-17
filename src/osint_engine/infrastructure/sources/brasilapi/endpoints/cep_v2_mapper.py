from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.domain.entities.nodes.address import Address

if TYPE_CHECKING:
    from osint_engine.infrastructure.sources.payload import Payload


def map_address(*, payload: Payload, number: str) -> Address:
    return Address(
        cep=payload.require(key="cep", expected_type=str),
        city=payload.require(key="city", expected_type=str),
        complement=None,
        neighborhood=payload.require(key="neighborhood", expected_type=str),
        number=number,
        state=payload.require(key="state", expected_type=str),
        street=payload.require(key="street", expected_type=str),
    )
