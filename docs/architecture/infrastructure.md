# Infrastructure — what it does

This layer holds every concrete adapter that talks to the outside world on behalf of the layers above it — external HTTP
APIs, the password-hashing algorithm, token signing, and every persistence backend. Nothing above this layer imports a
concrete adapter directly; each one exists only to satisfy a contract defined in the application layer, so any adapter
can be swapped for another implementing the same contract without the layers above noticing.

Three independent providers are integrated today: one unauthenticated aggregator for company registration data, one that
requires a caller-supplied API key for public-sanction records, and one that requires a caller-supplied API key for CPF
lookups. All three share the same shape — each concrete endpoint declares only its own path and how to translate its
response into domain entities, while the shared base every endpoint builds on handles composing the full request and
turning a failed HTTP call into a single, consistent error every endpoint reports the same way. Every provider gets this
shared base from the moment it's integrated, even the one with a single endpoint today: the base itself carries no
per-endpoint knowledge, so there's nothing to wait for a second endpoint to justify, and every provider looking the same
way keeps the pattern predictable instead of conditional on how many endpoints a given provider happens to have right
now.

Persistence today is split two ways depending on what's being stored. Every entity, relationship, and user account lives
in a plain in-memory snapshot with no framework and no external dependency — appropriate for a demo-scale deployment
where nothing needs to survive a process restart and nothing needs to coordinate concurrent writers. Beyond looking an
entity up by its own identity, the in-memory store can also list every currently-known entity of a given kind at once —
the one lookup shape the possible-match workflow needs and the identity-keyed storage didn't offer before, added
narrowly for that purpose rather than as a general query capability. One kind of sensitive data — the external
credentials callers save for each paid provider — is durable and encrypted at rest in a real relational database
instead, reached through hand-written, inspectable queries rather than any query-building abstraction, because staying
close to the raw query was itself a deliberate goal, not an accident of the smallest-effort path. A single transactional
boundary bridges the two storage kinds transparently to anything above it, at the cost that a failure partway through a
write touching both kinds can leave one side applied and the other rolled back — accepted today because nothing yet
writes to both kinds in the same transaction.

Password hashing uses the current OWASP-recommended, memory-hard algorithm, deliberately slow so that guessing many
candidate passwords stays expensive for an attacker; verification always runs the same check whether or not the account
being checked actually exists, so an attempt against a username that isn't there takes the same time as one against a
real account, closing a timing side-channel that would otherwise let an attacker enumerate valid usernames.

Turning an uploaded spreadsheet into plain text is a single, stateless step with no state of its own: it flattens
whatever the file actually contained, cell by cell, into text without inserting or reformatting anything the source
didn't have, so ingestion downstream sees exactly what a caller uploaded. Every failure a corrupted or oversized file
can produce — a size limit crossed before any of the file's content is read, a row count crossed mid-file, or the
underlying file-reading library itself failing on content that only looks like a valid spreadsheet — is converted into
one of a small, closed set of errors at this boundary, so nothing about a third-party library's own exception surface
ever reaches the layers above.

## Decisions

The production persistence target is a proper graph database; the in-memory snapshot is a deliberate, explicit MVP
boundary, not a temporary hack — every persistence contract the layers above depend on is already validated against a
real, working implementation, so introducing a different backend later is a matter of writing a new adapter against the
same contracts, not changing anything above this layer.

The paid CPF provider publishes per-API-key limits across three windows — a 5-per-second burst, a 100-per-minute average
and a 1000-per-hour volume — and the engine paces every outbound call against them from the client side instead of
discovering the ceiling through 429s. Each credential gets its own in-memory queue of three token buckets fed at the
documented rates; a fetch that would cross any window waits in arrival order rather than dropping, nothing re-tries on
the caller's behalf, and the batch pre-flight reads the queue's current deficit so a caller knows the wait before paying
for anything. The buckets start full rather than dripping from empty: the burst capacity mirrors the provider's own
published limits and keeps small demo batches fast, at the accepted cost that the first requests of a fresh process may
front-load a window up to its burst allowance while the long-run rate stays at or under the documented average. The
state lives in one process only — a restart loses the queue, but never paid work, because each expansion commits the
moment it completes and re-submitting a batch costs nothing twice.

The durable, database-backed storage stays close to raw hand-written queries by explicit choice, favoring inspectability
and a learning goal over the convenience of an abstraction that writes the queries automatically; schema changes are
plain, ordered, reversible migration files rather than a framework-specific migration language, so they carry no
dependency on any particular ORM or Python tooling.

Converting a corrupted spreadsheet into a clear error rather than letting an underlying library's own exception escape
started with the small number of failure types documented for that library, then grew once actually reproducing a
handful of different corruption shapes — an archive missing an internal part, a truncated internal document — surfaced
distinct exception types the library raises for the same broad situation, confirming that no closed list can be trusted
as exhaustive for a file format understood by a third-party library, not authored by this project. The chosen shape
keeps both properties at once: every failure mode already reproduced and confirmed stays named explicitly, so the code
documents exactly what's actually been seen and tested, while one final, deliberately broad catch underneath guarantees
nothing from that same boundary can still escape unclassified.

## Consequences

Replacing the in-memory store with a real graph database later is adapter work against contracts already proven correct,
not a redesign of anything above this layer — the layers above never see which concrete store answers a lookup, so that
migration's own risk stays contained entirely to this one.

Because the pacing state lives in one process with no persistence of its own, restarting the process resets every
credential's own window back to full — a caller loses no paid work, since each completed expansion already committed,
but also loses whatever wait a batch estimate had already promised, so an estimate given just before a restart can
undercount the true wait afterward.

Staying on hand-written queries and plain migration files means every future schema change or query is written and
reviewed by hand, with nothing generated to fall out of sync with the schema — the tradeoff is that no tool catches a
query still referencing a column a migration already renamed; that stays a manual discipline, not a mechanical
guarantee.

The closed list of named spreadsheet-corruption failures is exactly what has actually been reproduced and confirmed so
far, not a claim of completeness — a new corruption shape a future file exhibits falls through to the broad catch
underneath rather than a specific, documented one, until someone reproduces it and gives it its own name.
