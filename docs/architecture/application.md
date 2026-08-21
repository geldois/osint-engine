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
each newly seen `Person`'s CPF against every `Person` already known, overlapping the visible digits of a masked value
against another value's corresponding digits, and records a **possible match** where two carry distinct identities but
an overlapping CPF. This is deliberately separate from ingestion's own resolution rule, which stays
exact-identifier-only; the two solve different problems. An official identifier can itself be inconsistent across
providers — one may reveal only a partial, masked form of the identifier another knows in full — so the same real person
can end up recorded under two identities with no shared identifier to resolve them by. Comparing the document's visible
digits is the only signal left in that situation, so it stays explicitly probabilistic and advisory rather than folded
into the identifier-based resolution everything else relies on.

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

A workflow that reaches a paid provider guards against paying twice for the same identifier by checking, before it ever
calls out, whether any revision already stored for that identifier came from that same provider — a caller who repeats
the same expansion without asking to pays nothing extra, and only an explicit `force` bypasses the check. This reused
the revision history a `merge()` already keeps rather than introducing a separate record of what's been paid for: the
provider name already travels with every revision, so the check is a lookup, not new state to keep consistent. The lock
is scoped per provider, not per identifier, because a revision that arrived from ingestion or a different provider
carries no information about whether the paid one has ever run. Merging the fetched result into the graph alone isn't
enough to arm the lock: a graph merge only cascades a node revision when the node's content is actually new, so a paid
result that happens to carry the exact content something else already recorded would leave no trace of which provider
paid for it. The workflow records that node's revision a second time, directly and unconditionally, purely so the
provider name is never lost to that optimization.

Ingestion's recognition criteria were split from one fixed combination into individually addressable pieces once a
concrete gap showed up: a document appearing as bare digits with no punctuation and no textual label next to it —
exactly what a spreadsheet cell looks like — matched none of the fixed combination's pieces, and the fix couldn't be to
reformat the text before recognizing it, since ingested text feeds an immutable snapshot that must honestly reflect what
the source actually contained. Splitting recognition into individually addressable pieces, composable per request, let a
new loose-matching piece cover that gap without touching or redefining what any existing named combination means to
whoever already depends on it. The one accepted cost is the same one a loose, label-free match always carries: it will
occasionally match something that merely happens to satisfy the checksum by chance, so it stays opt-in per request
rather than folded into any existing default combination.

The catalog that lists every root ever fetched groups its entries by `root_id`, not by `Graph.id`, even though
`Graph.id` is the identity `merge()` already keys storage by. `Graph.id` is derived from the exact set of node and edge
ids it holds, so an expansion that discovers one new node under an already-known root produces a different `Graph.id`
from the one before it — grouping by that id would split a single root's timeline into two unrelated entries the moment
it grew, silently losing the earlier revision from view. Grouping by `root_id` instead means the aggregation can't live
in the repository, which only ever indexes by an entity's own id; it has to walk every stored revision and bucket it by
the root each one points to, in the use case, where it stays trivial to test without a storage double.
