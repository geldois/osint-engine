from __future__ import annotations

from typing import override

from osint_engine.interface.errors.interface_error import InterfaceError


class AuthorizationError(InterfaceError, error_code=None): ...


class InsufficientRoleError(
    AuthorizationError, error_code="AUTHORIZATION_INSUFFICIENT_ROLE"
):
    required_roles: frozenset[str]
    role: str

    @override
    def __init__(self, *, role: str, required_roles: frozenset[str]) -> None:
        super().__init__(role=role, required_roles=required_roles)

    @override
    def _build_message(self) -> str:
        allowed = ", ".join(sorted(self.required_roles))

        return f"Role '{self.role}' is not permitted; requires one of: {allowed}"
