# `identity_fields` subset for entity ID derivation

## Status

Accepted

## Context

After ADR-0003, entity identity was computed by passing **all** constructor kwargs to `_calculate_id`. This worked
correctly for entities whose every field is part of their natural key (e.g., the original two-field `Address`).
However, as entities grew richer — `Address` gained `city`, `complement`, `neighborhood`, `state`, and `street`;
`Company` gained `registration_status_date`, `registration_status_reason`; `Person` gained `age_range`; `Cnae`
gained `description`; `PersonOwnsCompany` gained `entry_date` and `role` — hashing all fields into the ID became
semantically wrong:

- Changing a descriptive attribute (e.g., correcting a trade name typo) would produce a **new** entity ID,
  breaking deduplication and idempotency.
- The UUID5 name would encode volatile, non-identifying data, making it sensitive to upstream data drift.

The domain needed a clean way to declare *which* fields constitute the canonical key of an entity, separately from
*which* fields the entity carries as attributes.

## Decision

Add an `identity_fields: frozenset[str] | None` parameter to `Entity.__init__`. When provided, only the specified
fields are forwarded to `_calculate_id`; all remaining kwargs are still set as attributes. When `None`, all kwargs
are forwarded (preserving the original behaviour for test fakes and the `Graph` entity).

`_validate_identity_fields` is called before ID derivation to assert that every name in `identity_fields` exists
as a key in `kwargs`, raising `InvalidIdentityFieldEntityError` on violation.

Concrete entities (`Address`, `Cnae`, `Company`, `Person`) declare their own `identity_fields` at construction
time by passing the appropriate `frozenset` up the `super().__init__` chain. `Edge` defaults to
`frozenset({"source_id", "target_id"})` unless an explicit override is supplied.

`_validate_deterministic_str`, which checked for `__str__`/`__repr__` overrides as a heuristic for
determinism, was replaced by an explicit whitelist `_DETERMINISTIC_TYPES` (`bool`, `datetime`, `Decimal`, `int`,
`str`, `None`, `UUID`). The whitelist is more precise, self-documenting, and eliminates false negatives caused by
custom types that happened to implement `__str__`.

## Consequences

- **Stable identity under attribute growth:** adding new descriptive fields to an entity no longer silently
  changes its ID. The identity contract is explicit and version-safe.
- **Explicit over implicit:** identity is declared at construction, not inferred from the full kwargs set.
  Any mismatch between `identity_fields` and the actual kwargs is caught eagerly at construction time.
- **Test fakes remain compatible:** passing `identity_fields=None` opts out of the new path, so all existing
  fake entities are unaffected without changes to their logic.
- **Trade-off:** each concrete entity's `__init__` is slightly more verbose (must forward `identity_fields`).
  This is acceptable because the verbosity is proportional to the explicitness gained.
- **Trade-off:** the `_DETERMINISTIC_TYPES` whitelist must be extended whenever a new primitive type is
  intentionally used as an identity field. The current set covers all types presently used in identity keys.
