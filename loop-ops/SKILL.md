---
name: loop-ops
description: >-
  Operate an existing or intent-settled long-running, recurring, or unattended
  agent loop SAFELY — the
  scheduling, cost, safety, and rollout layer around a loop. Use this WHENEVER the
  user wants to RUN/SCHEDULE/OPERATE an agent loop over time rather than author its
  prompt: "run this agent every day / on every PR / nightly / on a cron", "set up
  an autonomous agent that keeps running", "babysit my PRs", "auto-triage issues",
  "sweep CI failures", "draft release notes automatically", "how do I run my loop
  unattended without it doing damage", or any question about an agent loop's
  cadence, autonomy level, token/cost budget, safety gates, denylist, human
  escalation, multi-loop coordination, kill switch, or operational readiness.
  If the per-run goal, success, safety, or budget is unsettled, loop-spec owns the
  request first. For a compound build-and-schedule request, loop-ops is lead and
  calls loop-engineering once for the per-run prompt.
  Produces an operating plan (pattern + cadence + autonomy level + budget + safety
  gates + schedule command + STATE/run-log scaffolding). Pairs with
  loop-engineering, which authors the per-run prompt this operates.
metadata:
  version: 3.1.0
---

# Loop Ops

There are two halves to loop engineering. **loop-engineering** writes the *prompt*
a single run executes. **loop-ops** (this skill) wraps that prompt into a
**recurring, often unattended operation** and makes it safe to leave running.

That power cuts both ways: a recurring loop **amplifies judgment — good and bad**.
So this skill is mostly about *restraint*: start small, gate the risky stuff, cap
the cost, and keep a human able to read what shipped.

Your job when this skill triggers: produce an **operating plan** for the loop —
pattern, cadence, autonomy level, budget, safety gates, the schedule command, and
the state/run-log files. It's the plan, not the running system: scaffold it and
hand it over; only actually schedule/launch it if the user explicitly asks.

> Respond and write the plan in **the user's language**; reasoning in English.

## The building blocks of a recurring loop

A loop that runs unattended is assembled from six primitives (Cobus Greyling's
"five building blocks + memory"):

1. **Automation / scheduling** — what fires it, and how often (cron, `/loop 1d …`,
   GitHub Actions, a watcher).
2. **Worktrees / isolation** — a safe, parallel place to work so a bad run can't
   corrupt the main branch or other loops.
3. **Skills** — the persistent project knowledge each run loads.
4. **Plugins & connectors (MCP)** — how it reaches your real tools (git, tickets,
   CI), and at what scope.
5. **Sub-agents** — the **maker/checker split**: an implementer does the work, a
   separate verifier checks it.
6. **Memory / state** — the durable spine (a `STATE.md` + a run-log) that lives
   *outside* any single run, so each run orients and the operator can audit.

For team/shared agents, bind tools, connector credentials, memory, state, and
events to one tenant/channel/principal authority context. Channel visibility does
not grant connector-data access, and another channel never inherits memory or a
side-effect token.

## The one rule that matters most: phased rollout (L1 → L2 → L3)

Never let a new loop act unattended on day one. Earn it in stages:

- **L1 — report-only.** It observes and *proposes*; it changes nothing. You read
  its output and judge whether you'd have done the same. Every loop starts here.
- **L2 — assisted.** It may make *narrow, reversible* changes behind safety gates
  (e.g. patch-only dependency bumps, draft PRs), still with a human gate on
  anything risky.
- **L3 — unattended.** It acts on its own for the allowlisted, low-risk slice —
  only after L1/L2 have shown it behaves.

State the level in the plan, and **default new loops to L1**. Graduating a level is
a deliberate decision, not a default.

## Workflow for an operating plan

1. **Pick a pattern.** Map the goal to a known recurring pattern (PR babysitter,
   daily triage, CI sweeper, dependency sweeper, changelog drafter, post-merge
   cleanup, issue triage). See `references/recurring-patterns.md` — each gives a
   cadence, a starting autonomy level, a cost band, and its specific safety gates.
