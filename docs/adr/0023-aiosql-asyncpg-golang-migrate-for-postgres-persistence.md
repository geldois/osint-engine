# aiosql, asyncpg, and golang-migrate for PostgreSQL persistence

## Status

Accepted

## Context

`PgExternalCredentialRepository` needed a Postgres access layer, a schema-migration tool, and a way to integration-test
against a real engine, chosen with an explicit personal-learning goal in play: stay close to bare SQL rather than
adopt a full ORM, keep migrations simple and unversioned-tooling-free where possible, and pick the most performant,
extensible option available at each layer. `api_key` also needed to never be stored as plaintext, ruling out a bare
`INSERT`/`SELECT` without an encryption step.

## Decision

`asyncpg` is the driver: it is the fastest Postgres driver available for Python (binary protocol, no ORM overhead)
and is what `aiosql` targets for async query execution. `aiosql` maps hand-written `.sql` files to Python functions by
name-comment convention (`-- name: find_by_username_and_provider^`), keeping every query as inspectable, editable SQL
instead of an ORM-generated one — the closest available option to bare SQL that still gives typed Python call sites.
`golang-migrate` handles schema migrations as plain numbered `.up.sql`/`.down.sql` file pairs, with no Python
dependency or ORM-coupled migration DSL; it has no PyPI package, so the CLI binary is pulled into the Docker image via
a multi-stage `COPY --from=migrate/migrate:v4.19.1` rather than declared in `pyproject.toml`. `api_key` is encrypted
with `cryptography`'s `Fernet` at the application layer (encrypt before `INSERT`, decrypt after `SELECT`) instead of
Postgres-side `pgcrypto`, keeping the encryption key and logic entirely inside the Python process rather than split
across the database and the app. `testcontainers[postgres]` backs the integration tests, spinning up a real,
disposable Postgres per test session instead of faking the repository — a fake would just reimplement
`MemExternalCredentialRepository` and could never catch a real SQL or encryption bug (which it did: an invalid
`aiosql` name-line syntax broke test collection until this real-engine layer surfaced it).

## Consequences

- `asyncpg` ships no `py.typed` marker and `aiosql.from_path()`'s returned `Queries` object has dynamically generated
  attributes; both are permanently unknowable to `basedpyright --strict`, requiring narrow
  `# pyright: ignore[reportUnknownMemberType]` comments at each call site rather than a blanket suppression.
- Every new query is a new named block in `external_credentials.sql` plus a matching `Protocol` method in
  `_ExternalCredentialQueries` — more manual bookkeeping than an ORM's auto-generated query builder, traded for SQL
  that stays fully visible and hand-editable.
- `golang-migrate`'s binary is a non-Python, non-`uv`-managed dependency: CI and the Docker image must fetch it
  separately, and local dev has no automated install path yet (tracked in `TO-DO.md`).
- `testcontainers` pulls Docker images from Docker Hub on first run per machine (cached afterward) and, in CI, on
  every ephemeral run — this needed an authenticated Docker Hub login in CI to avoid anonymous rate-limit throttling
  on shared runner IPs, an operational cost a fake repository would not have had.
