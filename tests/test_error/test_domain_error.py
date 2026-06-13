from dataclasses import FrozenInstanceError

import pytest

from osint_engine.domain.errors.domain_error import (
    DomainError,
    MissingErrorIdentityContractError,
)


class FakeDomainError(DomainError, error_code="TEST"):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)

    def _build_message(self) -> str:
        return "test"


# INVALID CASES


def test_domain_error_raises_when_it_becomes_concrete_without_error_code() -> None:
    with pytest.raises(MissingErrorIdentityContractError):

        class FakeConcreteDomainErrorWithoutErrorCodeError(  # pyright: ignore[reportUnusedClass]
            DomainError, error_code=None
        ):
            def __init__(self, **kwargs: object) -> None:
                super().__init__(**kwargs)

            def _build_message(self) -> str:
                return "test"


def test_domain_error_instances_are_immutable() -> None:
    error = FakeDomainError(content="test")

    with pytest.raises(FrozenInstanceError):
        error.content = "testing..."

    with pytest.raises(FrozenInstanceError):
        del error.content
