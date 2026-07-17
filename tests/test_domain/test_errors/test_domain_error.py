import pytest

from osint_engine.domain.errors.domain_error import (
    DomainError,
    MissingErrorIdentityContractError,
)

# TEST DOUBLES


class FakeDomainError(DomainError, error_code="TEST"):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)

    def _build_message(self) -> str:
        return "test"


# TESTS


class TestDomainErrorSubclassContract:
    def test_domain_error_raises_when_it_becomes_concrete_without_error_code(
        self,
    ) -> None:
        with pytest.raises(MissingErrorIdentityContractError) as exception:

            class FakeConcreteDomainErrorWithoutErrorCodeError(  # pyright: ignore[reportUnusedClass]
                DomainError, error_code=None
            ):
                def __init__(self, **kwargs: object) -> None:
                    super().__init__(**kwargs)

                def _build_message(self) -> str:
                    return "test"

        assert "FakeConcreteDomainErrorWithoutErrorCodeError" in str(exception.value)
