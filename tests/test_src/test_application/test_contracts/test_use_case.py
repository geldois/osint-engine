from __future__ import annotations

import importlib
import pkgutil
from inspect import isabstract

import pytest

from osint_engine.application.contracts.use_case import (
    Query,
    UseCase,
    UseCaseBilling,
    UseCaseRegistry,
)
from osint_engine.application.errors.use_case_registry_error import (
    DuplicateUseCaseRegistrationError,
    UnregisteredUseCaseError,
)
from osint_engine.application.use_cases import expansion as expansion_package
from osint_engine.application.use_cases.expansion.expand_by_cpf_batch import (
    EstimateCPFBatch,
    ExpandByCPFBatch,
)

_NOT_SELF_REGISTERING = frozenset({ExpandByCPFBatch, EstimateCPFBatch})


def _concrete_expansion_use_cases() -> list[type[UseCase[object]]]:
    for module_info in pkgutil.iter_modules(
        expansion_package.__path__, prefix=f"{expansion_package.__name__}."
    ):
        importlib.import_module(module_info.name)

    result: list[type[UseCase[object]]] = []

    def _walk(*, base: type) -> None:
        for cls in base.__subclasses__():
            if (
                not isabstract(cls)
                and cls.__module__.startswith(expansion_package.__name__)
                and cls not in _NOT_SELF_REGISTERING
            ):
                result.append(cls)

            _walk(base=cls)

    _walk(base=UseCase)

    return result


class TestUseCaseRegistry:
    def test_billing_for_returns_what_was_registered(self) -> None:
        class FakeUseCase(Query[None]):
            def __init__(self, **kwargs: object) -> None:
                super().__init__(**kwargs)

            async def execute(self) -> None:
                return None

        UseCaseRegistry.register(FakeUseCase, provider="fake", billable=True)

        billing = UseCaseRegistry.billing_for(FakeUseCase)

        assert billing == UseCaseBilling(provider="fake", billable=True)

    def test_billing_for_raises_when_never_registered(self) -> None:
        class FakeUnregisteredUseCase(Query[None]):
            def __init__(self, **kwargs: object) -> None:
                super().__init__(**kwargs)

            async def execute(self) -> None:
                return None

        with pytest.raises(UnregisteredUseCaseError) as exception:
            UseCaseRegistry.billing_for(FakeUnregisteredUseCase)

        assert exception.value.subject is FakeUnregisteredUseCase

    def test_register_raises_on_a_second_registration_of_the_same_use_case(
        self,
    ) -> None:
        class FakeDuplicateUseCase(Query[None]):
            def __init__(self, **kwargs: object) -> None:
                super().__init__(**kwargs)

            async def execute(self) -> None:
                return None

        UseCaseRegistry.register(FakeDuplicateUseCase, provider="dup", billable=False)

        with pytest.raises(DuplicateUseCaseRegistrationError) as exception:
            UseCaseRegistry.register(
                FakeDuplicateUseCase, provider="dup-again", billable=True
            )

        assert exception.value.subject is FakeDuplicateUseCase
        assert exception.value.existing == UseCaseBilling(
            provider="dup", billable=False
        )

    def test_registering_two_distinct_use_cases_does_not_collide(self) -> None:
        class FakeFirstUseCase(Query[None]):
            def __init__(self, **kwargs: object) -> None:
                super().__init__(**kwargs)

            async def execute(self) -> None:
                return None

        class FakeSecondUseCase(Query[None]):
            def __init__(self, **kwargs: object) -> None:
                super().__init__(**kwargs)

            async def execute(self) -> None:
                return None

        UseCaseRegistry.register(FakeFirstUseCase, provider="first", billable=False)
        UseCaseRegistry.register(FakeSecondUseCase, provider="second", billable=True)

        assert UseCaseRegistry.billing_for(FakeFirstUseCase) == UseCaseBilling(
            provider="first", billable=False
        )
        assert UseCaseRegistry.billing_for(FakeSecondUseCase) == UseCaseBilling(
            provider="second", billable=True
        )


class TestUseCaseRegistryCompleteness:
    @pytest.mark.parametrize("use_case_class", _concrete_expansion_use_cases())
    def test_every_expansion_use_case_is_registered(
        self, use_case_class: type[UseCase[object]]
    ) -> None:
        UseCaseRegistry.billing_for(use_case_class)
