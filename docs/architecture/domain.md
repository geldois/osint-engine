# Domain — what it does

The domain layer defines what a real-world entity is (a company, a person, an address, a phone, an email, a CNAE
classification, a sanction, a piece of ingested text) and how two entities relate to each other. Every entity's identity
is derived deterministically from its own content — the same real-world thing, described the same way, always produces
the same identifier, regardless of when or where it was constructed. Deduplication and idempotent re-processing follow
automatically: fetching the same subject twice never creates two competing records for the same real thing.

An entity refuses to exist in an invalid state. If a concrete type is missing something the base abstraction requires —
a namespace, a properly typed identifier — the mistake is caught the moment the class itself is defined, not the first
time someone tries to use it. The same fail-fast posture extends to relationships between entities: a relationship
connecting an entity to itself is rejected outright, and a graph containing a relationship that points at an entity the
graph doesn't actually hold is rejected too, both at the moment of construction, not later when something happens to
touch the bad data.

Identity is computed from only the fields that make an entity the entity it is, not from every attribute it happens to
carry. That separation matters because entities grow richer over time — new descriptive fields get added — without ever
changing what identity means for an already-existing kind of entity. A few identifying fields (a tax ID, a national ID
number) are normalized before identity is computed, so the same real-world subject is recognized as one thing even when
different providers format that field differently, while the original, unnormalized value the caller supplied is
preserved untouched for display.

Relationships between entities are modeled as their own first-class, strongly typed concept — one dedicated type per
kind of relationship (ownership, residency, membership, mention-in-text, sanction, and so on) rather than a single
generic connector, even where two relationships look structurally identical. Typing carries all the way down to which
kind of entity may sit on each end of a relationship, so connecting the wrong kinds of things together is caught before
the program ever runs, not discovered later as a data bug. Every module in this layer is free of any dependency on
frameworks, persistence technology, or transport concerns; it can be exercised in complete isolation.

## Decisions

An early attempt leaned on a generic, framework-provided base for entities to get equality and construction machinery
for free; it was abandoned because it could not fail fast the moment a concrete type broke the contract — a violation
only surfaced the first time an instance was actually built. A hand-written base with fail-fast validation replaced it
for exactly that reason.

Making one relationship generic across two entity kinds that happen to need the same shape (ownership by an individual
versus ownership by another entity) was considered and rejected: every other relationship in this layer already exists
as its own dedicated type, and a generic exception here would break that consistency rather than simplify it — the
accepted cost is a bit of repeated shape between the two, not a shared abstraction.

Normalizing an identifying field is decided individually, case by case, right where identity for that kind of entity is
computed, deliberately not centralized into one universal rule — at least one identifying-looking field genuinely cannot
be normalized the same way, since it can legitimately hold non-numeric content that a universal rule would silently
corrupt.
