# CompanyOwnsCompany as a concrete edge type over a generic ownership edge

## Status

Accepted.

## Context

The QSA (quadro de sócios e administradores) feed from BrasilAPI includes legal-entity partners
(`identificador_de_socio == 1`), which need a company-to-company ownership relationship carrying the same
`entry_date`/`role` shape already modeled by `PersonOwnsCompany` for person partners. Two shapes were weighed:
generalizing `PersonOwnsCompany` into a single `Ownership[SourceID_co, TargetID_co]` edge reusable across both partner
kinds, or introducing `CompanyOwnsCompany` as its own concrete `Edge[CompanyOwnsCompanyID, CompanyID, CompanyID]`
subclass mirroring `PersonOwnsCompany`'s fields. Every one of the eleven existing edges follows the concrete-subtype
pattern already — `CompanyLocatedAt` and `PersonResideAt` are structurally identical (source-to-`Address` with no
extra fields) yet remain two separate classes rather than one generic address-edge — so a generic `Ownership` type
would be the first of its kind in this codebase rather than a continuation of an established convention.

## Decision

`CompanyOwnsCompany` is a new concrete `Edge` subclass (`domain/entities/edges/company_owns_company.py`), duplicating
`PersonOwnsCompany`'s `entry_date`/`role` fields and constructor shape but constraining both `source_id` and
`target_id` to `CompanyID`. It gets its own `EntityNAMESPACE.COMPANY_COMPANY` member and its own schema
(`CompanyOwnsCompanySchema`), following the same registration path every other edge already uses.

## Consequences

The type system statically prevents constructing a company-ownership edge between the wrong node kinds, and adding
this edge required no change to `Edge`'s generic bounds or to any other edge's contract. The cost is duplicated
shape between `PersonOwnsCompany` and `CompanyOwnsCompany` — the same trade-off already accepted for
`CompanyLocatedAt`/`PersonResideAt` — and, less obviously, three separate manual registration points per new edge
type (`EdgeSchemaUnion`/`EdgeSchemaRegistry` in `edge_schema.py`, and the standalone `_EDGE_MAP` in
`edge_presenter.py`), none of which are discovered automatically; missing the presenter map specifically only
surfaces at runtime as a 500 on serialization, not at type-check time.
