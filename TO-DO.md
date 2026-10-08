# TO-DO

Open problems only: each bullet names where it lives, what leaving it costs and what would make it worth doing. A limit
accepted by design belongs in `docs/architecture/` (Consequences), not here. A gap found while working goes here in the
same commit; a gap closed comes out in the same commit.

## feat(persistence)

- **All graph and consumption-log data lives in a plain in-memory snapshot** (`MemStorage` behind `HybridUoW`). Every
  restart loses it, there is no coordination between concurrent writers, and the `fastapi-throttle` limiter and the
  KipFlow pacing queue are in memory too, so the service is a single process by construction and a restart resets every
  rate bucket. Only accounts and external credentials survive, because they sit in PostgreSQL. The replacement is a real
  graph or relational adapter behind the existing repository contracts (a Neo4j migration is the stated direction); the
  layers above never see which store answers. When it lands, `GraphRepository.list_all_revisions()` (a full scan today,
  with `ListGraphCatalog` as its only caller) is the one method to replace with an aggregated projection. Do it before
  any data that must outlive a deploy
- **`Graph.nodes` and `Graph.edges` hold full `Node`/`Edge` content, not references.** Every stored `GraphRevision`
  re-embeds the complete content of every node and edge it holds, even ones unchanged since the previous revision. The
  node and edge repositories already dedupe by `content_id`; the graph repository does not reuse that. A reference-based
  redesign (`Graph` holding an `EntityRef` per node and edge, resolved against those repositories at read time, behind a
  new application-layer value object so no interface code touches a repository) was fully specified and deferred: it
  touches every expansion, estimate, ingestion and matching use case under `application/use_cases/` (twelve today across
  `expansion/`, `text_ingestion/` and `matching/`), every fetcher, every graph-shaped presenter, the mem seeder and the
  whole domain test suite for `Graph`. Not a narrow change
- **Commits are not atomic across PostgreSQL credentials and the in-memory snapshot.** `HybridUoW` persists credentials
  during repository `save()` and only coordinates the snapshot during `commit()`. The reuse lock and the consumption log
  inherit the same gap, and so does any future workflow that writes to both (`docs/architecture/application.md`,
  Consequences)
- **The committed `generated/` sqlc models can drift from `migrations/` and
  `infrastructure/persistence/pg/queries/*.sql`.** `scripts sqlc-generate` is manual and not part of `check`, so nothing
  fails if someone changes a query or a migration and forgets to regenerate. A gate that regenerates and compares would
  close it, but sqlc's own comparison also reports the unused querier file this repo discards, so it needs a wrapper

## feat(cep)

- **`BrasilAPICEPv2Fetcher` and `cep_v2_mapper` are built and fully tested but unwired.** No use case calls
  `CEPFetcher.fetch(cep, number)`. Text ingestion deliberately does not consume it (it never calls external APIs, only
  stubs and links by deterministic id; see `docs/architecture/application.md`). The likely consumer is a manual "enrich
  this Address stub" endpoint, not automatic chaining from `cnpj_v1`, whose `_map_address` already returns a complete
  `Address`. Decide the consumer or delete the fetcher

## feat(sanctions)

- **CEPIM's `convenio` and CEAF's `cargoEfetivo`, `codigoCargoComissao`, `cargoComissao`, `punicao.portaria`,
  `punicao.paginaDOU` and `punicao.secaoDOU` are real upstream fields with no counterpart on the `Sanction` node.**
  `cepim_mapper.py` and `ceaf_mapper.py` drop them silently, because mapping them would extend the entity for something
  specific to two of the four sanction sources. Revisit if a consumer needs those details

## feat(spreadsheet-ingestion)

- **`_read_csv` splits on a fixed `,`.** A `;`-delimited export (common from PT-BR Excel) degrades cell-level
  granularity to line-level; CPF and CNPJ extraction is unaffected because neither pattern depends on cell boundaries.
  Add delimiter sniffing only if a real file makes it a problem

## feat(text-ingestion)

- **Two identical subjects revealed with different hidden digits are never auto-relinked**
  (`docs/architecture/domain.md`, Consequences). The relinking is left to "something else", and no workflow does it
  today

## fix(text-ingestion)

