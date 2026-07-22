# Role guard for per-route authorization

## Status

Accepted

## Context

ADR-0008 introduced stateless JWT authentication and explicitly deferred RBAC: `jwt_guard` validated only signature
and expiry, ignoring the `role` claim it already carried. That deferral ends here — a public, credential-free
`VIEWER` role (issued via `POST /auth/viewer-token`) now needs to reach read endpoints (`/cnpj/{cnpj}`) while being
denied write endpoints (`/credentials`), which must stay `ADMIN`-only. Enforcement had to land somewhere between
"decode the token" and "run the use case."

Two placements were considered: authorization checks inside each use case (application layer), or a second
interface-layer guard alongside the existing `jwt_guard`. Use-case-level checks would scatter the same role logic
across every write path and blur the boundary between business rules and transport-level access control; a route
guard keeps authorization a pure interface concern, consistent with how `jwt_guard` already handles authentication.

## Decision

`build_role_guard` (`src/osint_engine/interface/http/fastapi/dependencies/jwt_guard.py`) decodes the token — same
call `jwt_guard` makes — then checks `claims["role"] not in allowed_roles`, where `allowed_roles` is a
`frozenset[Role]` supplied per router (`cnpj_router`: `{ADMIN, VIEWER}`; `credentials_router`: `{ADMIN}`). The
membership check needs no explicit conversion because `Role` is a `StrEnum`: `Role.ADMIN == "ADMIN"` holds directly
against the raw string claim. A mismatch raises `InsufficientRoleError` (`interface/errors/authorization_error.py`),
mapped to 403 — distinct from `jwt_guard`'s 401 for missing/invalid tokens.

The `VIEWER` token itself is issued without touching `AuthenticateUser` or `mem_seeder` — there is no credential to
verify, so `post_viewer_token` calls `jwt_service.create_access_token` directly with a fixed `username="visitor"` and
`role=Role.VIEWER`. Routing it through the password-based use case would mean seeding a fake user with a public
password purely to satisfy a code path that has no actual authentication decision to make.

## Consequences

- `jwt_guard` and `build_role_guard` each decode the token independently — `cnep_router` (unwired, out of scope) still
  uses the plain `jwt_guard`, so the two guards coexist rather than one wrapping the other. The duplicate decode is
  cheap (single HMAC verification) and keeps `jwt_guard`'s existing test suite and call sites untouched.
- Authorization is route-granularity only. A future requirement for per-resource or per-field permissions (e.g. a
  viewer allowed to read some CNPJs but not others) would need a different mechanism than `allowed_roles` per router.
- The `VIEWER` role has no backing `User` record in `mem_storage` — anything that assumes every authenticated
  principal maps to a stored user (audit logging keyed by username, for example) will not find one for visitor
  sessions.
