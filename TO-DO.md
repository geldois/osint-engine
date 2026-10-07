# TO-DO

Every deferral, workaround, accepted limit, placeholder and unwired piece in this repository. Each bullet says what is
open, where it lives, what leaving it costs and what would make it worth doing. A gap found while working goes here in
the same commit; a gap closed comes out in the same commit.

## feat(persistence)

- **All graph, user and consumption-log data lives in a plain in-memory snapshot** (`MemStorage` behind `HybridUoW`).
  Every restart loses it, and there is no coordination between concurrent writers, so the service is a single process by
  construction. Only external credentials survive, because they sit in PostgreSQL. The replacement is a real graph or
  relational adapter behind the existing repository contracts (a Neo4j migration is the stated direction); the layers
  above never see which store answers, so the risk stays inside infrastructure. Do it before any real second user or any
  data that must outlive a deploy
- **`Graph.nodes` and `Graph.edges` hold full `Node`/`Edge` content, not references.** Every stored `GraphRevision`
  re-embeds the complete content of every node and edge it holds, even ones unchanged since the previous revision. The
  node and edge repositories already dedupe by `content_id`; the graph repository does not reuse that. A reference-based
  redesign (`Graph` holding an `EntityRef` per node and edge, resolved against those repositories at read time, behind a
  new application-layer value object so no interface code touches a repository) was fully specified and deferred: it
  touches every expansion, estimate and ingestion use case under `application/use_cases/expansion/` (twelve today, among
  them `ExpandByCPF`, `ExpandByCPFBatch`, `ExpandByCNPJ`, `ExpandByCEAF`, `ExpandByCEIS`, `ExpandByCEPIM`,
  `ExpandByCNEP`, `ExpandByPEP`, `ExpandByLegalProcess`, `EstimateCPFBatch`, `IngestText`, `FindPossiblyMatches`), every
  fetcher, every graph-shaped presenter, the mem seeder and the whole domain test suite for `Graph`. Not a narrow change
- **Commits are not atomic across PostgreSQL credentials and the in-memory snapshot.** `HybridUoW` persists credentials
  during repository `save()` and only coordinates the snapshot during `commit()`. The reuse lock and the consumption log
  inherit the same gap, and so does any future workflow that writes to both: it must account for it, because nothing
  enforces it (`docs/architecture/application.md`, Consequences)
- **`GraphRepository.list_all_revisions()` is a full scan.** In `MemStorage` it costs what `list_revisions_by_root`
  already costs, but a Neo4j or Postgres adapter needs an aggregated projection instead of replaying the scan per
  `GET /graphs` request. The projection was not designed up front because it would mean guessing a storage that does not
  exist yet. When that adapter lands, `list_all_revisions` is the one method to replace, and `ListGraphCatalog` is its
  only caller
- **The committed `generated/` sqlc models can drift from `migrations/` and `queries/*.sql`.** `scripts sqlc-generate`
  is manual and not part of `check`, so nothing fails if someone changes a query or a migration and forgets to
  regenerate. A gate that regenerates into a temporary directory and diffs would close it

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
- **The list of named spreadsheet-corruption failures is only what has been reproduced**, with a broad catch beneath it.
  A new corruption shape is reported generically until someone reproduces it and names it
  (`docs/architecture/infrastructure.md`)

## feat(text-ingestion)

- **The loose, label-free patterns (`CNPJ_LOOSE` and its siblings) can match a checksum coincidence.** Accepted as a
  false-positive risk because they are opt-in; it is a precision limit, not a bug
- **Two identical subjects revealed with different hidden digits are never auto-relinked**
  (`docs/architecture/domain.md`, Consequences). The relinking is left to "something else", and no workflow does it
  today

## fix(text-ingestion)

- **A text-ingested `Person` stub stores its `cpf` exactly as the regex matched it**, whatever punctuation the source
  used. `Person.id` comes from normalized digits, so a later ingestion of the same CPF in another format resolves to the
  same entity and is only linked, never merged, which makes the first-seen format permanent. Cosmetic: identity
  resolution is unaffected. Fixing it means giving `_resolve_node` a path to update an existing entity's field from a
  new deterministic match, which the design deliberately does not do for anything. Revisit only if it surfaces as a real
  complaint

## fix(api)

- **`GET /graphs` returns every graph the process holds, with no owner.** `MemStorage` never records which user
  originated a revision, and no expansion route writes one. Invisible with a single demo operator; with a second real
  user the catalog becomes a cross-account leak and the route needs scoping before it goes public
- **`GET /graphs` has no pagination.** `entries` sits in the dozens for a demo. Past a few hundred, the route needs
  `limit` and `cursor` and the studio client needs to handle a partial response; not designed ahead of the need, since
  the shape depends on how the client consumes it
- **`GET /credentials/{provider}/reveal` returns a stored API key decrypted over HTTP** to its ADMIN owner. The
  trade-off (the studio can show a key back, at the price of exposing it in a response body and any log in front of it)
  is not recorded in `docs/architecture/`; decide whether to keep it, mask it, or write the decision down
- **`/health` and `/health/ready` do not report which commit is running.** After a deploy the pipeline proves the
  process answers, not that it is the verified commit. Exposing the build SHA would let the pipeline compare it to
  `${{ github.sha }}`

## fix(rate-limit)

- **Expansion buckets are a flat 100/min per route (`_EXPANSION_REQUESTS_PER_MINUTE`)**, but Portal da Transparência's
  token ceiling is 90/min from 06:00 to 23:59 (higher overnight). With five Portal-backed routes (`/cnep`, `/ceis`,
  `/cepim`, `/ceaf`, `/peps`) the aggregate can exceed it, so the limiter protects this server but not the shared
  upstream token, and Portal may `429` first under load. Deliberate for the visitor-only demo; replace with a combined
  cross-route Portal bucket under 90/min if real traffic trips it
