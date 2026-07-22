# Harness component catalog

Assemble the smallest harness that closes the demonstrated risks. `CORE` is
always present. Every optional component must have a trigger and an acceptance
check in the component manifest; absent triggers mean absent components.

| ID | Trigger | Depends on | Acceptance check |
|---|---|---|---|
| CORE | Every loop | — | One increment follows Orient → Plan → Act → Verify → Record and stops on done, blocked, or cap |
| PROFILE | Stable preferences are available or environment facts are discoverable | — | Facts cite sources, inferences are labeled, and decisions remain user-owned |
| STATE | Work crosses runs, retries can duplicate effects, or interruption recovery is promised | CORE | Kill after claim and after effect; restart neither loses nor duplicates work, and persisted authority matches runtime authority |
| VERIFY | Consequential or judgment-based outcome needs separation from the maker | CORE; STATE when cross-run | A receipt names the check, evidence reference, result, and verifier identity |
| RULES | A failure class repeats | STATE when cross-run | The tactical rule changes without changing human success criteria, then all affected work is revalidated |
| DEVIATIONS | Plan uncertainty is material | STATE when the ledger persists | A mismatch appends expected, observed, evidence, and decision and is citable by retrospective |
| EXPLAIN | A merge or shipment is substantial | VERIFY for L2/L3 merge/ship | Claims cite evidence and delivery records comprehension or an explicit waiver |
| CAL | Quality is judgment-based and can drift at volume | VERIFY | A seeded disagreement pauses continuation and preserves disagreeing cases |
| SHAKE | L3 operation or promised recovery | STATE for recovery tests | Supervised runs pass and a deliberate interruption recovers cleanly |
| FLOW | Large/replayable fan-out or branching would flood the main context | CORE; normally STATE | Executable orchestration persists branches/intermediates; independent reads overlap while side effects are serialized |
| CONTAIN | L2/L3 or access to consequential systems/data | CORE | Environment policy blocks a seeded forbidden action and fails closed on authority mismatch |

## Component manifest

Place this near the top of a generated harness:

```yaml
components:
  - id: CORE
    reason: every loop needs bounded incremental execution
  # Add only triggered optional IDs.
omitted:
  - id: STATE
    reason: single-session and no side effect can be retried
```

The manifest is an audit surface, not an excuse to mention every module in the
runtime prompt. Remove `omitted` from the final paste-ready prompt when brevity
matters, but keep selected IDs.

Use `scripts/select_components.py FEATURES.json` when task features are already
structured; its output is the canonical starting manifest. STATE transitions use
`scripts/state_transition.py`, FLOW may start from `scripts/build_workflow.py`,
and a host adapter can implement CONTAIN's policy contract using
`scripts/containment_check.py` as a deterministic reference oracle. Production
containment must still be bound to OS/runtime controls.

## Composition rules

- `CAL` without `VERIFY` is invalid.
- Recovery claims without `STATE` are invalid.
- L2/L3 with prompt-only safety and no `CONTAIN` is invalid.
- `FLOW` is not a synonym for sub-agents. Use code for stable branching and data
  plumbing; use sub-agents only for bounded judgment or context isolation.
- `FLOW` classifies every tool action as `read_only` or `side_effecting`.
  Parallel groups contain only independent reads. Side effects use an ordered,
  unique sequence; shared-state writes use a lease/fencing token or transaction.
- Persisted `STATE`, memory, connector credentials, and events bind to one
  `authority_context` (`tenant_id`, `channel_id`, `principal_id`, connector,
  memory namespace, and permission snapshot). A mismatch fails closed; the loop
  never broadens or silently migrates authority.
- A budget has a hard controller and may also have observed metrics. Never treat
  a model-estimated token or dollar count as a hard controller.
