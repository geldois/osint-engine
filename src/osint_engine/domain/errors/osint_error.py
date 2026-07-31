from __future__ import annotations


class OsintError(Exception):
    """Common root of every first-party error, across all layers.

    Each layer's error base (``DomainError``, ``ApplicationError``,
    ``InfrastructureError``, ``InterfaceError``) inherits from this. It lets an
    outer adapter register or recognise "any error we raised" with a single type
    from the innermost layer — e.g. the HTTP app registers one exception handler
    for ``OsintError`` instead of importing each layer's base (which would make
    the interface import infrastructure and break the dependency rule).
    """
