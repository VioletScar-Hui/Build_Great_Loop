# Recurring Loop Patterns

Seven production-tested patterns for recurring agent loops (adapted from Cobus
Greyling's pattern registry). Pick by cadence, cost tolerance, and risk. Each lists
the **starting autonomy level** and its **specific safety gates** — the actions that
must hit a human gate or be blocked outright. Start every pattern at L1.

| Pattern | What it does | Cadence | Start level | Token cost | Must-gate (never auto) |
|---|---|---|---|---|---|
| **Daily Triage** | Prioritized morning scan of CI, issues, commits, chat → one ranked list | 1d–2h | L1 report | Low | n/a (report-only) |
| **Issue Triage** | Discover, dedupe, prioritize incoming issues into an actionable queue | 2h–1d | L1 propose | Low | security, P0/P1, ambiguous duplicates |
| **Changelog Drafter** | Draft categorized release notes for human review | 1d / on tag | L1 draft | Low | breaking changes, security, major features |
| **Post-Merge Cleanup** | Follow-up tech-debt cleanup after merges to main | 1d–6h | L1 off-peak | Low | anything beyond the named cleanup scope |
| **Dependency Sweeper** | Discover, apply, verify dependency + vulnerability updates | 6h–1d | L2 patch-only | Medium | major version bumps, high-severity CVEs, denylisted packages |
| **PR Babysitter** | Shepherd PRs through review, CI, rebase, merge | 5–15m | L1 watch | High | security/payments/auth code; cap max-fix attempts |
| **CI Sweeper** | React to failing CI with minimal fixes + escalation | 5–15m | L2 cautious | Very high | infra failures, security tests; early-exit required |

## How to choose

- **Just want signal, lowest risk/cost** → Daily Triage or Issue Triage (L1).
- **Reduce release toil** → Changelog Drafter, Post-Merge Cleanup (L1, low cost).
- **Keep dependencies healthy** → Dependency Sweeper (L2, patch-only first).
- **Speed up PR flow** → PR Babysitter (watch first; it's high-cost at 5–15m).
- **Keep main green** → CI Sweeper (very high cost — gate hard, early-exit).

## Cost is a first-class concern

Notice the cost column. A 5–15-minute cadence with sub-agents (PR Babysitter, CI
Sweeper) can burn a *lot* of tokens fast. For those, set both a per-run and a
per-day budget, and prefer a longer cadence until you trust the loop. See the budget
section in `operating-safety.md`.

## Every pattern needs the same spine

Whichever you pick, it still needs what every loop needs: externalized `STATE.md` +
run-log, a maker/checker split (implementer + verifier sub-agents), a human gate on
the "must-gate" actions above, and a kill switch. The pattern decides *what* runs on
a cadence; `operating-safety.md` decides *how to run it without getting hurt*.
