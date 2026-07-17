from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.domain.entities.nodes.address import Address
from osint_engine.infrastructure.sources.brasilapi.endpoints.cep_v2_mapper import (
    map_address,
)
from tests.data.brasilapi import CEP_DATA, NUMBER

if TYPE_CHECKING:
    from osint_engine.infrastructure.sources.payload import Payload
    from tests.test_infrastructure.test_sources.conftest import MakePayload


class TestMapAddress:
    def test_maps_field_values_from_payload(self, make_payload: MakePayload) -> None:
        address = map_address(
            payload=make_payload(source="brasilapi", data=CEP_DATA), number=NUMBER
        )

        assert isinstance(address, Address)

        assert address.cep == "70040912"

        assert address.city == "Brasília"

        assert address.neighborhood == "Asa Norte"

        assert address.state == "DF"

        assert address.street == "SAUN Quadra 5 Lote B Torres I, II e III"

    def test_number_comes_from_the_external_parameter_not_the_payload(
        self, make_payload: MakePayload
    ) -> None:
        address = map_address(
            payload=make_payload(source="brasilapi", data=CEP_DATA), number=NUMBER
        )

        assert address.number == NUMBER

    def test_complement_is_always_none_since_the_source_never_provides_it(
        self, make_payload: MakePayload
    ) -> None:
        address = map_address(
            payload=make_payload(source="brasilapi", data=CEP_DATA), number=NUMBER
        )

        assert address.complement is None


class TestMapAddressWithRealAPISnapshot:
    def test_does_not_raise_with_real_api_snapshot(
        self, brasilapi_cep_v2_valid_payload: Payload
    ) -> None:
        map_address(payload=brasilapi_cep_v2_valid_payload, number=NUMBER)
