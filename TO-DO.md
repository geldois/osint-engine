# TO-DO

## chore(ci)

- install Renovate GitHub App on geldois/osint-engine and push `renovate.json` to enable automated dependency updates
for actions, uv, and pre-commit hooks

## chore(persistence)

- `migrate.py`'s `-path migrations` is relative to the current working directory; it only
  resolves correctly because the Dockerfile sets `WORKDIR /app` and copies `migrations/`
  there — an `osint-engine` installed from a wheel and run outside the repo/container root
  fails, since `migrations/` isn't packaged as package data; fine for the current
  Docker-only deployment target, revisit if a non-container install path is ever needed

## feat(cep)

- `BrasilAPICEPv2Fetcher`/`cep_v2_mapper` are built and fully tested but unwired — no use case calls `CEPFetcher.fetch(cep, number)` yet; the intended consumer is roadmap step 3 (text ingestion), which supplies `number` from regex extraction and uses this fetcher to fill in city/state/neighborhood/street around it; do not chain it from `cnpj_v1`, whose `_map_address` already returns a complete `Address`

## feat(cpf)

- `GET /cpf/{cpf}` is fully implemented, tested, and wired (mirrors CNPJ's
  architecture exactly), but the Portal da Transparência `/pf` endpoint
  currently rejects our API key with a bare `403` at the CloudFront edge
  (confirmed via direct `curl` against `api.portaldatransparencia.gov.br`,
  bypassing osint-engine entirely — same key works fine for `/cnep`/`/ceis`).
  Not a code defect: `ExternalCredentialRejectedError` classifies it
  correctly. Account already holds gov.br selo Ouro, so it isn't a trust-seal
  gap; root cause is still unconfirmed (undocumented restricted-API tier?
  per-endpoint scope grant?). Next step is external, via Fala.BR — revisit
  once the Portal da Transparência responds

## feat(persistence)

- make commits atomic across PostgreSQL credentials and the in-memory graph/user
  snapshot; `HybridUoW` intentionally persists credentials during repository
  `save()` and only coordinates the in-memory snapshot during `commit()`

## fix(rate-limit)

- expansion buckets are a flat 100/min per route, but Portal da Transparência's token ceiling is 90/min from
  06:00–23:59 (higher overnight); with three Portal-backed routes (`/cpf`, `/cnep`, `/ceis`) the aggregate can exceed
  that ceiling, so the per-route limiter protects this server but not the shared upstream token — Portal may `429` the
  token first under load. Deliberate for the visitor-only demo; tighten to a combined cross-route Portal bucket under
  90/min if real traffic trips it
