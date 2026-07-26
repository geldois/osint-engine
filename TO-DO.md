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

## feat(ceis)

- CEIS (Cadastro de Empresas Inidôneas e Suspensas) sanctions are not yet implemented — only CNEP is (see [ADR-0019](docs/adr/0019-portal-transparencia-as-cnep-ceis-sanctions-source.md)); `Sanction.organ` already accepts `Literal["CEIS", "CNEP"]`, so follow the same `PortalTransparenciaFetcher` subclassing pattern as `PortalTransparenciaCNEPFetcher`/`cnep_mapper` for the CEIS endpoint, and decide whether it joins `ExpandByCNEP` or becomes its own use case

## feat(cep)

- `BrasilAPICEPv2Fetcher`/`cep_v2_mapper` are built and fully tested but unwired — no use case calls `CEPFetcher.fetch(cep, number)` yet; the intended consumer is roadmap step 3 (text ingestion), which supplies `number` from regex extraction and uses this fetcher to fill in city/state/neighborhood/street around it; do not chain it from `cnpj_v1`, whose `_map_address` already returns a complete `Address`

## feat(persistence)

- make commits atomic across PostgreSQL credentials and the in-memory graph/user
  snapshot; `HybridUoW` intentionally persists credentials during repository
  `save()` and only coordinates the in-memory snapshot during `commit()`
