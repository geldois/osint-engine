# TO-DO

## chore(ci)

- install Renovate GitHub App on geldois/osint-engine and push `renovate.json` to enable automated dependency updates
for actions, uv, and pre-commit hooks

## refactor(tests)

- migrate `tests/fakes.py` to `tests/fakes/` directory and update all imports across test files

## test(interface/http)

- test `POST /auth/token`: valid credentials return token, invalid credentials return 401 with `WWW-Authenticate: Bearer`
- test `GET /cnpj/{cnpj}`: missing token returns 401, invalid token returns 401, valid token proceeds to use case
- test `fastapi_error_handler`: `WWW-Authenticate: Bearer` header present on 401, `ErrorDebug` absent in body when `debug=False`, detail masked to generic message on 5xx
- test node and edge presenter dispatch and `UnmappedTypeSchemaError` path
- test graph presenter full mapping
- test schema registries completeness and `MissingDiscriminatorFieldError` guard
