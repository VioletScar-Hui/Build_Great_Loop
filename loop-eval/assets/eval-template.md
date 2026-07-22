# Loop Eval: <task name>

## System under test
- **Harness hash:** <sha256>
- **Tool-interface hash:** <sha256 or `none`>
- **Controller ID:** <versioned identifier or `none`>
- **Permission-profile hash:** <sha256>
- **Model-policy hash:** <sha256>
- **Language:** <deployment language code>

When capability depends on the control surface, run the same end-state case
against the relevant no-tool/read-only/constrained/high-level-controller variants.
Changing any identity above makes an old comparison `STALE`.

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

## Multilingual parity (when the product supports multiple languages)
- Pair each deployment-critical case across languages.
- Keep invariant IDs identical for autonomy, human gate, authority, stop, and
  verification decisions; do not require literal wording equality.
- Record cross-language disagreement as a regression, not translation noise.

## Calibration protocol (quality-fuzzy loops only; deterministic loops: state "test suite is the calibration" and skip)
- **Golden set:** `./loop-docs/golden.json` · K = <≥10 or 2% of volume> items,
  human-ratified expected outputs, diverse incl. hard cases. Human-owned.
- **Cadence:** every <N> increments (<default 25 or 10% of total, whichever
  smaller> — reason: <sizing rationale>).
- **Calibration increment:** re-process <k> golden items fresh + VERIFIER
  re-checks <k> random completed items.
- **Drift threshold & action:** agreement < <X>% (from the ratified 抽检一致
  standard) → pause auto-continue, log `CALIBRATION FAILED`, human gate with the
  disagreeing cases. Never loosen the threshold to pass.
