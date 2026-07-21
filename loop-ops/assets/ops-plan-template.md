# Loop Operating Plan: <loop name>

> The plan for running this loop on a cadence, safely. The per-run prompt itself
> comes from the loop-engineering skill (linked below). Only a human promotes the
> autonomy level.

## Goal & pattern
- **Goal:** <what the recurring loop accomplishes>
- **Pattern:** <daily-triage | issue-triage | changelog-drafter | post-merge-cleanup |
  dependency-sweeper | pr-babysitter | ci-sweeper | custom>

## Autonomy level
- **Current:** **L1 — report-only** (default for a new loop)
- **Promote to L2 when:** <evidence from the run-log that proves it's safe>
- **Promote to L3 when:** <…, and only for this allowlisted slice: …>

## Cadence & schedule
- **Cadence:** <e.g. 1d / 2h / 5–15m>
- **Scheduler kind / timezone / misfire policy:** <verified capabilities>
- **Verified command:** <exact command only after capability detection; otherwise TBD>

## Budget (cost is a stop condition)
- **Hard controller:** <scheduler/quota store and atomic reservation method>
- **Per run / per day:** <enforced increments, tool calls, wall time, or metered cost>
- **Observed only:** <tokens/$ when no stopping meter exists>
- **Max-attempts per item:** <N>

## Safety gates
- **Human gate (never auto):** <risky/irreversible/ambiguous actions for this pattern>
- **Denylist (never touch):** <paths / actions / packages>
- **Tool / MCP scopes:** <minimal set; read-only unless L2+>
- **Auto-merge rule (if any):** <required checks + scope + attempt gates, else PR>
- **Enforcement evidence:** <credential/sandbox/branch-policy checks for each rule>
- **Kill switch:** <prevent launches + cancel active run + revoke side-effect token>

## State & audit
- **Control state:** `control-state.json` (budget/gate/cancellation/claim authority)
- **Events:** `run-events.jsonl` (append-only; see run-event.schema.json)
- **Views:** `STATE.md`, `run-log.md` generated/updated from machine state
- **Verification mode:** <deterministic_check | independent_context | human_review>
- **Independent verifier for L2/L3 mutation:** immutable criteria, own evidence,
  read-only access to candidate/tests/verdict history; fail closed on no verdict

## Per-run prompt
- Authored with **loop-engineering**. Confirm its stop conditions, human gate, and
  budget match this plan. Link/path: <…>

## Multi-loop
- Other loops on this repo: <list / none>. If scopes overlap, use an atomic lease
  with owner/run ID, expiry, and fencing token; worktrees/cadence are supplementary.

---
**Operator note:** pattern = <…>; top risks = <…>; promote past L1 only after <…>.
Run the readiness checklist in operating-safety.md before going beyond report-only.
