# Query-param collection plus by-id endpoint for CNEP/CEIS

## Status

Accepted

## Context

`PortalTransparenciaCNEPFetcher` (ADR-0019) was built and unit-tested exclusively against `MockTransport`, never against
the live Portal da Transparência API. It requested `GET /api-de-dados/cnep/{cpf_or_cnpj}[/{cnep_id}]`, assuming
path-segment identification analogous to BrasilAPI. Implementing `ExpandByCEIS` against the real API (needed since
`CeisDTO`'s Swagger schema was now available) surfaced that this request shape returns
`400 {"Erro na API":"Erro ao executar a consulta"}` — the existing CNEP integration had never actually worked in
production.

Live testing against the real API showed two distinct endpoints instead: a collection endpoint
(`GET /cnep?codigoSancionado=...&pagina=1`, `pagina` required, a trailing slash before `?` returns 403) returning a JSON
array of every sanction matching the CPF/CNPJ, and a by-id endpoint (`GET /cnep/{id}`) returning a single record, where
`{id}` is the sanction's own numeric id — not the queried CPF/CNPJ.

The real payload also disagreed with prior assumptions in two more ways: `pessoa.cnpjFormatado` is `""` (not
`null`/absent) for a person sancionado, so the company/person discriminator's `is not None` check misclassified persons
as companies; and `fundamentacao` can itself be `null`, not just an empty list.

## Decision

`PortalTransparenciaCNEPFetcher`/`CEISFetcher.fetch()` branch on whether an id (`cnep_id`/`ceis_id`) was given: with an
id, call the by-id endpoint and map the single object with the existing `map_graph`; without one, call the collection
endpoint with `codigoSancionado`+`pagina=1` and map every array element, unioning the resulting per-record graphs via a
new `Graph.merge()` method (`src/osint_engine/domain/entities/bases/graph.py`) instead of duplicating set-union logic in
each fetcher. An empty array (no sanctions found) makes `fetch()` return `None`; `ExpandByCNEP`/`ExpandByCEIS.execute()`
treat `None` as a legitimate empty result and skip `uow.graphs.merge()`, returning `None`; the router maps that to
`204 No Content` rather than an error, since `Graph` itself cannot represent zero nodes (`GraphHasNoNodesError`). The
discriminator now treats falsy (not just `None`) `cnpjFormatado` as "no CNPJ", and `fundamentacao` is read with
`payload.optional(...) or []`.

## Consequences

- CNEP expansion behavior changes for existing callers: a lookup with no matching sanctions now returns `204` instead of
  whatever the broken path-based request used to produce (in practice, always a `400`-wrapped `DataSourceRequestError`,
  since that request shape never succeeded against the real API).
- `cnep_id`/`ceis_id` now means "the sanction record's own id", confirmed against the live API — callers that assumed it
  filtered a per-subject list of results were never correct, since the collection endpoint has always been the only way
  to filter by CPF/CNPJ.
- `Graph.merge()` is now public domain surface; any future source returning multiple partial graphs for one subject can
  reuse it instead of duplicating set-union logic in infrastructure.
- The fixture-refresh script (`scripts/refresh_test_source_responses.py`) fetches a real by-id record (a single object)
  rather than a collection query, so the golden-snapshot tests continue to exercise `map_graph` directly; the
  array/merge path is instead covered by fetcher-level `MockTransport` tests.
