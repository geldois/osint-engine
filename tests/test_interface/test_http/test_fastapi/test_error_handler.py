from __future__ import annotations

import json
from collections.abc import Callable, Generator
from typing import TYPE_CHECKING, override
from uuid import UUID, uuid4

import pytest
from fastapi import Request
from fastapi.responses import JSONResponse

from osint_engine.application.errors.application_error import ApplicationError
from osint_engine.domain.errors.domain_error import DomainError
from osint_engine.infrastructure.errors.infrastructure_error import (
    InfrastructureError,
)
from osint_engine.infrastructure.errors.token_error import InvalidTokenError
from osint_engine.interface.errors.interface_error import InterfaceError
from osint_engine.interface.errors.sanitization_error import InvalidCNPJError
from osint_engine.interface.http.fastapi import error_handler as error_handler_module
from osint_engine.interface.http.fastapi.error_handler import build_error_handler
from osint_engine.observability.context import correlation_id

if TYPE_CHECKING:
    from tests.test_interface.test_http.test_fastapi.conftest import (
        MakeContainer,
        MakeSettings,
    )

# TEST DOUBLES


class _FakeDomainError(DomainError, error_code="TEST_DOMAIN_ERROR"):
    @override
    def __init__(self) -> None:
        super().__init__()

    @override
    def _build_message(self) -> str:
        return "fake domain error"


class _FakeInterfaceError(InterfaceError, error_code="TEST_INTERFACE_ERROR"):
    @override
    def __init__(self) -> None:
        super().__init__()

    @override
    def _build_message(self) -> str:
        return "fake interface error"


class _FakeApplicationError(ApplicationError, error_code="TEST_APPLICATION_ERROR"):
    @override
    def __init__(self) -> None:
        super().__init__()

    @override
    def _build_message(self) -> str:
        return "fake application error"


class _FakeInfrastructureError(
    InfrastructureError, error_code="TEST_INFRASTRUCTURE_ERROR"
):
    @override
    def __init__(self) -> None:
        super().__init__()

    @override
    def _build_message(self) -> str:
        return "fake infrastructure error"


_REQUEST = Request(
    scope={
        "type": "http",
        "method": "GET",
        "path": "/test",
        "query_string": b"",
        "headers": [],
    }
)

type _HandleError = Callable[[Request, Exception], JSONResponse]
type _MakeHandleError = Callable[..., _HandleError]


def _body(response: JSONResponse) -> dict[str, object]:
    return json.loads(bytes(response.body))


# TESTS


@pytest.fixture(autouse=True)
def _reset_correlation_id() -> Generator[None, None, None]:  # pyright: ignore[reportUnusedFunction]
    token = correlation_id.set(None)

    yield

    correlation_id.reset(token)


@pytest.fixture
def make_handle_error(
    make_container: MakeContainer, make_settings: MakeSettings
) -> _MakeHandleError:
    """
    *,
    debug: bool = False
    """

    def handle_error(*, debug: bool = False) -> _HandleError:
        settings = make_settings(debug=debug)
        container = make_container(settings=settings)

        return build_error_handler(container=container)

    return handle_error


class TestErrorHandlerDetailMasking:
    def test_4xx_exposes_exception_message(
        self, make_handle_error: _MakeHandleError
    ) -> None:
        exception = InvalidCNPJError(input_value="000", digit_count=3)
        data = _body(make_handle_error()(_REQUEST, exception))

        assert data["detail"] == str(exception)

    def test_5xx_returns_opaque_message(
        self, make_handle_error: _MakeHandleError
    ) -> None:
        data = _body(make_handle_error()(_REQUEST, ValueError("boom")))

        assert data["detail"] == "Internal server error"


class TestErrorHandlerHeaders:
    def test_401_includes_www_authenticate_bearer(
        self, make_handle_error: _MakeHandleError
    ) -> None:
        response = make_handle_error()(_REQUEST, InvalidTokenError(detail="expired"))

        assert response.headers.get("WWW-Authenticate") == "Bearer"

    def test_non_401_omits_www_authenticate(
        self, make_handle_error: _MakeHandleError
    ) -> None:
        exception = InvalidCNPJError(input_value="000", digit_count=3)

        assert (
            "WWW-Authenticate" not in make_handle_error()(_REQUEST, exception).headers
        )


class TestErrorHandlerErrorCode:
    def test_domain_error_includes_type_field(
        self, make_handle_error: _MakeHandleError
    ) -> None:
        data = _body(make_handle_error()(_REQUEST, _FakeDomainError()))

        assert data["type"] == "TEST_DOMAIN_ERROR"

    def test_interface_error_includes_type_field(
        self, make_handle_error: _MakeHandleError
    ) -> None:
        data = _body(make_handle_error()(_REQUEST, _FakeInterfaceError()))

        assert data["type"] == "TEST_INTERFACE_ERROR"

    def test_application_error_includes_type_field(
        self, make_handle_error: _MakeHandleError
    ) -> None:
        data = _body(make_handle_error()(_REQUEST, _FakeApplicationError()))

        assert data["type"] == "TEST_APPLICATION_ERROR"

    def test_infrastructure_error_includes_type_field(
        self, make_handle_error: _MakeHandleError
    ) -> None:
        data = _body(make_handle_error()(_REQUEST, _FakeInfrastructureError()))

        assert data["type"] == "TEST_INFRASTRUCTURE_ERROR"

    def test_generic_exception_omits_type_field(
        self, make_handle_error: _MakeHandleError
    ) -> None:
        data = _body(make_handle_error()(_REQUEST, ValueError("boom")))

        assert "type" not in data


class TestErrorHandlerDebugField:
    def test_debug_mode_includes_exc_type(
        self, make_handle_error: _MakeHandleError
    ) -> None:
        data = _body(make_handle_error(debug=True)(_REQUEST, ValueError("boom")))

        debug = data["debug"]

        assert isinstance(debug, dict)

        assert debug["exc_type"] == "ValueError"

    def test_production_mode_omits_debug_field(
        self, make_handle_error: _MakeHandleError
    ) -> None:
        data = _body(make_handle_error(debug=False)(_REQUEST, ValueError("boom")))

        assert "debug" not in data


class TestErrorHandlerLogSeverity:
    def test_5xx_at_server_error_boundary_logs_as_error(
        self,
        make_handle_error: _MakeHandleError,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """HTTP_SERVER_ERROR (500) is the boundary: status < 500 logs info,
        status >= 500 (inclusive) must log error, not info."""

        calls: list[str] = []
        logger = error_handler_module._logger  # pyright: ignore[reportPrivateUsage]

        def record_info(*args: object, **kwargs: object) -> None:  # noqa: ARG001
            calls.append("info")

        def record_error(*args: object, **kwargs: object) -> None:  # noqa: ARG001
            calls.append("error")

        monkeypatch.setattr(logger, "info", record_info)
        monkeypatch.setattr(logger, "error", record_error)

        make_handle_error()(_REQUEST, ValueError("boom"))

        assert calls == ["error"]


class TestErrorHandlerCorrelationId:
    def test_set_correlation_id_appears_in_response(
        self, make_handle_error: _MakeHandleError
    ) -> None:
        expected_id = uuid4()
        correlation_id.set(expected_id)
        data = _body(make_handle_error()(_REQUEST, ValueError()))

        assert UUID(str(data["correlation_id"])) == expected_id

    def test_unset_correlation_id_is_omitted(
        self, make_handle_error: _MakeHandleError
    ) -> None:
        data = _body(make_handle_error()(_REQUEST, ValueError()))

        assert "correlation_id" not in data