- **The `fastapi-throttle` limiter and the KipFlow pacing queue are per process and in memory.** They do not scale past
  one instance, and a restart resets every bucket to full, so a batch estimate given just before a restart can
  undercount the real wait (`docs/architecture/infrastructure.md`)

## test(providers)

- **KipFlow's fetchers and mappers have no live-snapshot contract test.** The `real_api_snapshot` tests cover BrasilAPI
  and Portal da Transparência only, and `tests/test_scripts/test_fixtures_coverage.py` excludes the paid provider on
  purpose, so CPF and legal-process mapping against the real paid response is never verified. Record a snapshot by hand
  once with a real key, or accept it explicitly

## test(gates)

- **`fail_under = 90` in `[tool.coverage.report]` is a placeholder, not a measured value.** A human runs
  `uv run python -m scripts check` (needs Docker) and `uv run python -m scripts mutation` once, then pins the coverage
  floor and the mutation ceiling to the measured baseline and only ratchets from there
- **`scripts mutation --max-survival` defaults to `100.0`, so the mutation gate can never fail today**, and no workflow
  runs it. After measuring the baseline: set the ceiling, then add a scheduled (weekly) and manual CI job for it. Until
  the ceiling is real, a scheduled job would be a false green
- **`cosmic-ray.toml` was pointing at test directories that do not exist** (fixed to `tests/test_src/test_domain` and
  `tests/test_src/test_application`); the mutation run itself has never been exercised since, so expect a first run to
  need adjustments

## chore(gates)

- **Local enforcement depends on one manual step per clone**: `git config --local include.path ../.gitconfig`. A clone
  that skips it runs no hook at all. `--no-verify`, `git rebase` and `git cherry-pick` also skip the hook. Only CI and a
  protected `main` close that gap
- **A partial commit needs the rest of the tree stashed**, because the hook refuses unstaged or untracked files; a run
  of split commits pays for the full gate each time (around a minute)
- **The uv version lives in three places**: `required-version` in `[tool.uv]` (a range, `>=0.11.21,<0.12`, so a
  distro-packaged uv still works and the workflows float within 0.11), the `build` extra that lets semantic-release
  install uv (`==0.11.25`), and the `Dockerfile`'s uv image tag (0.11.25). uv refuses to run outside the range, so a
  drifted copy fails loudly, but the two exact pins still move together. The workflows read the range through `setup-uv`
  and whether that action accepts this range syntax is unconfirmed until the first CI run
- **dprint downloads its plugins from `plugins.dprint.dev` on first run**, so the very first gate on a fresh machine
  needs network access beyond PyPI. The workflow linter runs from a pinned Docker image because its Python wrapper only
  ships a source distribution that downloads a binary at install time
- **`shfmt` comes from the `shfmt-py` wheel, which bundles shfmt 3.14.1**, not the 3.13.1 the repo used before; the
  wrapper's own version number does not track the tool's

## chore(ci)

- **`main` has no branch protection or ruleset.** Without them, anything can still reach `main` without having passed
  the gate. In the GitHub web UI: repository Settings, Rules, Rulesets, New branch ruleset, target `main`; enable
  "Require status checks to pass" and add the check `test`, "Require linear history", "Block force pushes" and "Restrict
  deletions", and leave bypass empty so admins are bound too. The check name `test` comes from the job in `test.yml` and
  should be confirmed in a real run before relying on it
- **`vars.API_DOMAIN` is still set to a stale domain** (`api.osint.angelitochagas.com`) while the host serves
  `osint-engine.duckdns.org`; the deploy job fails fast and says so until
  `gh variable set API_DOMAIN --body osint-engine.duckdns.org -R geldois/osint-engine` is run
- **`test.yml` runs the whole gate on a single runner and architecture** (`ubuntu-24.04`), while the image is built for
  amd64 and arm64; nothing exercises the arm64 image beyond the build

## chore(deployment)

- **Automatic reboot is disabled**, so a pending kernel update stays pending until someone reboots the host by hand
- **`IMAGE_TAG` is left empty by provisioning**, so the first `docker compose up` on every new host is manual
- **The `app`-to-Postgres link has TLS off** (`sslmode=disable`), safe only while the database stays on the
  compose-internal network
- **The generated admin password must be reviewed and rotated by hand** in the same session as the first deploy

## chore(persistence)

- **`migrate.py` passes `-path migrations`, relative to the working directory.** It only resolves because the Dockerfile
  sets `WORKDIR /app` and copies `migrations/` there; an installation from a wheel run outside the repo or container
  root fails, since `migrations/` is not package data. Fine for the Docker-only target; revisit if another install path
  is ever needed

## chore(harness)

- **The deny list matches command text**, so a wrapper shell or an absolute path to a tool can still run one. A guard
  against the usual form, not a boundary
- **A change made only through a shell command** (`mv`, `rm`, code generation) writes no docs-review mark, so it can
  skip the end-of-turn review
- **The docs-review marker is shared by every session in the same checkout**; two agents at once can consume each
  other's mark
- **The shared contract with `osint-studio` is written down nowhere.** The review prompt asks to check that repo's docs
  when the contract moves, but no document says what the contract is or where its source of truth lives

## chore(config)

- **`.env.example` sets `FETCHER_CONNECT_TIMEOUT=30.0`, while the code default is `15.0`.** Decide which is intended and
  align them
