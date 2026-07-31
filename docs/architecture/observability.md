# Observability — what it does

Every log line the running process emits is structured rather than free-form text, so a line can be filtered, searched,
and correlated mechanically instead of parsed by eye. A correlation identifier is attached to the context of a single
incoming request and automatically carried onto every log line produced while that request is being handled, so every
entry belonging to the same request can be found and grouped together after the fact — the same identifier is also
surfaced back to the caller on an error response, so a report from a caller can be matched directly against the logs for
that exact request.

## Decisions

Nothing in this area has required an actively weighed trade-off yet; its setup is straightforward configuration, not a
decision under real alternatives.