- **A text-ingested `Person` stub stores its `cpf` exactly as the regex matched it**, whatever punctuation the source
  used. `Person.id` comes from normalized digits, so a later ingestion of the same CPF in another format resolves to the
  same entity and is only linked, never merged, which makes the first-seen format permanent. Cosmetic: identity
  resolution is unaffected. Fixing it means giving `_resolve_node` a path to update an existing entity's field from a
  new deterministic match, which the design deliberately does not do for anything

## fix(api)

- **Every authenticated account reads every stored graph.** `GET /graphs`, `/graphs/{root_id}/history`,
  `/nodes/{node_id}/history` and `/edges/{edge_id}/history` return whatever any account ever expanded, with no owner and
  no pagination, because `MemStorage` never records which user originated a revision. Signup is now open, so a second
  account sees the CPF data a first account paid KipFlow for, and ids are deterministic from the CPF, so they can be
  guessed. Fix before opening signup to anyone untrusted: record the owner on each revision (or on a per-user index of
  root ids), filter every history route by it, and add `limit` and `cursor` once the catalog passes a few hundred
  entries, with the studio client handling a partial response
- **`GET /credentials/{provider}/reveal` returns a stored API key decrypted over HTTP** to its owner. The trade-off (the
  studio can show a key back, at the price of exposing it in a response body and any log in front of it) is not recorded
  in `docs/architecture/`; decide whether to keep it, mask it, or write the decision down
- **`/health` and `/health/ready` do not report which commit is running.** After a deploy the pipeline proves the
  process answers, not that it is the verified commit. Exposing the build SHA would let the pipeline compare it to
  `${{ github.sha }}`

## feat(auth)

- **Accounts have no password reset, no deletion and no email or other proof of ownership**
  (`application/use_cases/authentication/register_user.py`). A forgotten password locks the account and its saved keys
  for good, and open signup is bounded only by the 10-per-15-minutes IP limit and argon2's cost. Add an invite code (an
  environment value checked at registration) first if signup abuse shows up; a reset flow needs an email channel the
  project does not have

## fix(rate-limit)

- **Expansion buckets are a flat 100/min per route and per user (`_EXPANSION_REQUESTS_PER_MINUTE`)**, but Portal da
  Transparência's token ceiling is 90/min from 06:00 to 23:59 (higher overnight). With five Portal-backed routes
  (`/cnep`, `/ceis`, `/cepim`, `/ceaf`, `/peps`) the aggregate can exceed it, so the limiter protects this server but
  not the user's upstream key, and Portal may `429` first under load. Each account now spends its own bucket against its
  own Portal key; replace with a combined per-user cross-route Portal bucket under 90/min if real traffic trips it

## test(providers)

- **KipFlow's fetchers and mappers have no live-snapshot contract test.** The `real_api_snapshot` tests cover BrasilAPI
  and Portal da Transparência only, and `tests/test_scripts/test_fixtures_coverage.py` excludes the paid provider on
  purpose, so CPF and legal-process mapping against the real paid response is never verified. Record a snapshot by hand
  once with a real key, or accept it explicitly

## test(gates)

- **The mutation gate has never run.** `scripts mutation --max-survival` defaults to `100.0`, so it can never fail, no
  workflow runs it, and `cosmic-ray.toml` was only just pointed at the real test directories, so expect a first run to
  need adjustments. Run it once, set the ceiling to the measured baseline, then add a scheduled weekly and manual CI
  job; until the ceiling is real, a scheduled job would be a false green

## chore(gates)

- **The uv version lives in three places**, all exactly `0.11.21`: `required-version` in `[tool.uv]` (the one the
  workflows read and that uv enforces everywhere it runs), the `build` extra that lets semantic-release install uv, and
  the `Dockerfile`'s uv image tag and digest. A drifted copy fails loudly, but the three still move together

## chore(ci)

- **`main` has no branch protection or ruleset.** Without them, anything can still reach `main` without having passed
  the gate. In the GitHub web UI: repository Settings, Rules, Rulesets, New branch ruleset, target `main`; enable
  "Require status checks to pass" and add the check `test` (it must have run once on a pushed branch to appear), keep
  "Require linear history", "Block force pushes" and "Restrict deletions", and leave bypass empty so admins are bound
  too

## chore(harness)

- **The shared contract with `osint-studio` is written down nowhere.** The review prompt asks to check that repo's docs
  when the contract moves, but no document says what the contract is or where its source of truth lives
