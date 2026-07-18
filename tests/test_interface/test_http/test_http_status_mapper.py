from __future__ import annotations

from typing import override
from uuid import uuid4

import pytest

from osint_engine.application.errors.auth_error import InvalidCredentialsError
from osint_engine.application.errors.revision_error import EmptyRevisionSelectionError
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.errors.domain_error import MissingErrorIdentityContractError
from osint_engine.domain.errors.edge_error import EdgeSelfLoopError
from osint_engine.domain.errors.entity_error import (
    EntityInvalidIdentifierError,
    EntityNotFoundError,
)
from osint_engine.domain.errors.graph_error import (
    GraphHasNoNodesError,
    GraphInconsistentError,
    GraphRootNotInNodesError,
)
from osint_engine.infrastructure.errors.data_source_error import (
    DataSourceError,
    UnexpectedFieldFormatError,
    UnexpectedFieldTypeError,
    UnexpectedPayloadError,
)
from osint_engine.infrastructure.errors.token_error import InvalidTokenError, TokenError
from osint_engine.infrastructure.errors.uow_error import UoWError
from osint_engine.interface.errors.sanitization_error import InvalidCNPJError
from osint_engine.interface.http.errors.schema_error import UnmappedTypeSchemaError
from osint_engine.interface.http.mappers.http_status_mapper import map_status_from_error

# TEST DOUBLES


class _ConcreteTokenError(TokenError, error_code="TEST_TOKEN_ERROR"):
    @override
    def __init__(self) -> None:
        super().__init__()

    @override
    def _build_message(self) -> str:
        return "token error"


class _ConcreteDataSourceError(DataSourceError, error_code="TEST_DATA_SOURCE_ERROR"):
    @override
    def __init__(self) -> None:
        super().__init__()

    @override
    def _build_message(self) -> str:
        return "data source error"


class _ConcreteUoWError(UoWError, error_code="TEST_UOW_ERROR"):
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
            pytest.param(
                EntityNotFoundError(entity_id=uuid4(), subject=Company),
                404,
                id="EntityNotFoundError→404",
            ),
            pytest.param(
                InvalidCredentialsError(username="user"),
                401,
                id="InvalidCredentialsError→401",
            ),
            pytest.param(
                InvalidTokenError(detail="expired"), 401, id="InvalidTokenError→401"
            ),
            pytest.param(_ConcreteTokenError(), 401, id="TokenError(catch-all)→401"),
            pytest.param(
                InvalidCNPJError(input_value="000", digit_count=3),
                422,
                id="SanitizationError(InvalidCNPJError)→422",
            ),
            pytest.param(GraphHasNoNodesError(), 422, id="GraphHasNoNodesError→422"),
            pytest.param(
                GraphRootNotInNodesError(root_id=uuid4()),
                422,
                id="GraphRootNotInNodesError→422",
            ),
            pytest.param(
                UnexpectedFieldTypeError(
                    source="api", key="cnpj", expected_type=str, field_type=int
                ),
                500,
                id="UnexpectedFieldTypeError→500",
            ),
            pytest.param(
                UnexpectedPayloadError(source="api", missing_field="cnpj"),
                500,
                id="UnexpectedPayloadError→500",
            ),
            pytest.param(
                UnexpectedFieldFormatError(
                    source="api",
                    key="valorMulta",
                    raw_value="not-a-number",
                    reason="not a valid pt-BR monetary amount",
                ),
                500,
                id="UnexpectedFieldFormatError→500",
            ),
            pytest.param(
                EntityInvalidIdentifierError(
                    subject=Company,
                    field="cnpj",
                    raw_value="123",
                    expected_length=14,
                    actual_length=3,
                ),
                422,
                id="EntityInvalidIdentifierError→422",
            ),
            pytest.param(
                EdgeSelfLoopError(node_id=uuid4()), 422, id="EdgeSelfLoopError→422"
            ),
            pytest.param(
                EmptyRevisionSelectionError(),
                422,
                id="RevisionError(catch-all)→422",
            ),
            pytest.param(
                _ConcreteDataSourceError(), 502, id="DataSourceError(catch-all)→502"
            ),
            pytest.param(
                GraphInconsistentError(), 500, id="EntityError(catch-all)→500"
            ),
            pytest.param(
                UnmappedTypeSchemaError(subject=str),
                500,
                id="SchemaError(catch-all)→500",
            ),
            pytest.param(_ConcreteUoWError(), 500, id="UoWError(catch-all)→500"),
            pytest.param(
                MissingErrorIdentityContractError(subject=GraphHasNoNodesError),
                422,
                id="DomainError(catch-all)→422",
            ),
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
