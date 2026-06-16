# Loop Eval: <task name>

## Sharpened success criteria  (what "done" means — feeds the loop prompt)
Each is verifiable (two people would agree on pass/fail) and grades the end state,
not the path:
- <criterion 1 — observable check>
- <criterion 2>

If quality is multidimensional, separate the axes:
- **Outcome:** <the goal state>
- **Constraint:** <e.g. within N steps / under $X>
- **Quality:** <rubric, scored separately>

## Reliability metric
- [ ] pass@k  (any one good result is enough) — k = <N>
- [ ] pass^k  (must succeed every time — for user-facing reliability) — k = <N>

## Eval cases
Mix positive ("should do X") and negative ("should NOT do X") cases. Each has a
reference solution proving it's solvable.

| # | Input / scenario | Expected (end state) | Should-trigger? | Grader |
|---|---|---|---|---|
| 1 | <input> | <what must be true> | yes | code: <exit 0 / regex / state check> |
| 2 | <input> | <what must be true> | yes | model: <rubric, scored 1–5, escape hatch="Unknown"> |
| 3 | <near-miss input> | <correct restrained behavior> | no | code: <check it did NOT do X> |

## How to run
- <command or harness to execute the cases, k times each>
- Record pass/fail per case; compute the chosen metric.
- **Read the transcripts**, not just the scores — confirm each failure "seems
  fair" (a real defect, not a brittle grader). Fix graders that reject valid
  solutions.

## Capability vs regression
- **Capability** (currently failing, climbing): <which cases>
- **Regression** (must stay ~100%): <which cases — graduate capability cases here
  once they saturate>
