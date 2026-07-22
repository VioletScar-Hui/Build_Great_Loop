# Runtime and host adapters

Keep CORE provider- and host-neutral. Resolve model, effort, thinking, API message
shape, and session commands at runtime from a dated capability snapshot. Validate
the resolved contract with `scripts/validate_runtime_contract.py`.

## Role-based model policy

Declare requirements such as `intelligence_sensitive`, `highest_available`, and
`cheapest_capable`; do not put provider model IDs in the reusable harness. The
adapter records the concrete model, workload, effort, thinking mode, and reserved
output tokens for each role so eval results remain comparable.

Current Claude adapter baseline (2026-07-22):

- Opus 4.8 coding/agentic workloads start at `xhigh` effort; `max` remains an
  eval-driven exception because overthinking can add cost without enough gain.
- Sonnet 5 uses adaptive thinking when the request omits `thinking`; it does not
  use manual `budget_tokens`. Reserve enough `max_tokens` for thinking, tool use,
  and final output.
- A capability-snapshot or adapter change invalidates old comparable results
  unless the eval record includes the new model-policy hash.

Sources:

- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

## Assistant prefill compatibility

For current Claude models, reject a final partial assistant message used as a
prefill. Use structured outputs, enum tools, an explicit schema, or a new user
message for continuation. This API restriction is unrelated to PROFILE's
user-visible, overridable preference defaults; call those `profile_defaults`
when ambiguity matters.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

## Claude Code session semantics

For Claude Code capability week 2026-W29 and later:

- `/fork` creates a separately managed background session. Give it independent
  session, run, lease, budget, and cancellation IDs; include it in active-run
  cancellation and operator views.
- `/subtask` performs work inside the current session and does not receive those
  independent background-operation identities.

Never emit either command until the installed host capability is verified. Other
hosts map the same abstract operations—`background_session` and `in_session`—to
their own supported mechanisms.

Source: https://code.claude.com/docs/en/whats-new/2026-w29

## Eval identity

Comparable eval runs record:

```yaml
eval_context:
  harness_hash: <sha256>
  tool_interface_hash: <sha256>
  controller_id: <stable versioned ID>
  permission_profile_hash: <sha256>
  model_policy_hash: <sha256>
  language: <BCP-47 or stable project code>
```

Changing the control interface or permission profile changes the system under
test even if the model stays fixed. Mark unmatched historical results `STALE`.
