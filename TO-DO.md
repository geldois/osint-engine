# TO-DO

## chore(ci)

- install Renovate GitHub App on geldois/osint-engine and push `renovate.json` to enable automated dependency updates
for actions, uv, and pre-commit hooks

## fix(interface)

- harden `sanitize_cnpj`: after stripping non-decimal chars, assert the result is exactly 14 digits and raise an
appropriate interface error — currently silently forwards a malformed string to the use case

## test(application)

- test `AuthenticateUser`: valid credentials return user, wrong password raises `InvalidCredentialsAuthError`,
non-existent user raises same error (no enumeration), dummy hash path always runs when user is absent

## test(infrastructure/fetchers)

- test `BrasilAPICNPJFetcher` HTTP error and network failure handling
- test `BrasilAPICNPJMapper` field mapping, optional fields, and partner type filtering

## test(infrastructure/hashers)

- test `PasswordHasher`: `hash_` returns a string, `verify` returns `True`/`False`, both raise
`UnexpectedHasherOutputAuthError` when passlib returns unexpected type

## test(infrastructure/services)

- test `PyJWTService`: valid token round-trip, expired token raises `InvalidTokenAuthError`, tampered signature raises `InvalidTokenAuthError`

## test(interface/http)

- test `POST /auth/token`: valid credentials return token, invalid credentials return 401 with `WWW-Authenticate: Bearer`
- test `GET /cnpj/{cnpj}`: missing token returns 401, invalid token returns 401, valid token proceeds to use case
- test `error_handler`: each error hierarchy branch maps to the correct HTTP status, `WWW-Authenticate: Bearer` header
is set on 401, `ErrorDebug` appears in body only when `debug=True`, unknown exception falls through to 500
- test node and edge presenter dispatch and `UnmappedTypeSchemaError` path
- test graph presenter full mapping
- test schema registries completeness and `MissingDiscriminatorFieldError` guard

## test(interface/sanitizers)

- test `sanitize_cnpj`: formatted input strips to 14 digits, digit-only input passes through unchanged, invalid length
after strip raises the interface error
