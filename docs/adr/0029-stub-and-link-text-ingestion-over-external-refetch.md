# Stub-and-link text ingestion over external re-fetch

## Status

Accepted

## Context

Roadmap step 3 needed a way to ingest free text and discover which known entities it mentions. The first design
considered treated a text mention the same as a CNPJ/CPF/CEP path parameter: extract the identifier, then call the
existing external fetchers (BrasilAPI, Portal da Transparência) to enrich it, exactly like `/cnpj`/`/cpf` already do.
That was rejected on two grounds. First, `/cpf`'s upstream endpoint is currently rejecting this deployment's API key
with a bare `403` (tracked in `TO-DO.md`, root cause unconfirmed), so routing text-derived CPFs through the same path
would make ingestion depend on an external outage outside this project's control. Second, and more fundamentally, the
user explicitly wanted a hard boundary: probabilistic, text-derived signal must never silently merge into or overwrite
existing entity data, no matter how confident the match — only a deterministic, content-derived identity (the same
`_calculate_id` every entity already uses) is allowed to resolve to "this is the same real-world thing."

## Decision

`IngestText` never calls an external API. It extracts CPF/CNPJ/CEP-and-number via regex plus a mod-11 checksum, computes
each match's deterministic entity id the same way the domain always has, and looks it up in `uow.nodes`. A hit adds only
a mention edge (`PersonMentionedInText`/`CompanyMentionedInText`/`AddressMentionedInText`) — the existing entity is
never touched. A miss creates a minimal stub carrying only its identity field, with every other field `None`, and the
same mention edge. The returned graph is rooted at a new `TextSource` node (id derived from the text's own content, so
re-ingesting identical text is idempotent), which every matched or stubbed entity links back to.

## Consequences

Text ingestion has zero dependency on upstream API availability and can never corrupt existing entity data with an
unverified signal — the worst it can do is add a stub with nothing but an identity field, which is trivially safe.
Enriching a stub still requires a separate, explicit call to the existing `/cnpj`/`/cpf`/`/cnep`/`/ceis` endpoints;
nothing in this feature does that automatically. Name and free-text company/person mentions — anything without a
deterministic checksum — are out of scope here: matching those needs fuzzy comparison against existing entities, which
this design deliberately excludes to keep the "never merge on an unverified signal" guarantee intact. That
fuzzy-matching layer (a `PossiblyMatches` edge already sketched in the domain, confidence-scored, never auto-merged) is
a distinct future iteration, not an extension of this one.
