# CHANGELOG

<!-- version list -->

## v1.6.0 (2026-07-22)

### Bug Fixes

- **http**: Map TokenError, EdgeSelfLoopError and RevisionError to HTTP status codes
  ([`10a2329`](https://github.com/geldois/osint-engine/commit/10a232917442d1023e2ab74ccf5f7e828b6907e2))

- **http**: Restore router-level jwt_guard on cnep and credentials routers
  ([`b143c77`](https://github.com/geldois/osint-engine/commit/b143c777e1e053d66383dbe405847ba7c3296b3a))

### Build System

- **deps**: Add graphifyy dev dependency for local graphify skill execution
  ([`0f89639`](https://github.com/geldois/osint-engine/commit/0f89639d47b77a5dab7a43cef237d334ab45387d))

### Chores

- **config**: Raise FETCHER_CONNECT_TIMEOUT default to 30s
  ([`3384a88`](https://github.com/geldois/osint-engine/commit/3384a886d9db38ad37c8ff412c7fb0e93218e5e6))

- **deps**: Pin uv toolchain, add mutmut, tidy pre-commit config
  ([`db28155`](https://github.com/geldois/osint-engine/commit/db28155681061708183fc9144af644960fa77639))

- **git**: Declare graphify merge driver for graph.json
  ([`e1fdaca`](https://github.com/geldois/osint-engine/commit/e1fdaca2cf42c2be5950d7bc18291e150c85e5b8))

- **gitignore**: Ignore graphify-out/ knowledge graph output directory
  ([`6999fcb`](https://github.com/geldois/osint-engine/commit/6999fcb7a39b9764e76ae52f7aabbe9b4bcc9f5d))

### Code Style

- Apply ruff format line-break normalization to pre-existing files
  ([`0b8985f`](https://github.com/geldois/osint-engine/commit/0b8985ffca0265bd81573f8366b60bf65776cb99))

### Continuous Integration

- **security**: Pin GitHub Actions and container images to immutable digests
  ([`1f7c757`](https://github.com/geldois/osint-engine/commit/1f7c7579c51bae1eb93967e58d49694214620443))

### Documentation

- Record ADRs for role-guard authorization and fastapi-throttle over slowapi
  ([`efff7ad`](https://github.com/geldois/osint-engine/commit/efff7adcae5ac50a6dff724bef556d8c361c2540))

- Record error-code contract ADR and correct CNEP wiring status
  ([`9aab537`](https://github.com/geldois/osint-engine/commit/9aab537ea776ca172dc0d2d958edcfae2e6cfc21))

### Features

- **auth**: Add public viewer-token role, per-route authorization, and rate limiting
  ([`8db5e09`](https://github.com/geldois/osint-engine/commit/8db5e09fd7e55efa88622786d89b17c8f1a89e00))

- **cep**: Add cep/v2 address enrichment fetcher, mapper and number normalization
  ([`17846a4`](https://github.com/geldois/osint-engine/commit/17846a40375285f18dc404bc8caed30a4c282bd6))

- **cnep**: Integrate Portal da Transparência CNEP/CEIS sanctions source
  ([`7fd1f4a`](https://github.com/geldois/osint-engine/commit/7fd1f4af3f5e37b689ecd9c77444f9f1d6e9adc4))

- **cnep**: Wire CNEP/CEIS sanctions expansion and external credential storage end-to-end
  ([`9ff6cd8`](https://github.com/geldois/osint-engine/commit/9ff6cd8e7d4ac8be329cb2f6e68b8b8b39b0dbfa))

- **http**: Add opt-in DOCS_REDIRECT_ROOT setting to redirect / to /docs
  ([`71d41ad`](https://github.com/geldois/osint-engine/commit/71d41ad571ae6360cfce463b172902767847280b))

- **sanction**: Expand Sanction entity with organ+process identity, dates and fine amount
  ([`6469eff`](https://github.com/geldois/osint-engine/commit/6469eff94b72cf9f119b864f8a059e84bb379029))

- **sanitize**: Add sanitize_cpf_or_cnpj for dual-format CPF/CNPJ identifiers
  ([`e98655e`](https://github.com/geldois/osint-engine/commit/e98655eac723e2704e4db7db26151ab7ccfbbc5f))

- **validation**: Reject malformed CEP/CNPJ identifiers and format-invalid source fields
  ([`1418417`](https://github.com/geldois/osint-engine/commit/1418417dceafa5d0455574f201be84e6ac5d3d25))

### Refactoring

- **errors**: Require explicit error_code on ApplicationError and InfrastructureError subclasses
  ([`ba43a60`](https://github.com/geldois/osint-engine/commit/ba43a607a44fdddd08e24321719963759f53d72e))

- **fetchers**: Make CEPFetcher and CNPJFetcher contracts keyword-only
  ([`c0ec1dc`](https://github.com/geldois/osint-engine/commit/c0ec1dcefaec3d7a7ad560df11ce7cd63499822c))

### Testing

- Harden test suite against mutmut survivors, raise mutation score to 96%
  ([`db9cf98`](https://github.com/geldois/osint-engine/commit/db9cf9882dbb00c86d1c46cc2d60510e40a60ba6))

- **mutmut**: Enable mutation testing infra and fix root causes blocking its run
  ([`3d92d82`](https://github.com/geldois/osint-engine/commit/3d92d8230282dd6af46062ce42188a4e199cb7d8))


## v1.5.0 (2026-07-17)

### Bug Fixes

- **errors**: Render union expected types and report the actual subject in identity contract errors
  ([`aedb742`](https://github.com/geldois/osint-engine/commit/aedb742da16ba6d018351928893a4fbd48a662da))

- **http**: Route domain errors through dedicated handlers to stop 4xx re-raise
  ([`34c648f`](https://github.com/geldois/osint-engine/commit/34c648f4a50fb4e4f5c9207ea9007b23b7b711a6))

- **interface**: Harden sanitize_cnpj with 14-digit length validation
  ([`3436b9e`](https://github.com/geldois/osint-engine/commit/3436b9e04ae687cdafd52d9f622f5929d7307372))

### Build System

- **deps**: Update lockfile after hypothesis addition; remove generated CHANGELOG
  ([`0b2a398`](https://github.com/geldois/osint-engine/commit/0b2a398d66dc2e53015f352df872d952bcf41bee))

### Chores

- **ci**: Add uv sync --check pre-commit hook
  ([`e7443f5`](https://github.com/geldois/osint-engine/commit/e7443f528fb8d816a5d366aa47cf0e18c870bd7a))

### Continuous Integration

- Pin Python to 3.14 to match the production Docker image
  ([`ad2daea`](https://github.com/geldois/osint-engine/commit/ad2daeac30ae627e765a7f8d31ba140119ad1230))

### Documentation

- Record the entity-revision reconciliation architecture in ADRs and README
  ([`02200bb`](https://github.com/geldois/osint-engine/commit/02200bb92a9c2eb6a3b21dbdfd2ae93259402fd6))

### Features

- **application/authentication**: Implement user authentication use case with password hashing and
  tests
  ([`82fb23a`](https://github.com/geldois/osint-engine/commit/82fb23a1397fe8107a75a0ab2190b2105a642e4c))

- **interface/http**: Guard schema registries against duplicate registration
  ([`fb84b1a`](https://github.com/geldois/osint-engine/commit/fb84b1aacc54824477c37915375ccaf2ec7e35d0))

- **qsa**: Map legal-entity partners into normalized company stubs
  ([`494322c`](https://github.com/geldois/osint-engine/commit/494322cefc906b3af2456fce809aa8735212c725))

### Refactoring

- Reconcile repeated entity observations through immutable revisions
  ([`cf284aa`](https://github.com/geldois/osint-engine/commit/cf284aad69d60f8811ce9080c9438e3bd556d27b))

- Rename errors to {Domain}{FailureMode}Error; restructure infrastructure/sources and
  interface/http/fastapi; add api fixture script
  ([`1924f1a`](https://github.com/geldois/osint-engine/commit/1924f1ab9728453d1ec27ffac5678254eb8fba77))

- **auth**: Return decoded claims from the JWT guard
  ([`a61378f`](https://github.com/geldois/osint-engine/commit/a61378f3c8e91bfeceb9f605c47d8af22fe50e3a))

- **config**: Allow injecting a MemStorage into build_container
  ([`09ad374`](https://github.com/geldois/osint-engine/commit/09ad37427914b1c7bdeee00ee68e1a6a33b7d7c3))

- **domain**: Derive entity id from named field pairs and require identity_fields explicitly
  ([`e241325`](https://github.com/geldois/osint-engine/commit/e241325070b73eed081861a4e14859117e97b17d))

- **hashers**: Replace passlib with argon2-cffi direct usage
  ([`ecdb410`](https://github.com/geldois/osint-engine/commit/ecdb4105d10bc36248c13d6b7d5290d04c762ebe))

- **infrastructure**: Version brasilapi cnpj endpoint and harden Payload type casting
  ([`9eb327a`](https://github.com/geldois/osint-engine/commit/9eb327af9a98f48e11c0d24a574a0c21e6f95b94))

- **interface/http**: Promote framework-agnostic modules to http/ and replace match dispatch with
  dicts
  ([`f025559`](https://github.com/geldois/osint-engine/commit/f0255591a5c48157b64fbddc3f3180a45091e56a))

- **observability**: Relocate logging and request middleware into layered modules
  ([`e4e4abf`](https://github.com/geldois/osint-engine/commit/e4e4abfcdf668c4663089cace41f618d6ddfb5a5))

- **tests**: Consolidate brasilapi test data and extract payload tests
  ([`138ab3f`](https://github.com/geldois/osint-engine/commit/138ab3f47f1a315056a64249837b433b36722970))

- **tests**: Migrate fakes.py to fakes/ package and add make_container fixture
  ([`edd9290`](https://github.com/geldois/osint-engine/commit/edd9290a12c5179b0dfd28df9e21c99c74ddcab0))

### Testing

- Add BrasilAPICNPJFetcher tests; extract serve; configure pytest-asyncio session loop
  ([`fe1b41c`](https://github.com/geldois/osint-engine/commit/fe1b41c1296120f21a8ff9e305c20000eca3fe9b))

- Fix imports after error renames; drop deleted-method tests; improve test method names
  ([`f07c2ba`](https://github.com/geldois/osint-engine/commit/f07c2ba1b0d08d7c901047aa1267a9b1ace35537))

- Restructure fixture hierarchy and expand coverage across http, auth, and domain
  ([`a366b63`](https://github.com/geldois/osint-engine/commit/a366b6330e640a6ff14ae2613bd6242e3d4ec342))

- **errors**: Assert message content wherever domain errors are raised
  ([`9770688`](https://github.com/geldois/osint-engine/commit/9770688fcc5c619d1f163fc2c53d5ed0025d4110))

- **infrastructure/sources**: Add BrasilAPI mapper tests and make_payload fixture
  ([`f848b74`](https://github.com/geldois/osint-engine/commit/f848b74753f7806972c0e74e36de972398861fe4))

- **interface/http**: Add error_handler test suite; fix datetime/UUID JSON serialization
  ([`b1c2877`](https://github.com/geldois/osint-engine/commit/b1c28777c9a6ef07f88685b8e3e9f1e0e4d9e136))

- **interface/http**: Add presenter and schema test suites
  ([`7accdd0`](https://github.com/geldois/osint-engine/commit/7accdd057958dfa08bfb78ebf757fe77cbb202ce))

- **services**: Add PyJWTService test suite with algorithm property
  ([`6c97675`](https://github.com/geldois/osint-engine/commit/6c976751d77746a02f29bd44ecede385f86a3750))


## v1.4.0 (2026-07-06)

### Bug Fixes

- **router**: Accept raw slash in CNPJ path param via :path type
  ([`869271b`](https://github.com/geldois/osint-engine/commit/869271b6bf0ba3b4eda1683ae35be681323c112d))

### Build System

- **deps**: Add hypothesis for property-based testing
  ([`c5f4ae2`](https://github.com/geldois/osint-engine/commit/c5f4ae240cc421825df8281b630a45bcbfdf0cb9))

### Documentation

- Add ADRs 0011-0013 and update TO-DO
  ([`7289d62`](https://github.com/geldois/osint-engine/commit/7289d62b40e0f01284e3586002d9bc75b77c9ca9))

### Features

- **deploy**: Add brutal multi-stage Dockerfile and .dockerignore for simple and secure deployments
  ([`4eb4e31`](https://github.com/geldois/osint-engine/commit/4eb4e3105b99113f237018887bb2049470916206))

### Refactoring

- **domain**: Make Edge generic[IDType, SourceID, TargetID] and add self-loop and graph consistency
  validation
  ([`2a95681`](https://github.com/geldois/osint-engine/commit/2a95681c690e48641250314cc8711f99d6ea611f))

### Testing

- **application**: ExpandByCNPJ orchestration and transaction protection; rename fake fixtures to
  make_fake_* convention; add FakeCNPJFetcher
  ([`37cadef`](https://github.com/geldois/osint-engine/commit/37cadef220e22cfe3d6c3b3dabdcc4adc5be6baf))

- **domain**: Add _calculate_id determinism and non-deterministic value error tests
  ([`7ec0bfa`](https://github.com/geldois/osint-engine/commit/7ec0bfa81516cc077d2fb441582398fc15dd2220))

- **domain**: Reorganize tests by behavioral invariant and add edge and hypothesis permutation
  coverage
  ([`20f4713`](https://github.com/geldois/osint-engine/commit/20f471357790beb58c397cfcda239187e0c1fc7c))


## v1.3.0 (2026-07-04)

### Documentation

- Add ADR-0010 and update TO-DO
  ([`12cf024`](https://github.com/geldois/osint-engine/commit/12cf024bdc8ce2afc9cba80aa233f44f02c0703b))

- **readme**: Add release badge in canonical badge order
  ([`47feb1b`](https://github.com/geldois/osint-engine/commit/47feb1b7fd10a02f5acee89fd982c3f84a3e2a61))

- **todo**: Register missing test coverage for PasswordHasher and error_handler
  ([`b61655d`](https://github.com/geldois/osint-engine/commit/b61655dd8ba20e1d631714ee55cb3af602724848))

- **todo**: Register sanitize_cnpj hardening and test coverage
  ([`8765748`](https://github.com/geldois/osint-engine/commit/87657487ed36e9c5a7cfb13f8c295c1f0ecf6f4b))

### Features

- **domain**: Enrich entity attributes and declare identity_fields per entity
  ([`99db246`](https://github.com/geldois/osint-engine/commit/99db246e64171de35268e76a8782eda44209f556))

- **infrastructure**: Map enriched entity fields from BrasilAPI CNPJ response
  ([`5cda2ae`](https://github.com/geldois/osint-engine/commit/5cda2aef0250cf690fd039e37b90d2e84fe2b6bb))

- **interface**: Add CNPJ sanitizer and wire it into the GET handler
  ([`afd591c`](https://github.com/geldois/osint-engine/commit/afd591c8eddb1f051a70232747fa30e44a41f826))

- **interface**: Expose new entity fields in schemas and presenters
  ([`046dabf`](https://github.com/geldois/osint-engine/commit/046dabf147ab96c3b715405a04f7afd69b3283b5))

### Refactoring

- **domain**: Introduce identity_fields subset and deterministic-type whitelist
  ([`2ddb5da`](https://github.com/geldois/osint-engine/commit/2ddb5da69606bcc7c0b54399237c53e90ad9e1d1))

### Testing

- Adapt fakes and add mem_seeder and shared fixtures
  ([`1db9c2f`](https://github.com/geldois/osint-engine/commit/1db9c2f9368a4b7a1d04dd845750e348fbad97c3))


## v1.2.0 (2026-07-02)

### Bug Fixes

- **domain**: Decouple UUID from kwarg names and block non-deterministic str values
  ([`3cb0022`](https://github.com/geldois/osint-engine/commit/3cb002253e666b509c765c55e3a7d8fe1077623c))

### Chores

- Register known test gaps in TO-DO
  ([`d5c0daf`](https://github.com/geldois/osint-engine/commit/d5c0daf8a5edd8158ce0d4f7d03ff92f7af81c66))

- **build**: Migrate to hatchling, pin deps, complete project metadata, and scaffold env
  ([`f239124`](https://github.com/geldois/osint-engine/commit/f23912422ba84a473d53b077ce0ad1ea8764aa2e))

- **ci**: Explicitly set prerelease = false on main release branch
  ([`d43f93a`](https://github.com/geldois/osint-engine/commit/d43f93a2b1bac95e23bd4f237cca9588b48562dc))

- **ci**: Replace ci.yml with pinned test/release workflows, add mise toolchain and act config
  ([`4fe158e`](https://github.com/geldois/osint-engine/commit/4fe158e43fe1681c5b7395fa1c9db9a22ff1eb08))

- **deps**: Promote httpx2 and pydantic to runtime dependencies
  ([`1488e9f`](https://github.com/geldois/osint-engine/commit/1488e9f3b032b1e00fb9dc73d483c62d818808bb))

- **deps**: Replace httpx with httpx2
  ([`e4656d4`](https://github.com/geldois/osint-engine/commit/e4656d4ab7c8501e6068033edc5aef512064f80b))

### Continuous Integration

- Add GitHub Actions workflow, license, and markdownlint config
  ([`8a09532`](https://github.com/geldois/osint-engine/commit/8a0953245973157618e3759d376ef3a2919b4a1b))

### Documentation

- Rewrite README and ADRs for public portfolio
  ([`37ffcb6`](https://github.com/geldois/osint-engine/commit/37ffcb65f5205288ab01d92067678e62e829f599))

- Update README for auth flow, add ADR-0006 through ADR-0009, expand TO-DO with auth test gaps
  ([`1854d0d`](https://github.com/geldois/osint-engine/commit/1854d0d27f8aa1f40efd9494ff804d1456816275))

- **adr**: Record BrasilAPI as MVP CNPJ data source (ADR-0005)
  ([`97908cd`](https://github.com/geldois/osint-engine/commit/97908cd8e375c4a1a3e9cb499b782231432505bc))

- **adr**: Register entity modeling and identity decisions
  ([`860263a`](https://github.com/geldois/osint-engine/commit/860263a78b75c72ccc82bf1a704140e796d89303))

### Features

- Wire full boot sequence in __main__ with settings, DI container, and uvicorn
  ([`d18ea74`](https://github.com/geldois/osint-engine/commit/d18ea749f0da9c7e2137334f00cb20c6507e846c))

- **application**: Replace get_graph_by_root_id with ExpandByCNPJ use case
  ([`cf31e9c`](https://github.com/geldois/osint-engine/commit/cf31e9c9b0c07430a24d19a2f5009efe8f5b63e6))

- **auth**: Implement JWT authentication layer
  ([`e308ff7`](https://github.com/geldois/osint-engine/commit/e308ff78483ac3432ce602417ca5842470149af3))

- **config**: Add frozen Settings, DI Container, and composition root
  ([`dcefb5b`](https://github.com/geldois/osint-engine/commit/dcefb5bb2645345f8b24cea0877941ab132b6397))

- **domain**: Refine node entity field definitions
  ([`1fb7064`](https://github.com/geldois/osint-engine/commit/1fb706482e642b04832e864d1adb38d6db76f1e7))

- **http**: Initialize FastAPI application
  ([`52113b7`](https://github.com/geldois/osint-engine/commit/52113b75a32ab28f038e7259b45a8ac4190eec71))

- **infrastructure**: Implement BrasilAPI CNPJ fetcher with typed schema, mapper, and error
  hierarchy
  ([`c041bd6`](https://github.com/geldois/osint-engine/commit/c041bd6ed8e2eb33c0155fbd0b3be2924384cb0e))

- **interface**: Add HTTP routers, presenters, schemas, and centralised error handler
  ([`043d576`](https://github.com/geldois/osint-engine/commit/043d5767720cf91ac06ba1c7d86d54901f0d2a9a))

- **observability**: Add structlog setup and correlation-ID HTTP middleware
  ([`ed498ec`](https://github.com/geldois/osint-engine/commit/ed498ec3a4bfb9df816d7cd68f40907aced7ad24))

### Refactoring

- **application**: Unify Command/Query under frozen UseCase[T] and wire repository fields to UoW
  ([`188685c`](https://github.com/geldois/osint-engine/commit/188685c547578c48888f4dc486aebf2121c27272))

- **domain**: Expose error_code on DomainError and tighten edge/graph contracts
  ([`2da300d`](https://github.com/geldois/osint-engine/commit/2da300d19e2baf883309b49975a6e8f21505ee7c))


## v1.1.0 (2026-06-14)

### Features

- **application,domain**: Drop slots, add application contracts and Graph value object
  ([`01129af`](https://github.com/geldois/osint-engine/commit/01129afda44913173d6ecd4a2d319274fe82b3ff))

- **domain**: Assign deterministic namespaces to all nodes and edges
  ([`fe8767a`](https://github.com/geldois/osint-engine/commit/fe8767a0168644b14fe1fed45e4787748d0cb647))

- **persistence**: Implement in-memory layer with full test coverage
  ([`f3c8b31`](https://github.com/geldois/osint-engine/commit/f3c8b31150bebb031b841c38e31accabf4170b00))


## v1.0.1 (2026-06-04)

### Refactoring

- **domain**: Migrate to pure graph model with typed nodes and edges
  ([`22a80a9`](https://github.com/geldois/osint-engine/commit/22a80a94d9639d1c02587293389a6b095babd133))

### Testing

- **domain**: Cover Entity, EntityError and DomainError contracts
  ([`bf59b2a`](https://github.com/geldois/osint-engine/commit/bf59b2a07326e913018f6980059971d792571b66))


## v1.0.0 (2026-05-31)

- Initial Release
