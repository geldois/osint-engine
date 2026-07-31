# Per-request pattern set injection over a composition-root policy

## Status

Accepted

## Context

Text ingestion needs a way to describe how a CPF, a CNPJ, or a CEP-and-number pair look inside a specific source's free
text — the regex plus which checksum validates each captured group. The obvious precedent already in this codebase is
`RevisionMergePolicy`/`RevisionSelectionPolicy`: a single policy chosen once in `build_container` and shared by every
call for the process's lifetime. Wiring the pattern set the same way was considered first, but rejected: unlike a
merge/selection strategy, which is a business rule that legitimately shouldn't vary per call, different ingested texts
can come from genuinely different source formats, and locking one pattern set into the composition root would mean a
redeploy every time a new text source needs recognizing — directly working against the reason a demo-grade OSINT tool
wants this feature in the first place.

## Decision

Pattern sets live behind a new read-only `PatternSetRepository` (`list`/`get`, no `save`/`delete` — that surface simply
doesn't exist on the contract yet, not merely unimplemented) seeded at boot from a fixed in-memory catalog, the same way
`mem_seeder.py` seeds default users. It's exposed on `Container` directly, not behind `UoW`, since it's
non-transactional reference data with no write path to coordinate. `IngestText` and `ListTextPatternSets` both take
`pattern_set_id` as part of the request, not the constructor's fixed dependencies, so the same running deployment can
serve multiple pattern sets and a caller picks one per call via `GET /text-ingestion/patterns` first.

## Consequences

Multiple recognition patterns can coexist in one running process, and adding request-level selection cost nothing beyond
a repository lookup. The trade-off: today there is still no way to add a *new* pattern set without a code change and
redeploy — the repository is read-only by design, so this decision only moved the selection axis to request-time, not
the definition axis. A future CRUD-capable version (patterns defined by a user, possibly with AI-assisted regex
authoring) would extend this same contract rather than replace it, since `list`/`get` are already the correct read
surface for that.
