from __future__ import annotations

import pytest

from osint_engine.interface.errors.interface_error import InterfaceError

# TEST DOUBLES


class FakeInterfaceError(InterfaceError, error_code="TEST"):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)

    def _build_message(self) -> str:
        return "test"


# TESTS


class TestInterfaceErrorSubclassContract:
    def test_raises_when_it_becomes_concrete_without_error_code(self) -> None:
        with pytest.raises(TypeError) as exception:

            class FakeConcreteInterfaceErrorWithoutErrorCodeError(  # pyright: ignore[reportUnusedClass]
                InterfaceError, error_code=None
            ):
                def __init__(self, **kwargs: object) -> None:
                    super().__init__(**kwargs)

                def _build_message(self) -> str:
                    return "test"

        assert "FakeConcreteInterfaceErrorWithoutErrorCodeError" in str(exception.value)

    def test_allows_an_abstract_intermediate_subclass_to_omit_error_code(
        self,
    ) -> None:
        class FakeAbstractInterfaceError(  # pyright: ignore[reportUnusedClass]
            InterfaceError, error_code=None
        ): ...

        # no TypeError raised above: an abstract subclass (no __init__/
        # _build_message override) is allowed to leave error_code unset.

    def test_concrete_subclass_with_error_code_exposes_it_as_class_attribute(
        self,
    ) -> None:
        assert FakeInterfaceError.error_code == "TEST"
