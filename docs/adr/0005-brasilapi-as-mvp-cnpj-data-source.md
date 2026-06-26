# BrasilAPI as MVP CNPJ data source

## Status

Accepted

## Context

The MVP requires a CNPJ expansion pipeline that, given a company registration number,
produces a domain Graph populated with its legal data: company profile, address,
CNAEs, QSA members, phones, and email.

Candidate data sources were evaluated:

| Source | Auth required | Cost | Response richness | Reliability |
|---|---|---|---|---|
| **BrasilAPI** | No | Free | High (QSA, CNAEs, contacts, sanctions) | Unofficial SLA, community-maintained |
| ReceitaWS | No | Freemium, rate-limited | Medium | Unofficial |
| CNPJ.ws | API key | Paid tiers | High | Commercial |
| Receita Federal (direct) | CAPTCHA / scraping | Free | Authoritative | Fragile, ToS risk |

The primary constraint at this stage is **delivery speed**: the graph model must be
validated against real data before any investment in paid infrastructure or scraping
maintenance.

## Decision

Use BrasilAPI (`https://brasilapi.com.br/api/cnpj/v1/{cnpj}`) as the sole CNPJ
data source for the MVP.

The four reasons that drove the choice:

1. **API simplicity** — single REST endpoint, unauthenticated, no SDK or OAuth dance.
   A plain `GET` with httpx2 is enough.

2. **Ease of implementation** — the JSON response is flat and well-documented. The
   mapper translates it to domain entities in one pass with no pagination, cursors, or
   multi-step flows.

3. **Delivery speed** — no account creation, no API key provisioning, no contract.
   The fetcher was operational from the first line of code.

4. **Rich returned context** — a single call surfaces every field the graph model
   currently needs: legal name, trade name, CNAE primary + secondary, address (CEP +
   number), QSA with partner type discriminator, up to two phone numbers, email,
   registration status, share capital, company size category, and headquarters flag.
   No secondary requests are required to populate a complete Graph.

The fetcher is hidden behind the `CNPJFetcher` port in the application layer.
Nothing above the infrastructure boundary knows about BrasilAPI; swapping it out
requires only a new adapter, not changes to the domain or application.

## Consequences

- No SLA. BrasilAPI is a community project with no guaranteed uptime. The
  `ExternalAPIFetcherError` wraps HTTP failures and maps to HTTP 502 at the interface
  layer so callers receive a structured error rather than an exception trace.

- Rate limiting is possible but undocumented. At MVP scale (manual queries during
  development and demos) this is not a problem; at production scale it may require
  request throttling or a queue.

- BrasilAPI aggregates Receita Federal data on a delay. Fields such as QSA membership
  and registration status may lag behind the authoritative source by hours or days.
  For OSINT purposes this is acceptable; for compliance or legal use it is not.

- The `_BrasilAPIFetcher` base class uses `__init_subclass__` to compose the
  endpoint URL at class-definition time, making it straightforward to add new
  BrasilAPI endpoints (e.g. CPF, CEP) as further subclasses without duplicating the
  HTTP error-handling logic.
