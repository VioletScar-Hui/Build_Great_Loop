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
- **Scheduler / command:** <tool-specific, e.g. `/loop 1d Run <prompt>. Update STATE.md.`
  · Claude Code schedule/cron · GitHub Actions workflow>

## Budget (cost is a stop condition)
- **Per run:** <max tokens / $ / turns>
- **Per day:** <ceiling>
- **Max-attempts per item:** <N>

## Safety gates
- **Human gate (never auto):** <risky/irreversible/ambiguous actions for this pattern>
- **Denylist (never touch):** <paths / actions / packages>
- **Tool / MCP scopes:** <minimal set; read-only unless L2+>
- **Auto-merge rule (if any):** <required checks + scope + attempt gates, else PR>
- **Kill switch:** <the one step to stop all runs>

## State & audit
- **State file:** `STATE.md` (durable spine — see STATE-template.md)
- **Run-log:** `run-log.md` (one line per run incl. cost — see run-log-template.md)
- **Verifier:** maker/checker split — implementer + a separate verifier sub-agent

## Per-run prompt
- Authored with **loop-engineering**. Confirm its stop conditions, human gate, and
  budget match this plan. Link/path: <…>

## Multi-loop
- Other loops on this repo: <list / none>. Collision avoidance: <worktrees / claims
  in STATE.md / non-overlapping scopes / staggered cadence>

---
**Operator note:** pattern = <…>; top risks = <…>; promote past L1 only after <…>.
Run the readiness checklist in operating-safety.md before going beyond report-only.
