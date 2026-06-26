# TO-DO

## fix(domain)

- [ ] replace `_validate_deterministic_str` heuristic with whitelist of known-deterministic types

## test(application)

- [ ] test `ExpandByCNPJ` orchestration: fetch, persist, and return graph

## test(domain)

- [ ] test `_validate_deterministic_str` error path for objects without `__str__` or `__repr__` overridden
- [ ] test `calculate_id` determinism under kwarg reorder and key rename

## test(infrastructure/fetchers)

- [ ] test `BrasilAPICNPJFetcher` HTTP error and network failure handling
- [ ] test `BrasilAPICNPJMapper` field mapping, optional fields, and partner type filtering

## test(interface/http)

- [ ] test node and edge presenter dispatch and `UnmappedTypeSchemaError` path
- [ ] test graph presenter full mapping
- [ ] test schema registries completeness and `MissingDiscriminatorFieldError` guard
