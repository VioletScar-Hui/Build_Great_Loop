# Run Log — <loop name>

Human-readable view derived from `run-events.jsonl`. It is not the source of truth
for retries, cost enforcement, gates, approvals, or claims.

One line per run:

```text
[ISO timestamp] run=<id> level=<L1|L2|L3> result=<...> attempts=<n> verified=<pass/fail/unknown> cap=<used>/<max> gate=<none|id> next=<...>
```

Retro findings cite immutable event IDs from the JSONL source.
