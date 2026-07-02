# Stateless JWT for authentication

## Status

Accepted

## Context

The API requires a mechanism to authenticate requests after a successful login. The two primary options considered
were server-side sessions and stateless JWT tokens.

| Approach | State location | Revocation | Horizontal scaling | Complexity |
| --- | --- | --- | --- | --- |
| **Server-side session** | Server (cache or DB) | Immediate (delete key) | Requires shared session store | Moderate |
| **Stateless JWT** | Client (token payload) | Delayed (until expiry) | No shared state required | Low |
| API key (static) | Server (DB lookup) | Immediate | Requires DB on every request | Low |

The primary constraints were: single-user MVP (one admin), no Redis or shared cache in scope, and a frontend that
will call the API from a browser — making cookie-based sessions less ergonomic than Bearer tokens with CORS.

## Decision

Issue short-lived JWT access tokens signed with HMAC-SHA256 (HS256). The token payload carries `sub` (username),
`role`, and `exp` (expiry). `PyJWTService` signs and verifies tokens using a `secret_key` read from the environment.
The algorithm is hardcoded to HS256 as a class constant — it is not configurable to prevent downgrade attacks via
algorithm confusion.

The `OAuth2PasswordBearer` scheme is used at the interface layer so FastAPI generates a correct OpenAPI security
definition and Swagger UI displays the Authorize button.

HS256 was chosen over RS256 because the system is a monolith: there is no second service that needs to verify
tokens without access to the signing secret. RS256 adds key management overhead (key pair generation, rotation,
public key distribution) that is not justified here.

## Consequences

- **No revocation without a blocklist.** A valid token remains valid until it expires. Logout is client-side only
  (discard the token). If a secret is compromised, rotating `secret_key` invalidates all outstanding tokens
  immediately — this is the only server-side revocation mechanism available without a blocklist.

- **Token expiry is configurable** via `ACCESS_TOKEN_EXPIRE_MINUTES`. The default (60 minutes) is appropriate for
  a demo; a production deployment should lower this and introduce refresh tokens.

- **No refresh token.** The MVP issues only access tokens. A production auth layer would add a long-lived refresh
  token stored server-side (to enable revocation) and a `POST /auth/refresh` endpoint.

- **Role is carried in the token** (`role` claim). The `jwt_guard` currently ignores the claim — it only validates
  the signature and expiry. RBAC enforcement is deferred and can be added as a second guard or as a check inside
  each use case without touching the token structure.

- **HS256 is only safe with a strong secret key.** A key shorter than 32 bytes produces a warning from PyJWT.
  `SECRET_KEY` must be generated with a cryptographically secure source (e.g. `openssl rand -hex 32`).
