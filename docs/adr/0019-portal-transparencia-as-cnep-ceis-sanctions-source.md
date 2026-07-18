# Portal da Transparência as CNEP/CEIS sanctions source

## Status

Accepted

## Context

Expanding the entity graph beyond registration data (ADR-0005) requires a source of
Brazilian public-sanction records — administrative and civil sanctions applied to
companies and individuals (CNEP — Cadastro Nacional de Empresas Punidas — and CEIS —
Cadastro de Empresas Inidôneas e Suspensas) — to populate `Sanction` nodes and
`company_received_sanction`/`person_received_sanction` edges.

Unlike BrasilAPI, no unauthenticated community aggregator publishes this data. The
authoritative source is the Portal da Transparência (Controladoria-Geral da União),
which requires an API key issued per application.

## Decision

Use the Portal da Transparência API (`https://api.portaldatransparencia.gov.br/api-de-dados/`)
as the source for CNEP sanction records, authenticated via the `chave-api-dados` header
and an `ExternalCredential` supplied by the caller (see
`src/osint_engine/application/auth/external_credential.py`).

`PortalTransparenciaFetcher` (`src/osint_engine/infrastructure/sources/portal_transparencia/portal_transparencia_fetcher.py`)
mirrors the `_BrasilAPIFetcher` pattern from ADR-0005: `__init_subclass__` composes the
full endpoint URL from a `url_suffix` class keyword, so each endpoint subclass
(`PortalTransparenciaCNEPFetcher`) declares only its path suffix and response mapping,
not HTTP plumbing. The `CNEPFetcher` port lives in the application layer; nothing above
the infrastructure boundary knows this adapter exists.

## Consequences

- Every call requires a valid `ExternalCredential` with an API key issued by the Portal
  da Transparência — unlike the CNPJ pipeline, this source cannot be exercised
  anonymously. Key provisioning is a manual, out-of-band step for whoever configures a
  deployment.
- `PortalTransparenciaCNEPFetcher` and `cnep_mapper` are built and fully tested but are
  **not yet wired** into `Container`/`Fetchers` or any use case — the same
  built-but-unwired state already tracked for `CEPFetcher` in `TO-DO.md`. No API
  endpoint currently returns `Sanction` nodes; wiring it into `ExpandByCNPJ` (or a new
  use case) is future work.
- `DataSourceRequestError` (via `PortalTransparenciaFetcher`'s shared HTTP error
  handling) wraps failures the same way `_BrasilAPIFetcher` does, so the 502 mapping at
  the interface layer (`http_status_mapper.py`) already covers this source without
  additional wiring.
- CEIS (Cadastro de Empresas Inidôneas e Suspensas) is not yet implemented — this ADR
  covers CNEP only. A CEIS fetcher would follow the same `PortalTransparenciaFetcher`
  subclassing pattern.
