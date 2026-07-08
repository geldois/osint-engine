# TO-DO

## chore(ci)

- install Renovate GitHub App on geldois/osint-engine and push `renovate.json` to enable automated dependency updates
for actions, uv, and pre-commit hooks

## refactor(tests/test_infrastructure)

- rename `test_fetchers/` to `test_sources/` to match the renamed `infrastructure/sources/` package

## test(application)

- test `AuthenticateUser`: valid credentials return user, wrong password raises `InvalidCredentialsError`,
non-existent user raises same error (no enumeration), dummy hash path always runs when user is absent

## test(infrastructure/sources)

- test `BrasilAPICNPJFetcher` HTTP error and network failure handling

## test(infrastructure/services)

- test `PyJWTService`: valid token round-trip, expired token raises `InvalidTokenError`, tampered signature raises `InvalidTokenError`

## test(interface/http)

- test `POST /auth/token`: valid credentials return token, invalid credentials return 401 with `WWW-Authenticate: Bearer`
- test `GET /cnpj/{cnpj}`: missing token returns 401, invalid token returns 401, valid token proceeds to use case
- test `error_handler`: each error hierarchy branch maps to the correct HTTP status, `WWW-Authenticate: Bearer` header
is set on 401, `ErrorDebug` appears in body only when `debug=True`, unknown exception falls through to 500
- test node and edge presenter dispatch and `UnmappedTypeSchemaError` path
- test graph presenter full mapping
- test schema registries completeness and `MissingDiscriminatorFieldError` guard
