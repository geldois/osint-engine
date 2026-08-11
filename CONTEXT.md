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
edge pointing outside the node set is rejected there, never later. *Avoid*: result set, bundle

**Expansion**: The workflow that takes one official identifier (CPF, CNPJ, CEIS, CNEP) and returns a graph of everything
connected to it. *Avoid*: enrichment, crawl, search

**Ingestion**: The workflow that scans free text for anything shaped like an official identifier, validates each
candidate by that format's own checksum rule, and links only exact resolutions. Never fuzzy. *Avoid*: parsing, scraping,
NER

**Pattern set**: The set of recognition patterns ingestion runs against the text, chosen per request rather than fixed
at startup, because providers format the same identifier differently. *Avoid*: ruleset, regex config, profile

**Stub**: A node carrying nothing but the identifier ingestion just recognized, created when that identifier is not yet
known. Expansion enriches it later; ingestion never touches a node that already exists. *Avoid*: placeholder, skeleton,
partial entity

**Revision**: An entity paired with when it was fetched, when it was merged, and which provider it came from
(`EntityRevision`). Provenance travels with the data; it is stamped by whatever performed the fetch, never by the
orchestrating workflow. *Avoid*: envelope

**Selection policy**: Decides which revision of the same entity counts as current. Default: newest `fetched_at`.
*Avoid*: conflict resolution, dedup rule

**Merge policy**: Decides how two revisions of the same entity reconcile into one when both carry data worth keeping.
*Avoid*: combine, upsert rule

**Possible match**: An advisory edge (`PossiblyMatches`) between two nodes with distinct identities but strongly similar
names, carrying a similarity score. It never merges, re-identifies, or touches either node — the judgment stays with
whoever reviews the graph. *Avoid*: duplicate, alias, fuzzy match, candidate merge

**Domain Service**: Stateless domain logic that operates on primitive or Value Object inputs but doesn't naturally
belong to any Entity or Value Object — `document_checksum`, `normalization`. Distinct from the application layer's own
use of "Service" (`JWTService`, an injectable port for a technical capability): a Domain Service has no interface and
nothing to inject, and lives in `domain/`, never `application/contracts/`. *Avoid*: helper, util

**Fetcher**: The application-layer contract for one external endpoint (`CPFFetcher`, `CNPJFetcher`, `CEISFetcher`,
`CNEPFetcher`, `CEPFetcher`). The concrete client lives in infrastructure and this layer never names it. *Avoid*:
gateway, api wrapper

**Provider**: The external organization an identifier is fetched from — BrasilAPI, Portal da Transparência. *Avoid*:
data source, vendor

**External credential**: A caller's stored key for reaching a paid provider.

## Relationships

- A **Graph** holds one root **Node**, many **Nodes**, and many **Edges**
- An **Edge** connects exactly two **Nodes**, and both are **Entities**
- A **Revision** wraps one **Entity** and names one **Provider**
- **Expansion** and **Ingestion** both produce a **Graph**
- **Possible match** is an **Edge**, produced after **Expansion** or **Ingestion**, never during
- **Ingestion** creates a **Stub** only for an identifier no **Node** already carries

## Flagged ambiguities

- **"source" meant five things; two were the provider and are renamed.** `EntityRevision.source`, `Payload.source`, the
  `DataSourceError` family and `infrastructure/sources/` all meant the **Provider** and are now `provider`,
  `ProviderError` and `infrastructure/providers/`; the wire codes moved from `DATA_SOURCE_*` to `PROVIDER_*`. The three
  that stay are distinct concepts, not drift: `TextSource` (a node holding ingested text), `Edge.source_id` (an edge's
  origin node), and `source` meaning source code in the `scripts/` tests.
