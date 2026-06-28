# Run Log — <loop name>

> Append-only. One line per run. This is what an operator reads to judge the loop's
> health at a glance and to catch runaway cost or thrash early. Never rewrite past
> lines.

Format:
```
[ISO timestamp] level=L1 | result=<reported|proposed|acted|escalated|blocked> | cost=<tokens/$> | summary=<one line> | next=<…>
```

Examples:
```
[2026-06-16T08:00Z] level=L1 | result=reported | cost=4.1k | summary=3 CI failures, 2 stale PRs, 1 P0 issue | next=human review
[2026-06-16T20:00Z] level=L1 | result=escalated | cost=5.3k | summary=PR #482 touches auth — human gate | next=await approval
[2026-06-17T08:00Z] level=L2 | result=acted | cost=6.0k | summary=patched foo@2.1.3 (patch-only), tests green | next=monitor
```

End-of-day / on stop, append a summary line:
```
[ISO timestamp] DAY SUMMARY | runs=<n> | escalations=<n> | total_cost=<…> | budget_left=<…> | health=<ok|watch|over-budget>
```
