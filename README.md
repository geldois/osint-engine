# OSINT Engine

[![CI](https://github.com/geldois/osint-engine/actions/workflows/test.yml/badge.svg)](https://github.com/geldois/osint-engine/actions)
[![Release](https://img.shields.io/github/v/release/geldois/osint-engine)](https://github.com/geldois/osint-engine/releases)
[![Python](https://img.shields.io/badge/python-%E2%89%A53.12-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Entity relationship graph engine that expands identifiers into a fully traceable network of connections sourced
exclusively from official public records.

**Live:** [osint-engine.angelitochagas.com/docs](https://osint-engine.angelitochagas.com/docs)

## Overview

A **CNPJ** enters the engine as a root identifier. The engine queries official public records, constructs a typed
immutable graph, and returns it — ready to traverse. Each **Node** represents a real-world entity: a company, a person,
an address, a CNAE classification, a phone, or an email. Each **Edge** names the relationship between two nodes:
`company_has_member`, `person_owns_company`, `company_located_at`, and so on.

Every node and edge carries a stable, deterministic identity derived exclusively from its content. The same CNPJ
expanded on different machines at different times always produces the same graph with the same IDs — making the
structure idempotent by construction, not by convention.

## Architecture

```mermaid
flowchart LR
    subgraph Domain
        Graph("Graph")
        Node("Node")
        Edge("Edge")
        User("User")
    end

    Client("HTTP Request") --> FastAPI("FastAPI App")
    FastAPI --> Logging("Logging Middleware")
    FastAPI --> ErrorHandler("Error Handler")
    FastAPI --> AuthRouter("Auth Router")
    FastAPI --> CNPJRouter("CNPJ Router")
    FastAPI --> ExpansionRouters("CPF / CNEP / CEIS Routers")
    FastAPI --> GraphHistoryRouter("Graph History Router")
    FastAPI --> CredentialsRouter("Credentials Router")
    FastAPI --> HealthRouter("Health Router")
    FastAPI --> TextIngestionRouter("Text Ingestion Router")

    AuthRouter --> PostToken("POST /auth/token")
    AuthRouter --> PostViewerToken("POST /auth/viewer-token")
    CNPJRouter --> RoleGuard("Role Guard")
    CNPJRouter --> ExpansionRateLimit("Expansion Rate Limit · 100 per min per route, shared")
    CNPJRouter --> GetCNPJ("GET /cnpj/{cnpj}")
    ExpansionRouters --> JwtGuard("JWT Guard")
    ExpansionRouters --> ExpansionRateLimit
    ExpansionRouters --> GetExpansion("GET /cpf · /cnep · /ceis")
    GraphHistoryRouter --> JwtGuard
    GraphHistoryRouter --> ExpansionRateLimit
    GraphHistoryRouter --> GetGraphHistory("GET /graphs/{root_id}/history")
    CredentialsRouter --> RoleGuard
    CredentialsRouter --> PostCredential("POST /credentials")
    CredentialsRouter --> GetCredentials("GET /credentials")
    HealthRouter --> Liveness("GET /health")
    HealthRouter --> Readiness("GET /health/ready")
    TextIngestionRouter --> JwtGuard
    TextIngestionRouter --> ExpansionRateLimit
    TextIngestionRouter --> GetPatterns("GET /text-ingestion/patterns")
    TextIngestionRouter --> PostIngestion("POST /text-ingestion")
    TextIngestionRouter --> PostIngestionFile("POST /text-ingestion/file")

    Bootstrap("build_container") --> Container("Container")
    Container --> Fetchers("Fetchers")
    Container --> PatternSets("PatternSetRepository")
    Container --> Policies("Policies")
    Container --> Services("Services")
    Container --> UoWFactory("UoWFactory")
    Container --> UseCases("UseCases")
    Container --> ReadinessProbe("readiness_probe")

    UseCases --> AuthenticateUser("AuthenticateUser")
    UseCases --> ExpandByCNPJ("ExpandByCNPJ")
    UseCases --> ExpandByCPF("ExpandByCPF")
    UseCases --> ExpandByPortal("ExpandBy CNEP / CEIS")
    UseCases --> ListGraphHistory("ListGraphHistory")
    UseCases --> CredentialUseCases("List / Save ExternalCredential")
    UseCases --> IngestText("IngestText")
    UseCases --> ListPatternSets("ListTextPatterns")
    Services --> PyJWTService("PyJWTService")
    Services --> SpreadsheetReader("read_spreadsheet_text")
    Fetchers --> CNPJFetcher("BrasilAPICNPJv1Fetcher")
    Fetchers --> KipFlowFetcher("KipFlowCPFFetcher")
    Fetchers --> PortalFetchers("Portal da Transparência Fetchers")
    PatternSets --> MemPatternSets("MemPatternSetRepository")
    MemPatternSets --> DefaultPatterns("BRAZILIAN_DOCUMENTS_V1")

    PostToken --> AuthenticateUser
    PostViewerToken --> PyJWTService
    GetCNPJ --> ExpandByCNPJ
    GetExpansion --> ExpandByCPF
    GetExpansion --> ExpandByPortal
    GetGraphHistory --> ListGraphHistory
    PostCredential --> CredentialUseCases
    GetCredentials --> CredentialUseCases
    GetPatterns --> ListPatternSets
    PostIngestion --> IngestText
    PostIngestionFile --> SpreadsheetReader
    PostIngestionFile --> IngestText
    Readiness --> ReadinessProbe
    RoleGuard --> PyJWTService
    JwtGuard --> PyJWTService

    IngestText --> UoWFactory
    IngestText --> PatternSets
    IngestText --> ExtractMatches("extract_matches · regex + mod-11 checksum")
    IngestText --> TextSourceNode("TextSource")
    IngestText --> MentionEdges("Person/Company/AddressMentionedInText")
    ListPatternSets --> PatternSets

    AuthenticateUser --> UoWFactory
    AuthenticateUser --> Argon2("Argon2PasswordHasher")
    AuthenticateUser --> PyJWTService

    ExpandByCNPJ --> UoWFactory
    ExpandByCNPJ --> CNPJFetcher
    ExpandByCPF --> UoWFactory
    ExpandByCPF --> KipFlowFetcher
    ExpandByPortal --> UoWFactory
    ExpandByPortal --> PortalFetchers
    ListGraphHistory --> UoWFactory
    CNPJFetcher --> BrasilAPI("BrasilAPI")
    KipFlowFetcher --> KipFlowAPI("KipFlow")
    PortalFetchers --> PortalAPI("Portal da Transparência")
    CNPJFetcher --> Mapper("cnpj_v1_mapper")
    Mapper --> EntityRevision("EntityRevision")
    EntityRevision --> Graph

    UoWFactory --> HybridUoW("HybridUoW")
    HybridUoW --> MemUoW("MemUoW")
    HybridUoW --> PgCredentials("PgExternalCredentialRepository")
    CredentialUseCases --> HybridUoW
    PgCredentials --> Fernet("Fernet encryption")
    PgCredentials --> Postgres("PostgreSQL")
    ReadinessProbe --> Postgres
    MemUoW --> Snapshot("MemStorageSnapshot")
    MemUoW --> NodeRepo("MemNodeRepository")
    MemUoW --> EdgeRepo("MemEdgeRepository")
    MemUoW --> GraphRepo("MemGraphRepository")
    MemUoW --> UserRepo("MemUserRepository")

    Policies --> MergePolicy("RevisionMergePolicy")
    Policies --> SelectionPolicy("RevisionSelectionPolicy")
    MergePolicy --> NodeRepo
    MergePolicy --> EdgeRepo
    MergePolicy --> GraphRepo
    SelectionPolicy --> NodeRepo
    SelectionPolicy --> EdgeRepo
    SelectionPolicy --> GraphRepo

    NodeRepo --> Snapshot
    EdgeRepo --> Snapshot
    GraphRepo --> Snapshot
    UserRepo --> Snapshot
    Snapshot --> MemStorage("MemStorage")

    NodeRepo --> Node
    EdgeRepo --> Edge
    GraphRepo --> Graph
    UserRepo --> User
    GraphRepo -.cascades new content only.-> NodeRepo
    GraphRepo -.cascades new content only.-> EdgeRepo

    GetCNPJ --> GraphPresenter("Graph Presenter")
    GetGraphHistory --> GraphPresenter
    GraphPresenter --> GraphSchema("GraphSchema")
    PostToken --> TokenSchema("TokenSchema")
```

## API

Every endpoint except `/auth/token` and `/auth/viewer-token` requires a Bearer token. Obtain one first, then use it on
every subsequent request.

### Authentication

```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=admin&password=<ADMIN_PASSWORD>
```

Returns an `ADMIN`-role token, 60-minute TTL (`ACCESS_TOKEN_EXPIRE_MINUTES`):

```json
{ "access_token": "<token>", "token_type": "bearer" }
```

```http
POST /auth/viewer-token
```

Issues a `VIEWER`-role token with no credential — 20-minute TTL by default (`VIEWER_TOKEN_EXPIRE_MINUTES`), same
response shape as above. Intended for public demo access: it can read `/cnpj/{cnpj}` but is rejected with `403` on
`/credentials`. See `docs/architecture/interface.md`.

### Graph expansion

```http
GET /cnpj/{cnpj}
Authorization: Bearer <token>
```

Returns a `GraphSchema` containing the root company, all connected entities, and all typed relationships. Available to
both `ADMIN` and `VIEWER` tokens. The current provider is [BrasilAPI](https://brasilapi.com.br) (see
`docs/architecture/infrastructure.md`).

```http
GET /cpf/{cpf}?force=false
Authorization: Bearer <token>
```

Returns a `GraphSchema` rooted at the `Person` the CPF resolves to, including `registration_status`/`registration_date`
when the provider has them. The current provider is [KipFlow](https://kipflow.io), a paid API — a repeated expansion of
the same CPF returns `409` instead of calling the provider again, unless `force=true` is passed. Returns `204` (empty
body) when the provider has no record for the CPF. Requires the caller's own saved `KIPFLOW` credential, via
`POST /credentials`.

```http
GET /graphs/{root_id}/history
Authorization: Bearer <token>
```

Returns every `Graph` revision ever stored for that `root_id`, as a `GraphSchema` array ordered by `fetched_at`
ascending (oldest first). Available to both `ADMIN` and `VIEWER` tokens. `200 []` for a `root_id` never seen — an empty
history is a valid state, not an error.

### Text ingestion

```http
GET /text-ingestion/patterns
Authorization: Bearer <token>
```

Lists every atomic pattern name (with the node type and fields it covers) plus every registered pattern set shortcut,
without exposing the underlying compiled regex.

```http
POST /text-ingestion
Authorization: Bearer <token>
Content-Type: application/json

{ "text": "...", "patterns": ["brazilian_documents_v1", "CNPJ_LOOSE"] }
```

`patterns` accepts any mix of pattern set shortcuts and individually-named atomic patterns in the same call; they
resolve to a union before matching. Extracts CPF/CNPJ/CEP-and-number from free text via regex plus a mod-11 checksum,
never calling any external API. Every match is checked against what the graph already knows by deterministic id: an
existing entity is only linked, a new one becomes a minimal stub (identity field only, nothing invented). The response
is a `GraphSchema` rooted at a `TextSource` node, with a `PersonMentionedInText`/`CompanyMentionedInText`/
`AddressMentionedInText` edge per match, each carrying the exact pattern name that produced it. Returns `422` if nothing
matched or if `patterns` names an unknown pattern set or atomic pattern. See `docs/architecture/application.md`.

```http
POST /text-ingestion/file
Authorization: Bearer <token>
Content-Type: multipart/form-data

file=<a .xlsx or .csv file>
patterns=brazilian_documents_v1
patterns=CNPJ_LOOSE
```

Same matching, stubbing, and response shape as `POST /text-ingestion` above, `patterns` accepting the same mix of
shortcuts and atomic names — only the input differs: every cell of the uploaded spreadsheet is flattened into text
verbatim (no trimming, no reformatting, numeric cells converted via plain `str()`) and fed to the same matcher. Every
sheet of a `.xlsx` workbook is scanned, not only the active one; a formula cell is read by its last computed value,
never the formula text. Rejects anything above 10 MB or 50,000 rows in a single sheet, any extension other than `.xlsx`
or `.csv`, a CSV field past the parser's own size limit, and any file whose content isn't a valid spreadsheet, all as
`422`. See `docs/architecture/infrastructure.md`.

### Health

```http
GET /health
```

Liveness — always `200 {"status": "ok"}` while the process is up, touching no dependency. Both health endpoints are
unauthenticated and unthrottled so a hosting platform (Render) can poll them freely.

```http
GET /health/ready
```

Readiness — `200 {"status": "ready"}` when Postgres answers a `SELECT 1`, `503 {"status": "not_ready"}` otherwise.

### Rate limiting

| Endpoint                        | Limit      | Keyed by                |
| ------------------------------- | ---------- | ----------------------- |
| `POST /auth/token`              | 5 / 15 min | Client IP               |
| `POST /auth/viewer-token`       | 20 / min   | Client IP               |
| `GET /cnpj/{cnpj}`              | 100 / min  | Shared per-route bucket |
| `GET /cpf/{cpf}`                | 100 / min  | Shared per-route bucket |
| `GET /graphs/{root_id}/history` | 100 / min  | Shared per-route bucket |
| `GET /cnep/{cpf_or_cnpj}`       | 100 / min  | Shared per-route bucket |
| `GET /ceis/{cpf_or_cnpj}`       | 100 / min  | Shared per-route bucket |
| `GET /text-ingestion/patterns`  | 100 / min  | Shared per-route bucket |
| `POST /text-ingestion`          | 100 / min  | Shared per-route bucket |

A `429` response includes a `Retry-After` header (seconds) and is exposed cross-origin via
`Access-Control-Expose-Headers`. See `docs/architecture/interface.md`. Each expansion route has one global bucket shared
across all callers — a fixed key, not per-IP or per-role — so the combined outbound traffic every visitor generates
together is capped against the upstream API's per-minute quota, since every request proxies through this deployment's
own IP/token. The health endpoints are unthrottled.

### Errors

Every response includes an `X-Correlation-ID` header for end-to-end request tracing. Error responses carry the same
correlation ID in the body alongside a machine-readable `type` field derived from the domain error hierarchy. A `401`
response always includes `WWW-Authenticate: Bearer` per RFC 6750; a `403` means a valid token lacks the required role; a
`409` means the request conflicts with something already done (e.g. `GET /cpf/{cpf}` repeated without `force=true`); a
`429` means a rate limit was exceeded.

## Stack

- **Runtime:** Python 3.12, FastAPI, Uvicorn
- **CLI:** Typer (`osint-engine serve` / `osint-engine migrate up|down`)
- **Auth:** PyJWT (HS256 access tokens), argon2-cffi (Argon2id password hashing)
- **Persistence:** PostgreSQL via asyncpg + aiosql (external credentials), golang-migrate (schema migrations), in-memory
  snapshot store (graph/user data)
- **Encryption:** cryptography (Fernet, application-layer encryption of stored API keys)
- **Rate limiting:** fastapi-throttle (in-memory)
- **HTTP client:** httpx2 (async)
- **File reading:** openpyxl (`.xlsx`), stdlib `csv` (`.csv`)
- **Serialisation:** Pydantic v2 (discriminated unions for node and edge schemas)
- **Observability:** structlog (JSON in production, console in debug)
- **Tooling:** uv, Ruff, basedpyright (strict), import-linter, cosmic-ray
- **Testing:** pytest, pytest-asyncio, testcontainers

## Design

### Content-addressable entity identity

Every entity — node, edge, and graph — derives its ID from its content via UUID5. The same input always produces the
same identifier, on any machine, at any time. Deduplication, idempotent upserts, and safe concurrent writes are
structural consequences, not implementation choices. Each entity type occupies its own UUID namespace so that a
`CompanyID` and a `PersonID` derived from identical payloads can never collide.

See `docs/architecture/domain.md`.

### Fail-fast entity contracts

The entity base class uses `__init_subclass__` to validate every subclass at import time, not at instantiation. A
concrete entity missing a namespace or declaring an incompatible ID type raises immediately when the module is loaded —
before any test runs, before any instance is created. The domain is self-defending.

`__setattr__` and `__delattr__` raise `FrozenInstanceError` on every entity. Immutability is structural, not enforced by
convention.

See `docs/architecture/domain.md`.

### Zero-cost type hierarchy

Each concrete entity declares its own `NewType` ID (`CompanyID`, `PersonID`, `GraphID`, …) as the generic parameter of
`Entity[IDType_co]`, where `IDType_co` is a covariant `TypeVar` bound to `UUID`. The type-checker enforces that a
`Node[CompanyID]` cannot be substituted for a `Node[PersonID]` — and that edge source and target ID types match their
declared constraints — with no runtime representation whatsoever. `NewType` is the identity function at runtime; the
distinction exists only in the type-checker's world.

See `docs/architecture/domain.md`.

### Temporal reconciliation via revisions

An entity captures *what* something is; *when* it was observed and how repeated observations reconcile are separate
concerns that must never leak into the content-addressable identity. Every fetched entity is wrapped in an immutable
`EntityRevision` that stamps `fetched_at` at the I/O boundary — the fetcher owns provenance, the mapper stays a pure
payload-to-graph function, and the `id` never absorbs a timestamp. When a re-fetch arrives for an entity already stored
under the same `id`, a pluggable `RevisionMergePolicy` decides how the two reconcile — by default the incoming revision
is kept exactly as it arrived, no field synthesis, since the frontend renders every fetch as its own immutable snapshot
and navigates prior ones itself; a field-filling policy that lets the newest observation fill its nulls from the older
one remains available to inject where server-side reconciliation is actually wanted. A `RevisionSelectionPolicy` chooses
the current revision by newest `fetched_at`. Repositories retain every revision keyed by `content_id`, so a leaner
re-fetch never physically overwrites a richer prior observation, even when the default policy makes the current revision
look less complete than the one before it.

See `docs/architecture/application.md`.

## Setup

```bash
git clone https://github.com/geldois/osint-engine.git
cd osint-engine
```

### Linux

1. Install [Docker Engine](https://docs.docker.com/engine/install/) and start the daemon.
2. Install [mise](https://mise.jdx.dev) and activate it in your shell (see
   [getting started](https://mise.jdx.dev/getting-started.html)).
3. Install the project toolchain and activate the versioned git config:

```bash
mise install
git config --local include.path ../.gitconfig
cp .env.example .env  # then set SECRET_KEY, ADMIN_PASSWORD, DATABASE_URL and EXTERNAL_CREDENTIAL_ENCRYPTION_KEY
```

### Windows

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) with the WSL2 backend enabled.
2. Install [mise](https://mise.jdx.dev) via PowerShell and activate it in your shell (see
   [getting started](https://mise.jdx.dev/getting-started.html)).
3. Install the project toolchain and activate the versioned git config:

```powershell
mise install
git config --local include.path ../.gitconfig
copy .env.example .env  # then set SECRET_KEY, ADMIN_PASSWORD, DATABASE_URL and EXTERNAL_CREDENTIAL_ENCRYPTION_KEY
```

> `.gitconfig` points `core.hooksPath` at the versioned `.githooks/`, so the hooks are whatever is committed — nothing
> is generated into `.git/`. The hooks and the `uv run python -m scripts …` dev runner call `uv` directly, so `mise`
> must be active on the `PATH` of the shell you commit from — `mise` provides the pinned `uv`, `dprint`, `shellcheck`
> and `shfmt`. If `uv` isn't found, the hook prints how to fix it (activate mise, or `git commit --no-verify` to bypass
> once). No editor or Claude Code is required: the quality gates run entirely from these git hooks and CI, identically
> for every contributor, and there is no `pre-push` — pushing is never blocked.

> `--network host` in `.actrc` is Linux-only and has no effect on Docker Desktop. Internet access works via Docker
> Desktop's default networking — the first run downloads dependencies from PyPI, subsequent runs use the uv cache.

### Run

`osint-engine migrate` needs the `migrate` CLI on `PATH` (installed by `mise install`, pinned to the same version the
Dockerfile uses) and a running Postgres reachable at `DATABASE_URL` — unlike the test suite, `serve`/`migrate` don't
spin one up for you. `docker-compose.yml` starts a persistent local Postgres matching `.env.example`'s credentials, and
`osint-engine wait-db` blocks until it actually accepts connections (Postgres reports the container as "started" well
before it's ready to accept connections — polling avoids a race against it):

```bash
docker compose up -d
uv run osint-engine wait-db
uv run osint-engine migrate up
uv run osint-engine serve
```

The production image runs this sequence: its entrypoint chains `wait-db`, `migrate up`, then `serve`, so a container
deploy (Render) needs no manual migration step — the commands above are only for running against a local Postgres
outside the container.

### Test

`tests/**/responses/` (golden HTTP fixtures for the BrasilAPI/Portal da Transparência provider tests) is untracked and
regenerated on demand, not committed — run this once before testing, and again whenever the fixtures need refreshing:

```bash
uv run python -m scripts fixtures refresh
```

Portal da Transparência's fixtures require a real, working `PORTAL_TRANSPARENCIA_API_KEY` in `.env` — request one at
<https://api.portaldatransparencia.gov.br/>.

```bash
uv run pytest --cov --cov-branch
```

`tests/test_infrastructure/test_persistence/test_pg/` spins up a real Postgres via `testcontainers`, pulling the
`postgres:18` and `testcontainers/ryuk:0.8.1` images from Docker Hub on first run (cached locally afterward). If pulls
hang or time out, your DNS resolver may not be resolving Docker Hub reliably — point the Docker daemon at a known-good
resolver in `/etc/docker/daemon.json`:

```json
{ "dns": ["1.1.1.1", "8.8.8.8"] }
```

then `sudo systemctl restart docker` and re-run the pulls.

### Local CI

```bash
act push
```
