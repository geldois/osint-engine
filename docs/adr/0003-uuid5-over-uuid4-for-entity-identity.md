# uuid5-over-uuid4-for-entity-identity

## Status

Accepted

## Context

Domain entities — nodes, edges, and graphs — needed stable, reproducible identifiers. The naive choice of UUID4 (random) would make two entity instances constructed from identical data produce different IDs. This breaks several invariants the domain depends on:

- Deduplication: the same real-world entity (e.g., a company with a given CNPJ) would be inserted multiple times into the graph with distinct identifiers.
- Idempotency: re-fetching and re-processing the same source data would produce structurally different graphs.
- Concurrent writes: two workers expanding the same node concurrently would generate conflicting entities with no way to detect the collision without querying existing state.

The domain also needed each entity type to occupy its own identity space so that a `CompanyID` and a `PersonID` derived from the same logical key could never collide.

## Decision

Use UUID5 (name-based, SHA-1) as the identity function for all entities. Every concrete entity type is assigned a dedicated namespace UUID derived by hashing its canonical name against `NAMESPACE_DNS` via `EntityNAMESPACE`:

```python
class EntityNAMESPACE(Enum):
    COMPANY = "COMPANY"
    PERSON  = "PERSON"
    # ...

    def __init__(self, value: str, /) -> None:
        self.namespace = uuid5(namespace=NAMESPACE_DNS, name=value)
```

The entity ID is then computed in `Entity.calculate_id` by serializing the constructor kwargs as a deterministic JSON string and hashing it against the entity's own namespace:

```python
uuid5(namespace=cls.namespace, name=json.dumps(kwargs, sort_keys=True, default=str))
```

UUID4 was rejected because randomness is incompatible with content-addressability.

## Consequences

- **Deterministic:** the same input data always produces the same entity ID, on any machine, at any time.
- **Content-addressable:** the ID encodes what the entity is, not when it was created. Duplicate insertions are safe by construction.
- **Collision-resistant across types:** each entity type has its own namespace, so `uuid5(COMPANY_NS, "X") ≠ uuid5(PERSON_NS, "X")` even for identical payloads.
- **Immutable domain:** no mutable state is required to resolve or assign identity. Race conditions on concurrent writes are structurally eliminated — both workers produce the same ID and the upsert is idempotent.
- **Readable in logs:** UUID5 values are stable across runs, making them searchable in traces and logs without a lookup table.
- **Trade-off:** two entities with identical constructor arguments are considered the same entity. Callers must ensure that the kwargs passed to `__init__` are the canonical, normalized representation of the entity (e.g., trimmed strings, normalized CNPJ format).
