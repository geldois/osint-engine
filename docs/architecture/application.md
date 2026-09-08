# Application — what it does

The application layer orchestrates the business workflows the product actually offers: **expansion**, **ingestion**,
authenticating a user, and managing the external credentials a caller needs to reach a paid provider. It depends only on
the domain layer and on abstract contracts it defines itself — never on a concrete database, a concrete HTTP framework,
or a concrete external API client. Anything above this layer supplies a concrete implementation of those contracts; this
layer never knows or cares which one.

Every workflow that touches storage goes through a single transactional boundary that exposes every kind of stored
entity, plus credentials and users, uniformly, whether the underlying storage is an in-memory snapshot or a real
database. The moment data crosses in from a provider it becomes a **revision**, so provenance travels with the data
itself instead of being reconstructed later; the revision is stamped at the boundary that actually performed the fetch,
not in the orchestrating workflow, so the workflow stays pure sequencing with nothing to fake or freeze in a test.

Merging newly fetched data into what's already known is deliberately conservative: only content that's genuinely new or
has actually changed gets persisted, the **selection policy** decides which revision counts as current (by default, the
newest fetch), and the **merge policy** decides how two revisions reconcile into one when both carry data worth keeping.

Ingestion is a hard boundary by design: only a match the system can deterministically resolve — never a fuzzy or
probabilistic guess — is allowed to link into existing data. A recognized identifier that isn't already known creates a
**stub**, enriched later through expansion; a match against a node that already exists only ever adds a "mentioned in"
edge, and the existing node is never touched. Which criteria apply isn't fixed at startup — a caller composes the exact
list per request, naming individual **pattern names** and reusable **pattern sets** together, because providers format
the same identifier differently in free text and locking one fixed combination in globally would mean a redeploy every
time a new provider needs recognizing. Each mention edge records the one specific pattern name that actually produced
it, not just which combination was requested, so provenance stays precise even when two different criteria both match
the same text.

A separate, best-effort workflow runs after any expansion or ingestion produces a fresh batch of people: it compares
each newly seen person's CPF against every person already known, overlapping the visible digits of a masked value
against another value's corresponding digits, and records a **possible match** where two carry distinct identities but
an overlapping CPF. This is deliberately separate from ingestion's own resolution rule, which stays
exact-identifier-only; the two solve different problems. An official identifier can itself be inconsistent across
providers — one may reveal only a partial, masked form of the identifier another knows in full — so the same real person
can end up recorded under two identities with no shared identifier to resolve them by. Comparing the document's visible
digits is the only signal left in that situation, so it stays explicitly probabilistic and advisory rather than folded
into the identifier-based resolution everything else relies on.

A separate append-only log now records every attempt a caller makes to expand a CPF, regardless of outcome — blocked by
the reuse lock, no external credential on file, the provider returning nothing, or a genuine successful expansion. This
does not replace the reuse lock's own reasoning that revision history is enough to decide *whether to pay again*; it
answers a different question the revision history structurally cannot: a full audit trail of every attempt, including
the ones the lock stopped before they ever reached the provider. An entity's own revisions are deliberately deduplicated
by content — searching for the same person twice with identical results collapses to one revision, which is correct for
"what do we currently know," but wrong for "how many times was this looked up." The log's own entries are never
deduplicated by content for exactly that reason; each is stamped with a non-deterministic identity of its own, unlike
every other record in this system, because it represents an event, not a piece of content that can recur.

## Decisions

Where a revision gets stamped was revisited once: stamping it in the orchestrating workflow was the fast, narrow fix at
the time, but it recorded when the workflow got around to it rather than the instant the data arrived, and it forced the
workflow's own tests to freeze the clock just to assert a timestamp. Moving the responsibility to the component that
performs the fetch fixed both problems and left the workflow pure orchestration again.

A transactional boundary spanning two different kinds of storage at once (an in-memory snapshot plus a real external
database) does not currently guarantee both sides succeed or fail together. This is accepted for now because no current
workflow writes to both kinds of storage in the same unit of work; the moment one does, this gap needs a real fix rather
than remaining a known, accepted edge case.

