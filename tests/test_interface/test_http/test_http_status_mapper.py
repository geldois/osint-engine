from __future__ import annotations

from typing import override
from uuid import uuid4

import pytest

from osint_engine.application.errors.auth_error import InvalidCredentialsError
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.errors.domain_error import MissingErrorIdentityContractError
from osint_engine.domain.errors.entity_error import EntityNotFoundError
from osint_engine.domain.errors.graph_error import (
    GraphHasNoNodesError,
    GraphInconsistentError,
    GraphRootNotInNodesError,
)
from osint_engine.infrastructure.errors.data_source_error import (
    DataSourceError,
    UnexpectedFieldTypeError,
    UnexpectedPayloadError,
)
from osint_engine.infrastructure.errors.token_error import InvalidTokenError
from osint_engine.infrastructure.errors.uow_error import UoWError
from osint_engine.interface.errors.sanitization_error import InvalidCNPJError
from osint_engine.interface.http.errors.schema_error import UnmappedTypeSchemaError
from osint_engine.interface.http.mappers.http_status_mapper import map_status_from_error

# TEST DOUBLES


class _ConcreteDataSourceError(DataSourceError):
    @override
    def __init__(self) -> None:
        super().__init__()

    @override
    def _build_message(self) -> str:
        return "data source error"


class _ConcreteUoWError(UoWError):
    @override
    def __init__(self) -> None:
        super().__init__()

    @override
    def _build_message(self) -> str:
        return "uow error"


# TESTS


class TestStatusMapping:
    @pytest.mark.parametrize(
        ("exception", "expected_status"),
        [
            (EntityNotFoundError(entity_id=uuid4(), subject=Company), 404),
            (InvalidCredentialsError(username="user"), 401),
            (InvalidTokenError(detail="expired"), 401),
            (InvalidCNPJError(input_value="000", digit_count=3), 422),
            (GraphHasNoNodesError(), 422),
            (GraphRootNotInNodesError(root_id=uuid4()), 422),
            (
                UnexpectedFieldTypeError(
                    source="api", key="cnpj", expected_type=str, field_type=int
                ),
                500,
            ),
            (UnexpectedPayloadError(source="api", missing_field="cnpj"), 500),
            (_ConcreteDataSourceError(), 502),
            (GraphInconsistentError(), 500),
            (UnmappedTypeSchemaError(subject=str), 500),
            (_ConcreteUoWError(), 500),
            (MissingErrorIdentityContractError(), 422),
        ],
        ids=[
            "EntityNotFoundError→404",
            "InvalidCredentialsError→401",
            "InvalidTokenError→401",
            "SanitizationError(InvalidCNPJError)→422",
            "GraphHasNoNodesError→422",
            "GraphRootNotInNodesError→422",
            "UnexpectedFieldTypeError→500",
            "UnexpectedPayloadError→500",
            "DataSourceError(catch-all)→502",
            "EntityError(catch-all)→500",
            "SchemaError(catch-all)→500",
            "UoWError(catch-all)→500",
            "DomainError(catch-all)→422",
        ],
    )
    def test_maps_exception_to_correct_http_status(
        self, exception: Exception, expected_status: int
    ) -> None:
        assert map_status_from_error(exception) == expected_status


class TestUnknownExceptionFallback:
    def test_unregistered_exception_type_returns_500(self) -> None:
        assert map_status_from_error(Exception("unexpected")) == 500

    def test_stdlib_exception_returns_500(self) -> None:
        assert map_status_from_error(ValueError("bad value")) == 500
