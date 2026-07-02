# In-memory persistence as MVP boundary

## Status

Accepted

## Context

The production persistence target is a graph database (Neo4j). Wiring Neo4j into an MVP introduces operational
overhead: cluster setup, schema migration tooling, connection pooling, Cypher query design, and a non-trivial
integration test surface. None of these are required to validate the graph model or demonstrate the CNPJ expansion
pipeline to a client.

The application layer already enforces persistence abstraction through the Unit of Work and Repository ports. Any
concrete adapter that implements those contracts is a valid persistence backend.

## Decision

Use a single `MemStorage` dataclass (plain Python dicts) as the only persistence backend for the MVP. `MemUoW`
and the `Mem*Repository` family implement the same ports that a future `Neo4jUoW` will implement. The composition
root (`croot.py`) wires them in; nothing above the infrastructure boundary knows they exist.

Admin user seeding is performed once at startup via `seed_mem_storage`, which is called from the composition root
before the server starts. This is sufficient for a single-user demo.

## Consequences

- No data survives a process restart. This is acceptable for the MVP and explicit to anyone reading `MemStorage`.

- The port contracts (`UoW`, `UserRepository`, `GraphRepository`, etc.) are validated against a real implementation
  that must satisfy all invariants. Switching to Neo4j requires writing new adapters, not changing the ports.

- `MemStorage` is frozen at the field level but its dict fields remain mutable — this is intentional. Repositories
  mutate the dicts directly; the frozen constraint prevents accidental reassignment of the storage reference itself.

- Concurrency is not safe. `MemStorage` has no locking. At MVP scale (single user, demo workload) this is not a
  problem. A production adapter must handle concurrent writes at the database level.

- The `uow_factory: Callable[[], UoW]` pattern in the composition root and use cases means each request gets a
  fresh `MemUoW` instance scoped to that call, while the underlying `MemStorage` is shared across requests. This
  matches the session-per-request model a database UoW would also follow.