Whichever component discovers an entity now always persists it individually as well as inside the graph it arrived in,
so anything else can look it up on its own afterward. Persisting every entity unconditionally on every merge was tried
first and rejected: an entity whose content hadn't changed still got re-stamped with the new fetch time, which made the
selection policy treat a stale re-fetch as the freshest revision and silently discard the entity's true original
provenance. Checking each entity against what's already stored, and only touching what's genuinely new or changed, fixed
that.

The CPF-overlap workflow deliberately never merges or re-identifies the two nodes it flags; it only ever adds the
possible-match edge, leaving the judgment call to whoever reviews the graph. Auto-merging on an overlapping CPF alone
was rejected outright: an overlap can still coincide by chance on the digits either side happened to reveal, and merging
two nodes that turn out to be different real people is a much more damaging, harder-to-undo mistake than surfacing a
match a human has to double-check.

The merge policy's default was revisited once the frontend's own design became clear: it now treats every expansion or
ingestion as a fresh, immutable snapshot stacked on top of what came before, not a single record it keeps refining in
place, and it intends to let a person navigate back through those snapshots per node or edge. Reconciling a newly
arrived revision with whatever was already stored — filling its missing fields from an older, more complete one — was
the right default when the server owned the single "current" view, but it now works against a client that wants the
revisions exactly as they arrived, distinct and stacked, so it can offer that history navigation honestly. The default
became simpler: keep the incoming revision exactly as it arrived, no synthesis. The old reconciling behavior was not
deleted — it remains available to inject for a future workflow that genuinely needs a server-synthesized view — but
nothing wires it in by default anymore. The one accepted cost: a later revision that happens to carry fewer filled
fields than an earlier one now makes the "current" view look less complete than it did before that revision arrived,
even though the more complete, older data is still stored underneath; closing that gap is the frontend's own
history-navigation work, not this layer's.

Every expansion workflow guards against repeating the exact same fetch by checking, before it ever calls out, whether a
successful attempt for that identifier already exists from that same provider — a caller who repeats the same expansion
without asking to pays nothing extra on a paid route and spares the upstream a redundant call on a free one, and only an
explicit override flag bypasses the check. The lock is scoped per provider, not per identifier, because an attempt that
arrived from ingestion or a different provider carries no information about whether this one has ever run; "already ran"
itself is treated as either outcome that actually reached the provider (a result, or a confirmed empty), never a request
that failed before it got there or was itself blocked by this same lock.

The check reads the append-only consumption log (`EntityRecord`, `consumption/entity_record.py`), never the node storage
a successful fetch also writes to — deliberately, after the first version of this lock (checking node revisions instead)
shipped a real defect: every workflow's "no content beyond the bare identifier" stub carries identical content
regardless of which route produced it, so two different routes' stub writes collapse to the exact same content-addressed
storage slot, and the second one's provider tag silently overwrites the first's — the very loss this lock exists to
prevent, reintroduced by checking a store that deduplicates by content for an unrelated, legitimate reason. The
consumption log has no such deduplication — each attempt is its own event, keyed by nothing but its own identity — so a
provider tag written there can never be overwritten by a different route's write. The guard's own write of the blocked
attempt goes to that same log, for the same reason.

The check-and-record shape above lives in one shared function (`consumption/guard_reuse_lock.py`) that every expansion
workflow calls, rather than each repeating the same log-lookup-then-compare block inline — a second, inline copy of this
exact block had already appeared once (the CPF batch estimate use case), the concrete signal that the duplication was
real, not hypothetical. The shared function never raises what it finds; it returns the error for the caller to raise
once its own `uow_factory()` block has closed, so the blocked-attempt record the function just wrote survives the commit
instead of being rolled back by an inline raise — the same defect this file's own decisions already record fixing once
for the CPF root route, now structural for every route through the shared function rather than a convention each one has
to remember separately.

Knowing which provider string belongs to which workflow, and whether that route is billable, is itself a registration a
workflow makes about itself, not a fact the guard infers: `UseCaseRegistry` (`contracts/use_case.py`) holds a declared
`(provider, billable)` pair per use case class, and the guard looks a workflow up in it by class identity on every call,
before touching storage. A route whose class was never registered raises immediately (`UnregisteredUseCaseError`) the
first time it reaches the guard — never a silent no-op, and never a class of bug that waits for a human to notice a
missing test. The registry's shape mirrors `EdgeSchemaRegistry` (`interface/http/schemas/edge_schema.py`), this
codebase's existing precedent for the same kind of self-registering, fail-loud-on-miss catalogue; it could not live at
that same interface layer, though, since the guard it backs needs the transactional `UoW` a fetcher-layer component
never receives, so it sits in `contracts/use_case.py` instead, next to the base classes every workflow already inherits
from.

