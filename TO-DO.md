# TO-DO

## chore(ci)

- install Renovate GitHub App on geldois/osint-engine and push `renovate.json` to enable automated dependency updates
for actions, uv, and pre-commit hooks

## docs(adr)

- ADR-0006: manual composition root over FastAPI DI
- ADR-0007: in-memory persistence as deliberate MVP boundary

## feat(infrastructure/auth)

- implement `PasswordHasher` (`password_hasher.py` is empty)
- populate `__init__.py` exports
- add `UserRepository` interface and in-memory implementation
- wire auth into FastAPI router, dependency injection, and middleware

## fix(domain)

- replace `_validate_deterministic_str` heuristic with whitelist of known-deterministic types

## test(application)

- test `ExpandByCNPJ` orchestration: fetch, persist, and return graph

## test(domain)

- test `_validate_deterministic_str` error path for objects without `__str__` or `__repr__` overridden
- test `calculate_id` determinism under kwarg reorder and key rename

## test(infrastructure/fetchers)

- test `BrasilAPICNPJFetcher` HTTP error and network failure handling
- test `BrasilAPICNPJMapper` field mapping, optional fields, and partner type filtering

## test(interface/http)

- test node and edge presenter dispatch and `UnmappedTypeSchemaError` path
- test graph presenter full mapping
- test schema registries completeness and `MissingDiscriminatorFieldError` guard
