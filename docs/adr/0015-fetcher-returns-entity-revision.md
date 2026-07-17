# Fetcher returns EntityRevision and owns fetched_at provenance

## Status

Accepted. Supersedes: ADR-0014.

## Context

ADR-0014 had the use case (`ExpandByCNPJ`) mint the `EntityRevision[Graph]` by stamping `datetime.now(UTC)` after the
fetch returned, chosen to bound the interrupted refactor without touching the fetcher layer. That placement made
`fetched_at` record when the use case wrapped the graph rather than when the data was actually obtained, and it
scattered the `now(UTC)` call — and the revision-construction knowledge — into orchestration code, which also forced
use-case tests to freeze time to assert the timestamp. With the fetcher layer now in scope for enrichment, the
provenance ownership can be corrected. The mapper (`map_graph`) was considered as the owner and rejected: it is a pure
structural transformation from `Payload` to `Graph` with no access to the fetch instant, so giving it a timestamp would
couple a pure transform to I/O provenance.

## Decision

`CNPJFetcher.fetch` returns `EntityRevision[Graph]`; `BrasilAPICNPJv1Fetcher` captures
`fetched_at = datetime.now(tz=UTC)` at the I/O boundary, immediately after the successful response is parsed, and wraps
the mapper's `Graph` in `EntityRevision(entity=…, fetched_at=…, merged_at=None)`. The mapper stays pure.
`ExpandByCNPJ.execute` receives the revision, passes it straight to `graphs.merge`, and returns `revision.entity`, so it
keeps its `Query[Graph]` return contract and holds no timestamping logic. A dedicated narrower "observation" type
(entity plus `fetched_at`, without `merged_at`) was deliberately not introduced: `merged_at=None` is the legitimate
"raw fetch, not yet merged" state of a revision, not an illegal state, so splitting the type would add a second type
and a repository-contract ripple for no invariant gain while a single fetcher exists.

## Consequences

`fetched_at` now reflects the true fetch instant and lives at the boundary that owns it, the use case is pure
orchestration again, and use-case tests are deterministic because the fake fetcher returns a fixed revision rather than
relying on wall-clock time — the fetcher's own test asserts only that `fetched_at.tzinfo is UTC`. The cost is that the
`CNPJFetcher` contract, its BrasilAPI implementation, and the `FakeCNPJFetcher` test double all changed shape, and every
future fetcher must now construct the revision itself; should that construction ever repeat across fetchers, a
shared `EntityRevision.fetched(entity)` constructor helper is the natural next step. The HTTP presentation layer is
unaffected because the use case still returns a bare `Graph`.
