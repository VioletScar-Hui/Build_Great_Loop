# Loop State — <loop name>

> Durable spine that lives outside any single run. Each run reads this first
> (Orient) and updates it last (Record). Keep it scannable: live metrics + dated
> snapshots, not prose. Only the loop edits the status fields; a human owns the goal.

**Last run:** <ISO 8601 timestamp> · by <workflow/cadence> · autonomy **L1**

## High priority
<Blocking items + thresholds with live values, e.g.>
- Keep CI green: currently **failing on `build`** (since 2026-06-16T09:00Z) — escalated
- Keep open P0 issues at 0: currently **1** (#482)

## Watch list
<Emerging items the loop is tracking but not acting on yet>
- Dependency `foo@2.x` has a minor bump available — propose at next run

## Claims (multi-loop coordination)
<Which item this loop currently owns, so other loops don't grab it>
- owns: <issue/branch/none> until <when>

## Recent noise (ignored this run)
<Low-signal items explicitly deferred, so the next run doesn't re-surface them>
- <none this run>

---
Run history: see `run-log.md`. Process details: see the operating plan.
