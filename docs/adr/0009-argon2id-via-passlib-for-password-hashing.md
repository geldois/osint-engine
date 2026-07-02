# Argon2id via passlib for password hashing

## Status

Accepted

## Context

The admin user's password must be hashed before storage. The choice of algorithm and library affects both security
and implementation complexity.

| Algorithm | Memory-hard | OWASP recommended | GPU-resistant | Notes |
| --- | --- | --- | --- | --- |
| **Argon2id** | Yes | Yes (first choice) | Yes | Winner of Password Hashing Competition (2015) |
| bcrypt | No | Yes (acceptable) | Partial | Work factor is CPU-only; no memory cost |
| scrypt | Yes | Yes (acceptable) | Yes | Harder to tune; less library support |
| PBKDF2-SHA256 | No | Yes (minimum) | No | Django default; weakest of the four |

The `AuthHasher` ABC in the application layer requires only `hash_` and `verify` — it is agnostic to the
underlying algorithm. The concrete implementation lives in the infrastructure layer.

## Decision

Use Argon2id via `passlib.context.CryptContext` with `schemes=["argon2"]`. passlib acts as an adapter: it
delegates to `argon2-cffi` (the C binding) for the actual computation and manages the encoded hash format
(`$argon2id$v=19$...`) transparently.

The default passlib parameters for Argon2 (memory cost 65536 KiB, time cost 3, parallelism 4) meet OWASP
recommendations for interactive authentication.

passlib was chosen over calling `argon2-cffi` directly because it handles hash encoding, verification, and future
algorithm migration (via `deprecated="auto"`) in a single abstraction. If a stronger algorithm becomes standard,
switching schemes requires one line in `CryptContext`, not a rewrite of the hasher.

## Consequences

- **Timing attack mitigation is explicit.** `AuthenticateUser` always calls `auth_hasher.verify` regardless of
  whether the user exists, using a pre-computed dummy Argon2id hash when the user is not found. This prevents
  response-time enumeration of valid usernames.

- **Argon2id is slow by design.** Hashing takes ~300–500 ms on typical hardware with default parameters. This is
  the correct behaviour for a password hasher — it is the attacker's cost multiplier. It is not a bug to optimise
  away.

- **passlib adds a dependency.** passlib is mature but in maintenance mode. `argon2-cffi` can be used directly
  if passlib is ever dropped; the `AuthHasher` port isolates that change to `PasswordHasher` alone.

- **The dummy hash must be a valid Argon2id hash string.** An invalid string causes `argon2-cffi` to raise rather
  than return `False`, which would break the timing mitigation and expose the non-existent user via an exception
  path. The dummy was generated with `PasswordHasher().hash_(secret="dummy")` and must be replaced if the hasher
  parameters change materially.
