# Identity normalization lives on the entity via _calculate_id override

## Status

Accepted.

## Context

QSA legal-entity partner stubs and the later-enriched `Company` record for the same real company can arrive from the
same source (BrasilAPI) with differently formatted `cnpj` strings, depending on which payload field feeds them: the
top-level `cnpj` versus a partner's `cnpj_cpf_do_socio` inside `qsa`. `RevisionMergePolicy` only reconciles two
revisions that resolve to the same `id`, so this formatting variance silently defeated the merge, leaving the stub as
a permanent orphan node. Normalizing at the mapper boundary, before entities are constructed, was considered and
rejected: `Entity.__init__` computes identity from and stores raw attributes from the same `kwargs` dict, so
normalizing before `super().__init__` would make the normalized value the one stored on the entity, destroying the
original formatting `cnpj`/`cpf` need to keep for faithful display. It would also require every future mapper for
every future source (CEIS/CNEP, text ingestion) to duplicate the same normalization knowledge, which is a rule about
what makes two `Company` instances "the same," not an infrastructure concern.

## Decision

`Company` and `Person` override the classmethod `_calculate_id`, mirroring the existing `Graph._calculate_id`
override, to normalize only the identity-bearing field (`cnpj`/`cpf`) through a shared pure helper
(`domain/value_objects/normalization.py::digits_only`) before delegating to `super()._calculate_id(**kwargs)`. The
raw, unnormalized value the constructor received stays stored on the instance untouched.

## Consequences

Identity is now stable across formatting variance from any current or future data source without any mapper needing
to know about it, and `evolve()`/`reconstruct_kwargs()` round-trip correctly because normalization is re-derived
fresh from the always-raw stored value on every call rather than being baked into storage once. The cost is that this
is a per-entity decision repeated wherever it applies rather than one central mechanism — `Address.number` is a known
similar case deliberately left unnormalized, since it can hold non-numeric values like `"S/N"` that `digits_only`
would silently reduce to an empty string. `digits_only` is also lossy for masked identifiers: a masked CPF like
`***128734**` collapses to whatever digits remain visible, which is accepted because the masking is applied upstream
by Receita Federal under LGPD and no normalization can recover redacted data. A stronger fix — real `CNPJ`/`CPF`
value object types owning both normalization and mod-11 checksum validation — is deferred to when the roadmap's text
ingestion work forces loosening `Entity`'s exact-type `_validate_deterministic_type` check anyway.
