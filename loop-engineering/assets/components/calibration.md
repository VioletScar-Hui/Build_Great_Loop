# CAL — drift detection

At a cadence justified by risk and detection lag, re-run human-owned golden cases
and randomly sample completed work through VERIFY. Store disagreements and pause
when the ratified threshold fails. The loop may not edit the golden set or lower
the threshold. Deterministic suites use their regression tests instead of CAL.

Acceptance: one seeded disagreement triggers pause and is attached to escalation.
