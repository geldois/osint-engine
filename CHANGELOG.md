# CHANGELOG

<!-- version list -->

## v1.8.0 (2026-08-17)

### Bug Fixes

- **domain**: Derive Graph.content_id from constituents' content, not identity
  ([`78b9415`](https://github.com/geldois/osint-engine/commit/78b9415a54f726671cd023e40eae644f039f97ef))

- **domain**: Preserve masked-CPF digit position in Person identity
  ([`e210eda`](https://github.com/geldois/osint-engine/commit/e210eda032f7d953d8efb6ed8312f3c195cf7c24))

- **gates**: Carry untracked live-API fixtures into the materialized snapshot
  ([`4b2a3f4`](https://github.com/geldois/osint-engine/commit/4b2a3f40017798cd4cd997ef396ecbd7328ad392))

- **harness**: Block agent from pre-running check --full before commit
  ([`f7f6274`](https://github.com/geldois/osint-engine/commit/f7f627405bcde25358d119739f3e0ae6408389fa))

- **harness**: Fire the autofix hook on MultiEdit, not just Edit and Write
  ([`799bb7b`](https://github.com/geldois/osint-engine/commit/799bb7ba604ea08968c839ccab23c49b64a6d63e))

- **harness**: Match Stop hook on all matchers via empty string
  ([`cfd1181`](https://github.com/geldois/osint-engine/commit/cfd1181e30bb7ed117c677c7e649a451f133ecde))

- **harness**: Run the commit-time fixer on renamed files too
  ([`f0dfb47`](https://github.com/geldois/osint-engine/commit/f0dfb474d91d8e2cfab5c403f7d8d0257edb76bd))

- **harness**: Scan every statement for a bypassed direct check, not just the string's start
  ([`7f514f3`](https://github.com/geldois/osint-engine/commit/7f514f3db51df12cfa5a70a5ef20a87b1e0595a3))

- **harness**: Stop the agent from self-verifying with the gate facade
  ([`18a28c8`](https://github.com/geldois/osint-engine/commit/18a28c846f3470f39790b16335a67df7abe0768c))

- **harness**: Sync code-review-graph after commit lands
  ([`1fe3543`](https://github.com/geldois/osint-engine/commit/1fe3543b06aadfa5c0771a9481070df92153a588))

- **harness**: Type hook IO with casts so it stays clean under stricter basedpyright
  ([`cdcd535`](https://github.com/geldois/osint-engine/commit/cdcd5350b5d71b000cd2a9ece9aa277d5bd2c8f1))

- **scripts**: Stop the comment stripper from eating sqlc query annotations
  ([`1d0441f`](https://github.com/geldois/osint-engine/commit/1d0441fc21286193536448da0bed4402a2502d29))

- **tests**: Detect the container socket by type instead of existence
  ([`57916e0`](https://github.com/geldois/osint-engine/commit/57916e04bb8968f31374286dfbb8da723a2cadaa))

- **tests**: Exclude Python keywords from the generated identifier strategy
  ([`4908f1f`](https://github.com/geldois/osint-engine/commit/4908f1f1d6c63c8966ca5769dfc159990699559c))

- **text-ingestion**: Dedicate FieldTooLargeError to oversized CSV fields
  ([`f368f9a`](https://github.com/geldois/osint-engine/commit/f368f9a328f6384304aa6a56261af57dafade98a))

### Chores

- Bump project version to 1.7.0 in uv.lock
  ([`d9b1a37`](https://github.com/geldois/osint-engine/commit/d9b1a37e5286ef5c41e85c66f2df157369f458a3))

- Drop the opencode harness in favour of Claude Code only
  ([`df1c012`](https://github.com/geldois/osint-engine/commit/df1c01234176c68022de3d478bc1a67814aa00ce))

- Untrack recorded live-API fixtures
  ([`def741f`](https://github.com/geldois/osint-engine/commit/def741f6e3b0580d4f774e4e529647f1c07be558))

- **harness**: Align local Claude Code harness with global conventions
  ([`397705c`](https://github.com/geldois/osint-engine/commit/397705c0aa3bbe68d3c184192f97ca0cf4aa2816))

- **harness**: Modernize the self-owned quality-gate harness
  ([`5c74f0f`](https://github.com/geldois/osint-engine/commit/5c74f0ffc9f6d6edcefeb75ab436ec7f24c06ab7))

- **harness**: Remove dead checks-triager guard and stale doc references
  ([`9491dbc`](https://github.com/geldois/osint-engine/commit/9491dbc87ca9061ffe7476722da02689e28c499b))

- **hooks**: Confirm lint-green per edit via additionalContext
  ([`048609c`](https://github.com/geldois/osint-engine/commit/048609c341d5f36ae9d33488f85b5d313d563237))

- **hooks**: Remind to check the README diagram after semantic changes
  ([`545a5fc`](https://github.com/geldois/osint-engine/commit/545a5fc208f35dfc327bf19cea46f8201b9b6904))

- **lint**: Ignore PLR0917 for tests, matching PLR0913's existing exemption
  ([`a8bfc3e`](https://github.com/geldois/osint-engine/commit/a8bfc3eef24f50911d2a64205f1faf8108695e96))

- **tooling**: Ignore hypothesis and import-linter caches in dprint
  ([`22b0679`](https://github.com/geldois/osint-engine/commit/22b067997aee3944364c3d6c496de2213f3b4302))

### Code Style

- Apply formatter line-wrap the pre-commit gate had reformatted post-tree
  ([`1d42383`](https://github.com/geldois/osint-engine/commit/1d42383287ecdaeaf798a30e892566b1aad57a7d))

### Documentation

- Add CONTEXT.md as the project's ubiquitous language
  ([`e035a98`](https://github.com/geldois/osint-engine/commit/e035a98f52470e9ec85790cc27a415443cd8117c))

- Describe spreadsheet ingestion in README and architecture docs
  ([`f458acf`](https://github.com/geldois/osint-engine/commit/f458acf660d03e14838d4546790d6de003617df0))

- Describe the atomic pattern catalog and the pattern-name/pattern-set split
  ([`9883682`](https://github.com/geldois/osint-engine/commit/9883682d3a39720e79b1015bab6761e827ff26fb))

- Describe the graph-history endpoint and the id/content_id split
  ([`049b729`](https://github.com/geldois/osint-engine/commit/049b729788f7623978793a7302732086173ef2e6))

- Describe the keep-incoming merge default and its graph-history debt
  ([`f476461`](https://github.com/geldois/osint-engine/commit/f476461fe3ccd07977781f7ef19c2af11aa3c944))

- Describe the sqlc-generate regen command
  ([`7b22fe9`](https://github.com/geldois/osint-engine/commit/7b22fe9309b076861ac5a361dbc0b36f84a31e91))

- Reflect the pattern-sets UoW move in the architecture diagram
  ([`20c6756`](https://github.com/geldois/osint-engine/commit/20c675668ebeb50f6ebff4f60b2e6365d6a38a5f))

- Repoint ADR references to docs/architecture
  ([`260c234`](https://github.com/geldois/osint-engine/commit/260c23405fe66c7877267470c35025321089f0ea))

- Rewrite the architecture prose against the CONTEXT.md vocabulary
  ([`16252e5`](https://github.com/geldois/osint-engine/commit/16252e528bd200dcf77c652e129ce534b31a4c52))

- **architecture**: Describe possible-match as CPF overlap, not name similarity
  ([`96ec652`](https://github.com/geldois/osint-engine/commit/96ec65234cc4e2a5a7fc166820eafeca044d0418))

- **architecture**: Replace docs/adr with per-area architecture docs
  ([`07d85f7`](https://github.com/geldois/osint-engine/commit/07d85f7be3e0e03fe4201974e760a9d0b9a02f11))

- **cpf**: Describe the KipFlow provider swap and its reuse lock
  ([`1470215`](https://github.com/geldois/osint-engine/commit/14702158bf88632b893daadfefd6339ea27d264b))

- **readme**: Sync architecture diagram with current backend
  ([`4fc4149`](https://github.com/geldois/osint-engine/commit/4fc4149830f9738946d99974bbb4524b9da434e3))

### Features

- **cpf**: Replace Portal da Transparência with KipFlow as the CPF provider
  ([`8888fee`](https://github.com/geldois/osint-engine/commit/8888fee8adf2943c7b76420e09df8a5c81e3425e))

- **deploy**: Add Oracle Cloud deploy pipeline
  ([`af88627`](https://github.com/geldois/osint-engine/commit/af88627ada2516d1d4d01b4a9077e11311a5a97e))

- **deploy**: Orchestrate wait-db and migrate up before serve via entrypoint
  ([`ff7b905`](https://github.com/geldois/osint-engine/commit/ff7b905dc5e8010f93f2b42f87ca32b170a1ce67))

- **domain**: Add PossiblyMatches generic edge for cross-entity similarity
  ([`ff5bfe3`](https://github.com/geldois/osint-engine/commit/ff5bfe34543fa00e8059bd82576201024c014130))

- **domain**: Validate masked documents strictly and add overlap comparison
  ([`b2005ef`](https://github.com/geldois/osint-engine/commit/b2005ef4feedef9028cf911c66e93adf14b6075a))

- **graph-history**: Expose stored Graph revisions via GET /graphs/{root_id}/history
  ([`d018d5f`](https://github.com/geldois/osint-engine/commit/d018d5f3a4cf97877c8074ffda8bcf5b22a0b98e))

- **harness**: Add sqruff as the deterministic SQL gate
  ([`b13467c`](https://github.com/geldois/osint-engine/commit/b13467cc1dcbfbaba8de546b4c424c25ff51ed27))

- **harness**: Extend pre-commit safe-autofix to every fixer-owned filetype
  ([`f2867c5`](https://github.com/geldois/osint-engine/commit/f2867c5b68e3744d938e734d31adefc6d105e2bf))

- **harness**: Self-provision the local .env in the gate runner
  ([`ff77a5a`](https://github.com/geldois/osint-engine/commit/ff77a5a386aab827e1fd818df657bcb38c7dfd5f))

- **harness**: Strip agent-authored comments and nudge architecture-doc updates
  ([`f109ddc`](https://github.com/geldois/osint-engine/commit/f109ddcdba8526b11e5776aa8f833feec814a63a))

- **harness**: Surface failing-gate output inline on every channel
  ([`8130fe9`](https://github.com/geldois/osint-engine/commit/8130fe9d7e3373c9342c7c1c1e36a571adbd1b5c))

- **http**: Add health endpoints and unify expansion rate limiting
  ([`baeacff`](https://github.com/geldois/osint-engine/commit/baeacff010d54baa703f21f02d804c9996c94f22))

- **matching**: Produce and expose PossiblyMatches fuzzy cross-entity edges
  ([`206d08b`](https://github.com/geldois/osint-engine/commit/206d08b23ab61ef09b6b535efd0e64efd8b145cb))

- **persistence**: Make nodes/edges individually addressable and provenance-tracked
  ([`1a96d64`](https://github.com/geldois/osint-engine/commit/1a96d6425be2644e480e00ac7d3a56d0f892ae72))

- **revision**: Keep incoming revisions by default instead of filling nulls
  ([`c2217e8`](https://github.com/geldois/osint-engine/commit/c2217e81d2019a39e89305052107bf89652d905e))

- **text-ingestion**: Accept .xlsx/.csv uploads via POST /text-ingestion/file
  ([`32fde3e`](https://github.com/geldois/osint-engine/commit/32fde3e183cad0472023c39b1300475ade106011))

- **text-ingestion**: Add stub-and-link entity extraction from free text
  ([`ca80385`](https://github.com/geldois/osint-engine/commit/ca80385a003f134ddcd6fe9b8740eeb45bb4835b))

- **text-ingestion**: Compose individually addressable pattern names per request
  ([`097d4bb`](https://github.com/geldois/osint-engine/commit/097d4bb8e1e47acb6f11e0896daffa1013ff5e45))

- **text-ingestion**: Restrict access to ADMIN role only
  ([`53b0df2`](https://github.com/geldois/osint-engine/commit/53b0df29f8d0d99322432d38a3277659dd0a7aaf))

### Refactoring

- Name the provider concept out of the overloaded "source"
  ([`9ebe9c6`](https://github.com/geldois/osint-engine/commit/9ebe9c6e25091c31304e45efd962d507aa764d53))

- Split domain services out of value_objects
  ([`d8861d1`](https://github.com/geldois/osint-engine/commit/d8861d1fa5f66f322da8b0159e460547777093c6))

- Strip existing agent-authored comments and docstrings
  ([`dbb95e9`](https://github.com/geldois/osint-engine/commit/dbb95e9cd1db6b8180f0fe62f8228c1026a3fd3c))

- **config**: Load .env via python-dotenv instead of a hand-rolled parser
  ([`d980c83`](https://github.com/geldois/osint-engine/commit/d980c8344c23fa8c323c4b325c6269f64ae1c8c1))

- **domain**: Extract own_init_kwargs to dedupe entity __init__ boilerplate
  ([`4f2dc7a`](https://github.com/geldois/osint-engine/commit/4f2dc7a3a03aa43b0be18cd17ff2cf7019698c9b))

- **harness**: Rebuild the local harness around read-only hooks and zero-skip tests
  ([`6060b95`](https://github.com/geldois/osint-engine/commit/6060b9509a16a35ed3ddb6b8ce965676c52d21f1))

- **harness**: Trim the pytest gate to lean failure-only output
  ([`57042cc`](https://github.com/geldois/osint-engine/commit/57042cca4e9f29a52ce8272ea2924b444cf1acb6))

- **matching**: Compare CPF overlap instead of name similarity
  ([`4551a08`](https://github.com/geldois/osint-engine/commit/4551a0806b4a32ece07064c0ca10e9d3be53e733))

- **pattern-sets**: Move PatternSetRepository from Container into UoW
  ([`0e03555`](https://github.com/geldois/osint-engine/commit/0e035553bd436124e8f5c47bdfc074a03a11a435))

- **persistence**: Type external-credential rows via sqlc-generated models
  ([`60fcbcb`](https://github.com/geldois/osint-engine/commit/60fcbcbd81786d605840ff9affa20fdf00d88fac))

- **text-ingestion**: Resolve TextPatternSet import eagerly instead of under TYPE_CHECKING
  ([`d900d4e`](https://github.com/geldois/osint-engine/commit/d900d4e755e8eb3c3ce86c3f47cd01bc487ecb21))

### Testing

- **domain**: Confirm the for_content signal never leaks into a constructed entity
  ([`754da03`](https://github.com/geldois/osint-engine/commit/754da0316972442715f72ac6ea3f340dce8c9322))

- **matching**: Cover possibly-matches edge across the 5 CPF-producing handlers
  ([`42bfa44`](https://github.com/geldois/osint-engine/commit/42bfa4435f791e04047ff89ca101232b1b34edb5))

- **text-ingestion**: Cover spreadsheet flattening, limits, and the file upload endpoint
  ([`233e7b1`](https://github.com/geldois/osint-engine/commit/233e7b1b9ba5ce37ba4edbc53416dfa3c8d9661e))


## v1.7.0 (2026-07-28)

### Bug Fixes

- **brasilapi**: Document Payload require/optional contract and mark nullable fields optional
  ([`3e927a3`](https://github.com/geldois/osint-engine/commit/3e927a31d488a5a352b3f883f38bda3075062a86))

- **brasilapi**: Require cep and numero fields in address payload
  ([`b5901f4`](https://github.com/geldois/osint-engine/commit/b5901f4f1c99996dbce357f56b72b7de44dd3c78))

- **brasilapi**: Skip Address node when cep or numero is blank
  ([`14d56bc`](https://github.com/geldois/osint-engine/commit/14d56bc2c0508bc769689cb57f4103514f606ec3))

- **brasilapi**: Treat registration_status_date and size_category as nullable in CNPJ mapper
  ([`b7f90e6`](https://github.com/geldois/osint-engine/commit/b7f90e6280c1bc56ebba96093c5aae60754fc27c))

- **cli**: Install golang-migrate locally and disable SSL for local Postgres
  ([`7c38f2a`](https://github.com/geldois/osint-engine/commit/7c38f2a46dfe92d5ca9a8b161dd09c9bbe85613f))

- **config**: Restore PORTAL_TRANSPARENCIA_API_KEY as dev-tooling-only env var
  ([`f6fec3c`](https://github.com/geldois/osint-engine/commit/f6fec3c3b274bf7d6548c1b4b49acbb7044bef54))

- **security**: Cap combined CNPJ rate limit to protect shared BrasilAPI quota
  ([`52167d4`](https://github.com/geldois/osint-engine/commit/52167d4ea3cde1fb59b3aac3a6d261a2a46a7643))

### Chores

- Remove .gitattributes
  ([`f08fb1f`](https://github.com/geldois/osint-engine/commit/f08fb1f646d9448699fd8617d704ce9027f1b0bb))

- **config**: Remove unused PORTAL_TRANSPARENCIA_API_KEY from .env.example
  ([`ae656cc`](https://github.com/geldois/osint-engine/commit/ae656cca878528d7b5638ad0e694489052f17bb3))

- **deps**: Adopt code-review-graph for knowledge-graph tooling
  ([`d60fbdf`](https://github.com/geldois/osint-engine/commit/d60fbdf324c271d1f45fb2f4894ae2fc33ac541e))

- **deps**: Sync lockfile version with pyproject
  ([`b544895`](https://github.com/geldois/osint-engine/commit/b5448956d097da0421a172113e1205cfcc74cc97))

- **tests**: Stop tracking recorded live-API fixtures under tests/**/responses/
  ([`9abe7af`](https://github.com/geldois/osint-engine/commit/9abe7afdac94537d38b048fcbf45a1989fae243a))

### Continuous Integration

- Drop mutation-testing job and mutmut config
  ([`2be91e3`](https://github.com/geldois/osint-engine/commit/2be91e327ff17f11b381dbd152645f1d2d294d6c))

- Refresh test fixtures before running the suite
  ([`19c55e5`](https://github.com/geldois/osint-engine/commit/19c55e532f4ad456b36a4579e38c5c3baa99e752))

- **test**: Authenticate Docker Hub pulls for testcontainers images
  ([`d83796f`](https://github.com/geldois/osint-engine/commit/d83796f588379f3fdd73480b2b758f26c7d9e817))

### Documentation

- Add live deploy link to README
  ([`48c24b4`](https://github.com/geldois/osint-engine/commit/48c24b4a6a4d2b1249427961f043f4a1144aafb1))

- Record ADRs and catch up README/TO-DO for Postgres persistence work
  ([`65f6eae`](https://github.com/geldois/osint-engine/commit/65f6eae952f3d539c05be243a34ad08b012b2541))

- Reflect CNEP wiring and split out CEIS as its own TO-DO item
  ([`e7e60bf`](https://github.com/geldois/osint-engine/commit/e7e60bf6d9f308638fba716d7c8d4128978c4d47))

- **readme**: Move refresh-fixtures step ahead of the test command
  ([`e4338a5`](https://github.com/geldois/osint-engine/commit/e4338a54e860d815c76fbc8beebf61e471d78b1a))

### Features

- **ceis**: Add ExpandByCEIS and fix CNEP/CEIS Portal da Transparência fetcher contract
  ([`d58d658`](https://github.com/geldois/osint-engine/commit/d58d6587e9b5c3ca06f414725dae4f59c902ba59))

- **cli**: Add docker-compose Postgres and a wait-db command for local dev
  ([`42b9f26`](https://github.com/geldois/osint-engine/commit/42b9f26d3580bfb482047fa79f87c13bf00592cf))

- **cli**: Add Typer-based serve/migrate CLI, mirroring fastapi.py wiring
  ([`db58fa1`](https://github.com/geldois/osint-engine/commit/db58fa18009803803d18b07de22c9f9bcfcec065))

- **cpf**: Add GET /cpf/{cpf} pessoa-fisica lookup via Portal da Transparencia
  ([`623d2fa`](https://github.com/geldois/osint-engine/commit/623d2fa6a0cb4fd7b35401fecd5ab3e149a6a60d))

- **credentials**: Add GET /credentials endpoint listing configured providers
  ([`0779b7a`](https://github.com/geldois/osint-engine/commit/0779b7a6006b0dfd2491acb91d668a24d63226e2))

- **credentials**: Raise ExternalCredentialRejectedError on upstream 401/403
  ([`71b0817`](https://github.com/geldois/osint-engine/commit/71b0817e087e417d8e23a84bdde2ef2f6568ec0c))

- **persistence**: Back ExternalCredential with encrypted PostgreSQL storage
  ([`be0cb39`](https://github.com/geldois/osint-engine/commit/be0cb3959231c255c87249cbe1773033d348a1ce))

### Refactoring

- **config**: Default external_credential_encryption_key from Settings in build_container
  ([`509e897`](https://github.com/geldois/osint-engine/commit/509e8970bb29c92aae41c28e768c7c06fed0e592))

- **domain**: Add Graph.merge to union partial graphs from one subject
  ([`581f632`](https://github.com/geldois/osint-engine/commit/581f63287cc9f0803a77f7825135dc9f4d512a05))

- **domain**: Mark Address non-identity fields as optional
  ([`8452a06`](https://github.com/geldois/osint-engine/commit/8452a06d5b44f65905bc18dd27a840abcb12a9e2))

- **interface**: Rename cli.py/fastapi.py to typer_app.py/fastapi_app.py
  ([`8c77fe5`](https://github.com/geldois/osint-engine/commit/8c77fe514adb8133b4cfd9b5a14389417af7d8ce))


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
