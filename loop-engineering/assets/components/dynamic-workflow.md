# FLOW — executable orchestration

When branching, fan-out, retries, or intermediate data are stable and replayable,
put that control flow in a small executable workflow. It owns the queue and
intermediate artifacts; the agent receives one bounded judgment task and returns
a structured result. Validate inputs/outputs and keep summaries out of the main
context until reduction.

Before dispatch, label every tool action `read_only` or `side_effecting` and list
the resources it touches. Only independent reads may share a `parallel_group`.
Mutations, messages, quota reservations, and shared-state writes use a unique
ordered `sequence`; enforce leases/fencing tokens or transactions where multiple
workers could reach the same resource. Reduction waits for required effects to
commit and re-orients before any read-after-write step.

Acceptance: replaying the workflow from persisted inputs produces the same work
graph and does not require reconstructing it from conversation history. A seeded
test demonstrates overlapping independent reads and serialized side effects.
