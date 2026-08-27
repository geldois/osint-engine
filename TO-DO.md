# TO-DO

## chore(ci)

- install Renovate GitHub App on geldois/osint-engine and push `renovate.json` to enable automated dependency updates
  for actions and uv

## chore(persistence)

- `migrate.py`'s `-path migrations` is relative to the current working directory; it only resolves correctly because the
  Dockerfile sets `WORKDIR /app` and copies `migrations/` there — an `osint-engine` installed from a wheel and run
  outside the repo/container root fails, since `migrations/` isn't packaged as package data; fine for the current
  Docker-only deployment target, revisit if a non-container install path is ever needed

## feat(cep)

- `BrasilAPICEPv2Fetcher`/`cep_v2_mapper` are built and fully tested but unwired — no use case calls
  `CEPFetcher.fetch(cep, number)` yet. Text ingestion (roadmap step 3, shipped) deliberately does *not* consume this —
  see `docs/architecture/application.md`, it never calls external APIs, only stubs-and-links by deterministic id. This
  fetcher's actual consumer is still undecided: a manual "enrich this Address stub" endpoint is the likely shape, not
  automatic chaining from `cnpj_v1` (whose `_map_address` already returns a complete `Address`)

## feat(persistence)

- `Graph.nodes`/`Graph.edges` hold full `Node`/`Edge` content, not references — every stored `GraphRevision` re-embeds
  the complete content of every node and edge it holds, even ones unchanged since the previous revision. Node/edge
  repositories already dedupe correctly by `content_id`; the graph repository doesn't reuse that, so it's the one place
  in this system's storage doing more work than it needs to. A reference-based redesign (`Graph` holding an `EntityRef`
  per node/edge, resolved against the node/edge repositories at read time, behind a new application-layer value object
  so no interface-layer code ever touches a repository) was fully specified but deferred: it touches every one of the 9
  expansion use cases (`ExpandByCPF`, `ExpandByCPFBatch`, `ExpandByCNPJ`, `ExpandByCEAF`, `ExpandByCEIS`,
  `ExpandByCEPIM`, `ExpandByCNEP`, `IngestText`, `FindPossiblyMatches`), every fetcher, every graph-shaped presenter,
  the mem seeder, and the full domain test suite for `Graph` — not a narrow, single-path change
- make commits atomic across PostgreSQL credentials and the in-memory graph/user snapshot; `HybridUoW` intentionally
  persists credentials during repository `save()` and only coordinates the in-memory snapshot during `commit()`
- `GraphRepository.list_all_revisions()` is a full scan; in `MemStorage` it costs the same as `list_revisions_by_root`
  already does, but a future Neo4j/Postgres adapter needs an aggregated projection instead of replaying this scan per
  `GET /graphs` request — the projection wasn't designed up front because doing so against a storage that doesn't exist
  yet would mean guessing its shape; when that adapter lands, `list_all_revisions` is the one method to replace, and
  `ListGraphCatalog` is its only caller

## feat(sanctions)

- CEPIM's `convenio` (`DimConvenioDTO`: `codigo`/`objeto`/`numero`) and CEAF's `cargoEfetivo`/`codigoCargoComissao`/
  `cargoComissao`/`punicao.portaria`/`punicao.paginaDOU`/`punicao.secaoDOU` are real fields in the upstream payload with
  no matching field on the `Sanction` node — mapping them would mean extending the entity for a case specific to only
  two of the four sanction sources; not done, dropped silently by `cepim_mapper.py`/`ceaf_mapper.py`

## feat(spreadsheet-ingestion)

- `_read_csv` splits rows on a fixed `,` delimiter with no `;`-sniffing; a `;`-delimited export (common from PT-BR
  Excel) degrades cell-level granularity to line-level, though CPF/CNPJ extraction is unaffected since neither pattern
  depends on cell boundaries — revisit only if a real file makes this an actual problem

## fix(api)

- `GET /graphs` returns every graph the process holds, with no notion of owner — `MemStorage` never records which user
  originated a revision, and no expansion route writes one. Invisible with a single demo operator; the moment a second
  real user exists, the catalog becomes a cross-account leak and the route needs scoping before it goes public
- `GET /graphs` has no pagination; `entries` sits in the dozens for a demo. If the catalog grows past a few hundred
  before the Neo4j migration, the route needs `limit`/`cursor` and the studio client needs to handle a partial response
  — not designed ahead of the need, since the shape depends on how the client ends up consuming it

## fix(cpf-reuse-lock)

- `ExpandByCPF`'s reuse lock (see `docs/architecture/application.md`) records a `provider="kipflow"` node revision
  explicitly, but that record still passes through `NodeRepository.merge()`'s configured merge policy — under the
  shipped `keep_incoming_policy` this always wins, so the lock is sound in production today.
  `merge_by_filled_fields_policy` (already implemented, already injectable via `Policies`, just never wired in
  `croot.py`) can discard the explicit "kipflow" tag back to an older provider's tag when the KipFlow response happens
  to add no new field beyond what an existing revision from a different provider already had (e.g. a CPF also known as a
  company's sócio via BrasilAPI, paired with KipFlow's documented bare response shape carrying no field beyond `cpf`
  itself) — in that specific combination the lock silently never arms, allowing unlimited repeat KipFlow billing for
  that CPF. Not exploitable while `croot.py` only wires `keep_incoming_policy`; revisit before ever wiring
  `merge_by_filled_fields_policy` into a deployment that also uses KipFlow

## fix(rate-limit)

- expansion buckets are a flat 100/min per route, but Portal da Transparência's token ceiling is 90/min from 06:00–23:59
  (higher overnight); with four Portal-backed routes (`/cnep`, `/ceis`, `/cepim`, `/ceaf`) the aggregate can still
  exceed that ceiling, so the per-route limiter protects this server but not the shared upstream token — Portal may
  `429` the token first under load. Deliberate for the visitor-only demo; tighten to a combined cross-route Portal
  bucket under 90/min if real traffic trips it

## fix(text-ingestion)

- A text-ingested `Person` stub's `cpf` field stores the raw regex-matched text verbatim (whatever punctuation the
  source document happened to use). Since `Person.id` is derived from normalized digits, a later ingestion mentioning
  the same CPF in different formatting resolves to the same entity and is only linked, never merged — so whichever
  format arrived first is permanent. Purely cosmetic (identity resolution itself is unaffected, always correct); fixing
  it would mean giving `_resolve_node` a path to update an *existing* entity's own field from a new deterministic match,
  which the current design deliberately doesn't do for anything, cosmetic or not — revisit only if this formatting
  inconsistency actually surfaces as a real complaint

## test(gates)

- `fail_under` in `[tool.coverage.report]` is a placeholder `90`, not a measured value; run
  `python -m scripts check
  --full` (needs Docker + `PORTAL_TRANSPARENCIA_API_KEY`) and `python -m scripts mutation`
  once, then pin the coverage floor and mutation `--max-survival` ceiling to the measured baseline, ratcheting only (see
  the Quality gates section in this project's `CLAUDE.md`)
