from __future__ import annotations

import pytest

from osint_engine.infrastructure.errors.infrastructure_error import InfrastructureError

# TEST DOUBLES


class FakeInfrastructureError(InfrastructureError, error_code="TEST"):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)

    def _build_message(self) -> str:
        return "test"


# TESTS


class TestInfrastructureErrorSubclassContract:
    def test_raises_when_it_becomes_concrete_without_error_code(self) -> None:
        with pytest.raises(TypeError) as exception:

            class FakeConcreteInfrastructureErrorWithoutErrorCodeError(  # pyright: ignore[reportUnusedClass]
                InfrastructureError, error_code=None
            ):
                def __init__(self, **kwargs: object) -> None:
                    super().__init__(**kwargs)

                def _build_message(self) -> str:
                    return "test"

        assert "FakeConcreteInfrastructureErrorWithoutErrorCodeError" in str(
            exception.value
        )

    def test_allows_an_abstract_intermediate_subclass_to_omit_error_code(
        self,
    ) -> None:
        class FakeAbstractInfrastructureError(  # pyright: ignore[reportUnusedClass]
            InfrastructureError, error_code=None
        ): ...

        # no TypeError raised above: an abstract subclass (no __init__/
        # _build_message override) is allowed to leave error_code unset.

    def test_concrete_subclass_with_error_code_exposes_it_as_class_attribute(
        self,
    ) -> None:
        assert FakeInfrastructureError.error_code == "TEST"