2. **Set the autonomy level** — start L1 unless there's a reason not to.
3. **Set the budget controller.** Use an external scheduler/quota ledger to
   atomically reserve per-run/per-day capacity before dispatch and expensive
   increments, plus a persistent max-attempts cap. Token/$ values are hard caps
   only when the runtime meter can stop execution; otherwise report them as
   observed metrics.
4. **Define the safety gates.** A denylist (paths/actions it must never touch), a
   human gate for risky/irreversible/ambiguous actions, auto-merge rules, and MCP
   scopes. For L2/L3, map each rule to environment enforcement: credentials,
   sandbox/network policy, branch protection, scheduler pause, and active
   cancellation. See `references/operating-safety.md`.
5. **Choose cadence + scheduler** only after detecting what the user's environment
   actually supports. Never invent a `/loop` command or scheduler syntax; provide
   a platform-specific command only when verified, otherwise give a portable
   schedule specification.
   Host-specific background sessions are adapters, not CORE. On verified Claude
   Code W29+, `/fork` is a separately managed background session and `/subtask`
   stays in-session; never emit either from stale assumptions.
6. **Scaffold control state and events.** Use machine-readable `control-state.json`
   for budget, gate, cancellation, and claims; append structured events to
   `run-events.jsonl`; derive the glanceable Markdown status rather than treating
   prose as the source of truth. Templates and schemas live in `assets/`.
7. **Get the per-run prompt** from **loop-engineering** (the thing that actually
   runs each tick), and make sure its stop conditions, human gate, and budget match
   this plan.
8. **Run the readiness check** in `references/operating-safety.md` before anything
   goes past L1.

## Output contract

Deliver a single operating plan using `assets/ops-plan-template.md`, filled in:
pattern, cadence + schedule command, autonomy level (with why), per-run and per-day
budget, safety gates (denylist / human gate / auto-merge / MCP scopes), the
  control-state/event-log scaffolding, enforcement owners, and a pointer to the
  per-run loop prompt. Add a
2–4 line note: which pattern, the key risks, and what must be true before promoting
L1 → L2 → L3.

## The quality bar

- Autonomy starts at **L1 (report-only)** unless the user explicitly overrides.
- There's an externally enforceable **cost ceiling** (per run and per day) and a
  kill switch that prevents launches and cancels active work.
- Risky / irreversible / ambiguous actions hit a durable, action-bound **human
  gate** with full context; the scheduler stays paused until a matching decision.
- A **denylist** names what the loop must never touch; MCP/tool scopes are minimal.
- Shared/team operation has an explicit authority context and a seeded
  cross-namespace memory/credential denial test.
- State + run-log are externalized so the operator can audit what shipped.
- If several loops touch the same repo, **multi-loop coordination** is addressed.
- A human can read the run-log in 30 seconds and know the loop's health.

## Reference files

- `references/recurring-patterns.md` — the 7 named recurring patterns + their gates.
- `references/operating-safety.md` — rollout levels, human gate, cost/budget,
  denylist, auto-merge, MCP scopes, multi-loop coordination, failure modes, kill
  switch, and the operational-readiness checklist.
- `assets/ops-plan-template.md` — the fill-in operating plan (the deliverable).
- `assets/control-state.example.json`, `assets/run-event.schema.json` — control
  state and append-only audit contract.
- `assets/STATE-template.md`, `assets/run-log-template.md` — human-readable views,
  not enforcement state.
- `scripts/quota_ledger.py` — cross-platform, single-host atomic reference
  controller; distributed schedulers must provide equivalent reservation
  semantics.

## Method note

The operating plan applies the suite's core principles: start with the simplest
safe deployment, keep tools narrowly scoped, externalize state, verify outcomes,
and increase autonomy only after observed evidence. For per-run prompt discipline,
see **loop-engineering**.
