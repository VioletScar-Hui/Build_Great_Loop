# STATE — durable, idempotent recovery

- Persist machine state that conforms to `state.schema.json`; keep prose in a
  separate append-only run log.
- Bind state, memory, idempotency keys, connector calls, and evidence receipts to
  the runtime `authority_context`: tenant, channel, principal, connector identity,
  memory namespace, and permission snapshot hash. On any mismatch, fail closed at
  the human gate; never silently migrate or broaden authority.
- Before acting, assign a fresh `run_id`, increment `attempt`, compute an
  `idempotency_key`, and atomically claim one item.
- After the external effect, persist its `output_ref`; mark `done` only after a
  verifier receipt points to evidence.
- On startup, reconcile every `in_progress` item. Inspect the external effect and
  evidence before retrying; never infer failure merely from a stale timestamp.
- Write a temporary sibling file, validate it, then atomically replace state.

Acceptance: terminate once immediately after claim and once immediately after the
effect. Both restarts converge without a duplicate effect or false `done`. Restart
once with a different channel/principal fixture and prove that no state or memory
is read and no effect executes.
