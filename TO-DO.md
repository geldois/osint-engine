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
  see [ADR-0029](docs/adr/0029-stub-and-link-text-ingestion-over-external-refetch.md), it never calls external APIs,
  only stubs-and-links by deterministic id. This fetcher's actual consumer is still undecided: a manual "enrich this
  Address stub" endpoint is the likely shape, not automatic chaining from `cnpj_v1` (whose `_map_address` already
  returns a complete `Address`)

## feat(cpf)

- `GET /cpf/{cpf}` is fully implemented, tested, and wired (mirrors CNPJ's architecture exactly), but the Portal da
  Transparência `/pf` endpoint currently rejects our API key with a bare `403` at the CloudFront edge (confirmed via
  direct `curl` against `api.portaldatransparencia.gov.br`, bypassing osint-engine entirely — same key works fine for
  `/cnep`/`/ceis`). Not a code defect: `ExternalCredentialRejectedError` classifies it correctly. Account already holds
  gov.br selo Ouro, so it isn't a trust-seal gap; root cause is still unconfirmed (undocumented restricted-API tier?
  per-endpoint scope grant?). Next step is external, via Fala.BR — revisit once the Portal da Transparência responds

## feat(persistence)

- make commits atomic across PostgreSQL credentials and the in-memory graph/user snapshot; `HybridUoW` intentionally
  persists credentials during repository `save()` and only coordinates the in-memory snapshot during `commit()`

## feat(text-ingestion)

- `PossiblyMatches` (fuzzy cross-entity similarity edge) has no Pydantic schema, no `EdgeSchemaRegistry` entry, and no
  `_EDGE_MAP` entry — unlike the three `*MentionedInText` edges shipped alongside it, which are fully wired. It's dead
  code today (zero constructors outside its own definition), so this is a landmine, not a live bug: the moment a future
  fuzzy-matching feature (spec 2, see the open thread in `~/.brain/RESUME.md`) starts emitting `PossiblyMatches` edges
  into a graph that reaches the HTTP layer, `edge_to_schema` 500s instead of returning 200. Wire it up as part of that
  spec, not speculatively now — the confidence-scoring/registry-dispatch shape it needs isn't designed yet

## fix(rate-limit)

- expansion buckets are a flat 100/min per route, but Portal da Transparência's token ceiling is 90/min from 06:00–23:59
  (higher overnight); with three Portal-backed routes (`/cpf`, `/cnep`, `/ceis`) the aggregate can exceed that ceiling,
  so the per-route limiter protects this server but not the shared upstream token — Portal may `429` the token first
  under load. Deliberate for the visitor-only demo; tighten to a combined cross-route Portal bucket under 90/min if real
  traffic trips it

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
  once, then pin the coverage floor and mutation `--max-survival` ceiling to the measured baseline, ratcheting only
  (ADR 0025)
