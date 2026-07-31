# HybridUoW without cross-store atomicity

## Status

Accepted

## Context

`ExternalCredential` needed durable, encrypted-at-rest storage, while `Graph`/`Node`/`Edge`/`User` stay on the existing
in-memory snapshot store (`MemUoW`, `MemStorage`) — no requirement surfaced to move those to PostgreSQL too. The
existing `UoW` contract exposes `edges`, `external_credentials`, `graphs`, `nodes`, `users` repositories behind a single
`_prepare`/`_finish`/`commit`/`rollback` lifecycle, so any unit of work touching both stores has to answer: does one
transaction span Postgres and the in-memory snapshot, or do the two stores commit independently? A parametrized `MemUoW`
(accepting an injected `ExternalCredentialRepository`) was considered first, but rejected because it would force every
`MemUoW` call site to reason about a Postgres dependency even when a use case never touches credentials — `HybridUoW` as
its own class keeps that coupling explicit and localized instead.

## Decision

`HybridUoW` keeps `edges`/`graphs`/`nodes`/`users` on the exact `MemUoW` snapshot pattern (copy-on-prepare,
commit-to-storage on exit) and backs `external_credentials` with `PgExternalCredentialRepository`, whose `save()` writes
to Postgres synchronously and immediately — not deferred to `commit()`. `HybridUoW.commit()` only coordinates the
in-memory snapshot; the Postgres write already happened by the time `commit()` runs.

## Consequences

- No cross-store atomicity: a use case that writes an `ExternalCredential` and then fails before the in-memory
  `commit()` leaves the Postgres write applied with the in-memory side rolled back — an inconsistent combined state is
  possible, not merely unlikely.
- Every current use case that touches `external_credentials` writes only that one entity per unit of work (no mixed
  `external_credentials` + `graphs`/`nodes`/`edges` writes in the same transaction yet), which is why this gap hasn't
  surfaced a real bug — this stops being true the moment a use case needs both in one atomic step, tracked in
  `TO-DO.md`.
- Fixing this properly means either moving all entities onto Postgres (dropping `MemUoW` and the in-memory snapshot
  design entirely) or introducing a real two-phase commit / outbox pattern across the two stores — both are bigger
  changes than this PoC scope justified, so the gap is accepted and documented rather than half-solved.
