# FLOW — executable orchestration

When branching, fan-out, retries, or intermediate data are stable and replayable,
put that control flow in a small executable workflow. It owns the queue and
intermediate artifacts; the agent receives one bounded judgment task and returns
a structured result. Validate inputs/outputs and keep summaries out of the main
context until reduction.

Acceptance: replaying the workflow from persisted inputs produces the same work
graph and does not require reconstructing it from conversation history.
