# Migrations — what it does

Schema changes to the one durable, database-backed store are plain, numbered, reversible SQL files — an "up" and a
matching "down" for each change — rather than any framework-specific migration language or ORM-driven schema tooling.
Applying and reverting a change is handled by a small, focused external tool with no dependency on this project's own
language runtime, kept entirely separate from the application's own code.

## Decisions

A schema-migration approach with no coupling to any particular ORM or Python migration DSL was chosen deliberately,
consistent with staying close to hand-written, inspectable SQL everywhere else this store is touched, rather than
adopting whichever migration tool happened to ship bundled with a broader persistence framework.
