# Operating & Safety

How to run a recurring/unattended loop without it hurting you. This is the doctrine
that turns a loop prompt into something you can leave running. Adapted from Cobus
Greyling's operating, safety, anti-patterns, failure-modes, and multi-loop docs.

**Contents:** 1. Phased rollout · 2. Human gate · 3. Cost & budget · 4. Denylist &
scopes · 5. Auto-merge gates · 6. Multi-loop coordination · 7. Failure modes ·
8. Kill switch · 9. Anti-patterns · 10. Readiness checklist

---

## 1. Phased rollout (L1 → L2 → L3)

The single most important safety control. New loops do not act unattended.

- **L1 — report-only.** Observes, proposes, changes nothing. You read its output and
  ask: *would I have done the same?* Run here for at least a week of real cadence.
- **L2 — assisted.** Narrow, **reversible** changes behind gates (draft PRs,
  patch-only bumps). A human still approves anything risky.
- **L3 — unattended.** Acts on its own for the **allowlisted, low-risk** slice only.

Promotion is earned, per slice, with evidence from the run-log — not a flag you flip
because it "seems fine." When in doubt, stay a level lower.

---

## 2. Human gate

A first-class checkpoint in the loop: when an action is **risky, irreversible, or
ambiguous**, the loop stops and hands off to a human **with full context** (what it
was doing, why, what it proposes, what it's unsure about) — it does not guess and
act. Define exactly what trips the gate (see each pattern's "must-gate" list), and
make the escalation legible enough that a human can decide in one read.

For recurring operation, prose is not a gate. Persist
`open → waiting_for_human → approved|rejected|expired → consumed`, keyed by a
unique gate ID and digest of the exact action, inputs, scope, and expiry. The
scheduler skips normal runs while waiting. Approval can be consumed once only by
the matching action.

---

## 3. Cost & budget

Recurring loops are where spend silently explodes (short cadence × sub-agents ×
long runs). Treat cost as a stop condition, not an afterthought:

- An external scheduler/quota ledger atomically reserves a **per-run** and
  **per-day** ceiling before dispatch and before costly increments.
- Prefer enforceable increments, tool calls, or wall time. Tokens/$ are hard caps
  only when an external meter can stop execution; otherwise they are observations.
- A **max-attempts** cap on any single fix (e.g. PR Babysitter retries).
- A **run-log** that records cost per run, so you can see the trend before the bill.
- Prefer a longer cadence until the loop has proven its value at L1.

---

## 4. Denylist & minimal scopes

- **Denylist:** paths, files, and actions the loop must *never* touch (secrets,
  prod config, billing, auth, migrations). Deny by default; allowlist the safe slice.
- **MCP / tool scopes:** grant the minimum the pattern needs. A triage loop is
  read-only; it doesn't get write/merge tokens. Scope creep is how a "harmless"
  loop does damage.
- For L2/L3, implement these boundaries outside the model with least-privilege
  credentials, filesystem/network sandboxing, and protected environments. Prompt
  text is an explanation of policy, not the enforcement layer.

---

## 5. Auto-merge gates

If the loop can merge/ship, every auto-action passes gates first: required checks
green, no changes to denylisted paths, within the allowlisted slice, under the
attempt cap. Anything outside → PR for human review, never an autonomous merge.

---

## 6. Multi-loop coordination

When several loops touch the same repo they collide: two loops grabbing the same
issue, fighting over a branch, or stacking conflicting commits. Coordinate with
isolated workspaces, non-overlapping scopes, and staggered cadences. If two loops
can act on the same artifact, use atomic compare-and-swap leasing with a fencing
token validated by every side effect. A Markdown claim is only an operator view.

---

## 7. Failure modes (watch for these)

- **Runaway cost** — short cadence + sub-agents with no budget → stop with a budget.
- **Silent breakage** — unattended loop ships a regression nobody saw → verifier
  sub-agent + read the run-log.
- **Thrash / flapping** — loop "fixes" then "unfixes" the same thing → attempt cap +
  state that records what was tried.
- **Stale state** — loop acts on an out-of-date snapshot → re-orient from live
  sources each run, not from memory.
- **Scope drift** — loop slowly does more than intended → denylist + tight scopes.
- **Comprehension debt** — it ships faster than anyone reads → keep cadence/volume
  matched to how much output a human will actually review.

---

## 8. Kill switch

The kill switch must both prevent launches and cancel active runs. Revoke or fence
the credential used for side effects, check cancellation before each ACT/external
effect/merge boundary, and fail closed if L2/L3 cannot read the switch. Record
cancellation acknowledgement with bounded heartbeat latency.

---

## 9. Anti-patterns

- Going straight to L3 ("it worked in testing").
- No budget; discovering cost from the invoice.
- One loop with broad write scopes "to keep it simple."
- Auto-merging because review is slow.
- Nobody reads the run-log, so failures compound unseen.
- Adding loops faster than you can operate them.

---

## 10. Operational readiness checklist

Before promoting past L1, every box should be checked:

- [ ] **Autonomy** starts at L1; promotion criteria per slice are written down.
- [ ] **Budget**: external atomic reservation for per-run/day ceilings + persistent attempts.
- [ ] **Human gate**: durable pause + action digest + single-use matching approval.
- [ ] **Denylist**: each rule has tested environment-level enforcement evidence.
- [ ] **Auto-merge** (if any) passes required checks + scope + attempt gates.
- [ ] **State + events** are machine-readable; operator views retain event IDs.
- [ ] **Multi-loop**: no collisions with other loops (worktrees / claims / scopes).
- [ ] **Kill switch**: launch prevention and active cancellation both tested.
- [ ] **Verifier**: a maker/checker split, not the implementer grading itself.
- [ ] **Comprehension**: volume/cadence is within what a human will actually read.
