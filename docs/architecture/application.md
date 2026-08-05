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
edge, and the existing node is never touched. Which **pattern set** applies isn't fixed at startup — a caller picks one
per request, because providers format the same identifier differently in free text, and locking one set in globally
would mean a redeploy every time a new provider needs recognizing.

A separate, best-effort workflow runs after any expansion or ingestion produces a fresh batch of people or companies: it
compares each newly seen one's name against every node of the same kind already known and records a **possible match**
where two carry distinct identities but strongly similar names. This is deliberately separate from ingestion's own
resolution rule, which stays exact-identifier-only; the two solve different problems. An official identifier can itself
be inconsistent across providers — one may reveal only a partial, masked form of the identifier another knows in full —
so the same real person or company can end up recorded under two identities with no shared identifier to resolve them
by. Comparing names is the only signal left in that situation, so it stays explicitly probabilistic and advisory rather
than folded into the identifier-based resolution everything else relies on.

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

The name-similarity workflow deliberately never merges or re-identifies the two nodes it flags; it only ever adds the
possible-match edge, leaving the judgment call to whoever reviews the graph. Auto-merging on a name match alone was
rejected outright: name matching produces false positives by nature, and merging two nodes that turn out to be different
real people or companies is a much more damaging, harder-to-undo mistake than surfacing a match a human has to
double-check.