Ingestion's recognition criteria were split from one fixed combination into individually addressable pieces once a
concrete gap showed up: a document appearing as bare digits with no punctuation and no textual label next to it —
exactly what a spreadsheet cell looks like — matched none of the fixed combination's pieces, and the fix couldn't be to
reformat the text before recognizing it, since ingested text feeds an immutable snapshot that must honestly reflect what
the source actually contained. Splitting recognition into individually addressable pieces, composable per request, let a
new loose-matching piece cover that gap without touching or redefining what any existing named combination means to
whoever already depends on it. The one accepted cost is the same one a loose, label-free match always carries: it will
occasionally match something that merely happens to satisfy the checksum by chance, so it stays opt-in per request
rather than folded into any existing default combination.

Recording a blocked attempt's log entry required moving where the reuse lock's error is actually raised. The
transactional boundary only persists what a workflow wrote once the boundary closes without an exception escaping it;
raising inline, from inside that boundary, discarded whatever had just been written on the way out, silently losing the
very attempt the log exists to capture. The workflow now captures which error to raise, if any, as a local decision,
lets the boundary close normally so the write survives, and only then raises — the caller still sees the exact same
error, but the audit trail no longer depends on nobody having actually blocked.

The catalog that lists every root ever fetched groups its entries by the root identifier, not by the graph's own
content-derived identity, even though that content-derived identity is what storage is already keyed by when merging.
The graph's own identity is derived from the exact set of node and edge ids it holds, so an expansion that discovers one
new node under an already-known root produces a different graph identity from the one before it — grouping by that
identity would split a single root's timeline into two unrelated entries the moment it grew, silently losing the earlier
revision from view. Grouping by the root identifier instead means the aggregation can't live in the repository, which
only ever indexes by an entity's own identity; it has to walk every stored revision and bucket it by the root each one
points to, in the use case, where it stays trivial to test without a storage double.

Each catalog entry's set of already-fetched routes is read from a second, separate query per root — the same consumption
log the reuse lock itself reads — rather than derived from the graph-level revisions the entry already walks for its
`providers` field. A graph-level revision is stamped by the fetcher that produced it, and more than one route can share
the same fetcher (every Portal da Transparência route stamps `"portal_transparencia"` there, every KipFlow route stamps
`"kipflow"`), so `providers` can never distinguish which specific route ran. The consumption log holds one entry per
attempt, stamped with the calling workflow's own registered provider string, which is the only place per-route
granularity actually exists.

## Consequences

A provider guard scoped per provider rather than per identifier means a workflow reaching a new external source still
declares its own `(provider, billable)` pair in `UseCaseRegistry` before its first call — registration doesn't
generalize to a source nobody named yet, by design, since a shared guard function still needs to know which stored
revisions belong to which route. What does now generalize is the failure mode for skipping that step: a workflow that
never registers raises `UnregisteredUseCaseError` the moment it reaches the guard, rather than quietly shipping with no
reuse protection until someone notices the gap by hand. The atomicity gap across the two kinds of storage stays a
standing obligation rather than a closed question: the moment any future workflow writes to both in one unit of work,
that workflow inherits the gap and has to close it, not merely notice it.

Because the merge policy's default now keeps every incoming revision exactly as it arrived, any future workflow that
genuinely wants a single synthesized view has to explicitly reach for the older reconciling policy — it stays available,
but nothing wires it in automatically, so that choice has to be made deliberately each time, not inherited for free.

Splitting recognition criteria into individually addressable pieces means a future provider's own format is added as a
new piece rather than a redefinition of an existing combination, but a caller only gets a newly added piece's coverage
by naming it, or an updated combination, explicitly — an existing default combination never grows silently underneath
whoever already depends on it.

Grouping the catalog by the root identifier rather than the graph's own content-derived identity means that aggregation
cannot be answered by the same identity-keyed lookup every other stored entity supports; a future storage backend has to
support walking and bucketing by root the same way, or the catalog's own grouping logic has to be re-derived for it
specifically.
