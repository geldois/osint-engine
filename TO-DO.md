# TO-DO

## fix(domain)

- [ ] Replace `_validate_deterministic_str` heuristic with a whitelist of known-deterministic types

## test(domain)

- [ ] `_validate_deterministic_str` raises `NonDeterministicValueEntityError` for objects without `__str__` or `__repr__` overridden
- [ ] `calculate_id` produces the same UUID after renaming a kwarg key while keeping the same value
- [ ] `calculate_id` produces the same UUID regardless of kwarg insertion order
