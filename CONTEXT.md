# osint-engine

Expands an official Brazilian identifier into a graph of everything connected to it, and recognizes those identifiers
inside free text.

## Language

**Entity**: Anything whose identity is derived deterministically from its own content — the same real-world thing,
described the same way, always yields the same id. Nodes and edges are both entities. *Avoid*: model

**ID fields**: The subset of an entity's fields that determine its identity. Everything else is descriptive and can grow
without changing what the entity is. *Avoid*: key fields, identity attributes, primary key

**Value Object**: An immutable type with no identity of its own, defined entirely by the values it carries and compared
by structural equality — `EntityNAMESPACE`, `FieldPattern`, `TextPatternSet`, `PatternSetID`. *Avoid*: DTO, model

**Namespace**: The per-kind UUID5 namespace an entity's id is computed under (`EntityNAMESPACE`). Two different kinds
carrying the same value never collide. *Avoid*: type tag

**Node**: An entity that is a thing rather than a connection: Person, Company, Address, Phone, Email, Cnae, Sanction,
TextSource. *Avoid*: vertex

**Edge**: A typed connection between two nodes, one dedicated class per kind of connection (`PersonOwnsCompany`,
`CompanyLocatedAt`). Which node kind may sit on each end is fixed at the type level. *Avoid*: relation, association

**Graph**: A root node with the nodes and edges reachable from it, validated whole at construction — a self-loop or an
edge pointing outside the node set is rejected there, never later. *Avoid*: result set

**Expansion**: The workflow that takes one official identifier (CPF, CNPJ, CEIS, CNEP) and returns a graph of everything
connected to it. *Avoid*: enrichment, crawl, search

**Batch**: One request expanding many CPFs at once, every expansion in its own transaction with its own outcome, so one
item's failure never discards another's paid fetch. *Avoid*: bulk

**Estimate**: The read-only pre-flight that sorts a batch's CPFs into three buckets — already fetched, billable or
invalid — so the caller learns which items would cost a provider call, and how long the provider's rate-limited queue
would hold the billable ones, before paying for any. *Avoid*: quote, preview

**Ingestion**: The workflow that scans free text for anything shaped like an official identifier, validates each
candidate by that format's own checksum rule, and links only exact resolutions. Never fuzzy. *Avoid*: parsing, scraping,
NER

**Pattern name**: One atomic, individually addressable recognition rule — a regex plus optional checksum validators for
one node type (`TextPatternName`, e.g. `CPF_LOOSE`). Chosen directly in a request or grouped into a pattern set.

**Pattern set**: A named shortcut bundling one or more pattern names under a single reusable id (`TextPatternSet`, e.g.
`brazilian_documents_v1`), resolved alongside any directly-named pattern in the same request rather than fixed at
startup, because providers format the same identifier differently. *Avoid*: ruleset, regex config, profile

**Stub**: A node carrying nothing but the identifier ingestion just recognized, created when that identifier is not yet
known. Expansion enriches it later; ingestion never touches a node that already exists. *Avoid*: placeholder, skeleton,
partial entity

**Revision**: An entity paired with when it was fetched, when it was merged, and which provider it came from
(`EntityRevision`). Provenance travels with the data; it is stamped by whatever performed the fetch, never by the
orchestrating workflow. *Avoid*: envelope

**Catalog**: Every distinct `root_id` ever fetched, grouped by that root rather than by `Graph.id` — a **Graph**'s id
changes the moment a new node is discovered under the same root, so grouping by it would lose that expansion's place in
the timeline (`GraphCatalogSchema`).

**Selection policy**: Decides which revision of the same entity counts as current. Default: newest `fetched_at`.
*Avoid*: conflict resolution, dedup rule

**Merge policy**: Decides how two revisions of the same entity reconcile into one when both carry data worth keeping.
Default: keeps the incoming revision as-is, no field synthesis — every revision stays distinct and stacked, one
immutable `Graph` snapshot per expansion/ingestion, readable back through its own history endpoint. The previous
field-filling default remains available for injection when a use case actually needs server-side reconciliation.
*Avoid*: combine, upsert rule

**Possible match**: An advisory edge (`PossiblyMatches`) between two `Person` nodes with distinct identities whose CPF
overlaps — every visible digit of a masked value agrees with the corresponding digit of another, complete or differently
masked, value — carrying the overlap as a confidence score. It never merges, re-identifies, or touches either node — the
judgment stays with whoever reviews the graph. *Avoid*: duplicate, alias, fuzzy match, candidate merge, name match

**Domain Service**: Stateless domain logic that operates on primitive or Value Object inputs but doesn't naturally
belong to any Entity or Value Object — `document_checksum`, `normalization`, `sanitization`. Distinct from the
application layer's own use of "Service" (`JWTService`, an injectable port for a technical capability): a Domain Service
has no interface and nothing to inject, and lives in `domain/`, never `application/contracts/`. *Avoid*: helper, util

**Fetcher**: The application-layer contract for one external endpoint (`CPFFetcher`, `CNPJFetcher`, `CEISFetcher`,
`CNEPFetcher`, `CEPFetcher`). The concrete client lives in infrastructure and this layer never names it. *Avoid*:
gateway, api wrapper

**Provider**: The external organization an identifier is fetched from — BrasilAPI, Portal da Transparência, KipFlow.
*Avoid*: data source, vendor

**External credential**: A caller's stored key for reaching a paid provider.

## Relationships

- A **Graph** holds one root **Node**, many **Nodes**, and many **Edges**
- An **Edge** connects exactly two **Nodes**, and both are **Entities**
- A **Revision** wraps one **Entity** and names one **Provider**
- A **Catalog** entry groups every **Revision** of every **Graph** sharing one root_id
- **Expansion** and **Ingestion** both produce a **Graph**
- A **Batch** runs many **Expansion**s, one outcome per item
- An **Estimate** classifies a **Batch**'s CPFs before any **Expansion** runs
- **Possible match** is an **Edge**, produced after **Expansion** or **Ingestion**, never during
- **Ingestion** creates a **Stub** only for an identifier no **Node** already carries
- A **Pattern set** groups one or more **Pattern name**s under one shortcut id

## Flagged ambiguities

- **"source" meant five things; two were the provider and are renamed.** `EntityRevision.source`, `Payload.source`, the
  `DataSourceError` family and `infrastructure/sources/` all meant the **Provider** and are now `provider`,
  `ProviderError` and `infrastructure/providers/`; the wire codes moved from `DATA_SOURCE_*` to `PROVIDER_*`. The three
  that stay are distinct concepts, not drift: `TextSource` (a node holding ingested text), `Edge.source_id` (an edge's
  origin node), and `source` meaning source code in the `scripts/` tests.

- **"bundle" carried two senses.** Early glossary work discarded it as a synonym for **Graph** (`result set`, `bundle`).
  The pattern-set repository (`list_bundles`, the `bundles` field) later claimed it for real, naming the same concept as
  **Pattern set** — a named shortcut grouping pattern names. That sense won; **Graph**'s `*Avoid*` list drops `bundle`.
