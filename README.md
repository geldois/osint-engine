# OSINT Engine

[![CI](https://github.com/geldois/osint-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/geldois/osint-engine/actions)

Entity relationship graph engine that expands identifiers into a fully traceable network of connections sourced
exclusively from official public records.

## Overview

A **CNPJ** enters the engine as a root identifier. The engine queries official public records, constructs a typed,
immutable graph, and returns it — ready to traverse. Each **Node** represents a real-world entity: a company, a
person, an address, a sanction, a CNAE classification, a phone, or an email. Each **Edge** names the relationship
between two nodes: `company_has_member`, `person_owns_company`, `company_received_sanction`, and so on.

Every node and every edge carries a stable, deterministic identity derived exclusively from its content. The same
CNPJ expanded on different machines at different times always produces the same graph with the same IDs — making
the structure idempotent by construction, not by convention.

## Stack

- **Runtime:** Python 3.12, FastAPI, Uvicorn
- **HTTP client:** httpx (async)
- **Observability:** structlog
- **Tooling:** uv, Ruff, basedpyright (strict), Commitizen
- **Testing:** pytest, pytest-asyncio

## Design

### Content-addressable entity identity

Every entity — node, edge, and graph — derives its ID from its content via UUID5. The same input always produces
the same identifier, on any machine, at any time. Deduplication, idempotent upserts, and safe concurrent writes are
structural consequences, not implementation choices. Each entity type occupies its own UUID namespace so that a
`CompanyID` and a `PersonID` derived from identical payloads can never collide.

See [ADR-0003](docs/adr/0003-uuid5-over-uuid4-for-entity-identity.md).

### Fail-fast entity contracts

The entity base class uses `__init_subclass__` to validate every subclass at import time, not at instantiation.
A concrete entity missing a namespace or declaring an incompatible ID type raises immediately when the module is
loaded — before any test runs, before any instance is created. The domain is self-defending.

`__setattr__` and `__delattr__` raise `FrozenInstanceError` on every entity. Immutability is structural, not
enforced by convention.

See [ADR-0002](docs/adr/0002-manual-entity-base-class.md).

### Zero-cost type hierarchy

Each concrete entity declares its own `NewType` ID (`CompanyID`, `PersonID`, `GraphID`, …) as the generic
parameter of `Entity[IDType_co]`, where `IDType_co` is a covariant `TypeVar` bound to `UUID`. The type-checker
enforces that a `Node[CompanyID]` cannot be substituted for a `Node[PersonID]` — and that edge source and target
ID types match their declared constraints — with no runtime representation whatsoever. `NewType` is the identity
function at runtime; the distinction exists only in the type-checker's world.

See [ADR-0004](docs/adr/0004-idtype-co-typevar-for-covariant-id-typing.md).

## Testing

```bash
uv run pytest
```

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/geldois/osint-engine.git
cd osint-engine
uv sync --group dev
uv run pre-commit install
uv run pytest
```
