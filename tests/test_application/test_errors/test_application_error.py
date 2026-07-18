from __future__ import annotations

import pytest

from osint_engine.application.errors.application_error import ApplicationError

# TEST DOUBLES


class FakeApplicationError(ApplicationError, error_code="TEST"):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)

    def _build_message(self) -> str:
        return "test"


# TESTS


class TestApplicationErrorSubclassContract:
    def test_raises_when_it_becomes_concrete_without_error_code(self) -> None:
        with pytest.raises(TypeError) as exception:

            class FakeConcreteApplicationErrorWithoutErrorCodeError(  # pyright: ignore[reportUnusedClass]
                ApplicationError, error_code=None
            ):
                def __init__(self, **kwargs: object) -> None:
                    super().__init__(**kwargs)

                def _build_message(self) -> str:
                    return "test"

        assert "FakeConcreteApplicationErrorWithoutErrorCodeError" in str(
            exception.value
        )

    def test_allows_an_abstract_intermediate_subclass_to_omit_error_code(
        self,
    ) -> None:
        class FakeAbstractApplicationError(  # pyright: ignore[reportUnusedClass]
            ApplicationError, error_code=None
        ): ...

        # no TypeError raised above: an abstract subclass (no __init__/
        # _build_message override) is allowed to leave error_code unset.

    def test_concrete_subclass_with_error_code_exposes_it_as_class_attribute(
        self,
    ) -> None:
        assert FakeApplicationError.error_code == "TEST"
