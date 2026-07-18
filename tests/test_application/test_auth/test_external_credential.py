from __future__ import annotations

import pytest

from osint_engine.application.auth.external_credential import (
    ExternalCredential,
    Provider,
)

# TESTS


class TestExternalCredentialEquality:
    def test_credentials_with_the_same_fields_are_equal(self) -> None:
        credential_a = ExternalCredential(
            api_key="key", provider=Provider.PORTAL_TRANSPARENCIA, username="analyst"
        )
        credential_b = ExternalCredential(
            api_key="key", provider=Provider.PORTAL_TRANSPARENCIA, username="analyst"
        )

        assert credential_a == credential_b

    def test_credentials_with_different_api_keys_are_not_equal(self) -> None:
        credential_a = ExternalCredential(
            api_key="key-a", provider=Provider.PORTAL_TRANSPARENCIA, username="analyst"
        )
        credential_b = ExternalCredential(
            api_key="key-b", provider=Provider.PORTAL_TRANSPARENCIA, username="analyst"
        )

        assert credential_a != credential_b


class TestExternalCredentialImmutability:
    def test_fields_cannot_be_reassigned(self) -> None:
        credential = ExternalCredential(
            api_key="key", provider=Provider.PORTAL_TRANSPARENCIA, username="analyst"
        )

        with pytest.raises(AttributeError):
            credential.api_key = "other-key"  # pyright: ignore[reportAttributeAccessIssue]


class TestProvider:
    def test_portal_transparencia_value_is_stable_for_storage_and_serialization(
        self,
    ) -> None:
        assert Provider.PORTAL_TRANSPARENCIA == "PORTAL_TRANSPARENCIA"
