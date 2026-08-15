# Infrastructure — what it does

This layer holds every concrete adapter that talks to the outside world on behalf of the layers above it — external HTTP
APIs, the password-hashing algorithm, token signing, and every persistence backend. Nothing above this layer imports a
concrete adapter directly; each one exists only to satisfy a contract defined in the application layer, so any adapter
can be swapped for another implementing the same contract without the layers above noticing.

Two independent providers are integrated today: one unauthenticated aggregator for company registration data, and one
that requires a caller-supplied API key for public-sanction records. Both share the same shape — each concrete endpoint
declares only its own path and how to translate its response into domain entities, while the shared base every endpoint
builds on handles composing the full request and turning a failed HTTP call into a single, consistent error every
endpoint reports the same way.

Persistence today is split two ways depending on what's being stored. Every entity, relationship, and user account lives
in a plain in-memory snapshot with no framework and no external dependency — appropriate for a demo-scale deployment
where nothing needs to survive a process restart and nothing needs to coordinate concurrent writers. Beyond looking an
entity up by its own identity, the in-memory store can also list every currently-known entity of a given kind at once —
the one lookup shape the possible-match workflow needs and the identity-keyed storage didn't offer before, added
narrowly for that purpose rather than as a general query capability. One kind of sensitive data — the external
credential for the paid provider — is durable and encrypted at rest in a real relational database instead, reached
through hand-written, inspectable queries rather than any query-building abstraction, because staying close to the raw
query was itself a deliberate goal, not an accident of the smallest-effort path. A single transactional boundary bridges
the two storage kinds transparently to anything above it, at the cost that a failure partway through a write touching
both kinds can leave one side applied and the other rolled back — accepted today because nothing yet writes to both
kinds in the same transaction.

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
