import pytest

from osint_engine.domain.errors.domain_error import (
    DomainError,
    MissingErrorIdentityContractError,
)


class FakeDomainError(DomainError, error_code=None):
    def __init__(self) -> None:
        super().__init__()

    def _build_message(self) -> str:
        return "test"


# INVALID CASES


def test_domain_error_raises_when_is_intantiated_with_none_error_code() -> None:
    with pytest.raises(MissingErrorIdentityContractError):
        FakeDomainError()
