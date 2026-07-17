# TO-DO

## chore(ci)

- install Renovate GitHub App on geldois/osint-engine and push `renovate.json` to enable automated dependency updates
for actions, uv, and pre-commit hooks

## feat(cep)

- `BrasilAPICEPv2Fetcher`/`cep_v2_mapper` are built and fully tested but unwired — no use case calls `CEPFetcher.fetch(cep, number)` yet; the intended consumer is roadmap step 3 (text ingestion), which supplies `number` from regex extraction and uses this fetcher to fill in city/state/neighborhood/street around it; do not chain it from `cnpj_v1`, whose `_map_address` already returns a complete `Address`
