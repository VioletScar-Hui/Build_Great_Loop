---
name: loop-eval
description: >-
  Design success criteria and a small eval set for an agentic loop — so the loop
  knows when it's done, and so YOU can measure whether the loop is any good. Use
  this whenever the user asks how to know if their agent/loop is working, how to
  define or sharpen success criteria, how to write evals/tests/graders for an
  agent, how to measure agent reliability, or wants pass/fail checks for a
  long-running task. Also use as the verification step when building a loop with
  loop-engineering. Covers verifiable criteria, code-based vs model-based graders,
  reliability metrics (pass@k vs pass^k), and balanced positive/negative cases.
---

# Loop Eval

Two different jobs that people conflate:

- **Success criteria** tell the *loop* when to stop (the agent self-checks against
  them every iteration). These live inside the loop prompt.
- **Evals** tell *you* whether the loop is reliable across many runs and inputs.
  These run outside the loop, repeatedly.

Both matter. A loop with good self-checks but no external evals can be confidently
wrong; a great eval suite on a loop with vague criteria measures noise.

> Write criteria and evals in **the user's language**; reasoning in English.

## Part 1 — Sharpen the success criteria

The core test (from agent-eval practice): **a good criterion is one where two
domain experts would independently reach the same pass/fail verdict.** If they'd
disagree, it's not a criterion yet.

- Turn vague goals into observable checks. "Summaries are good" → "summary is
  ≤ 150 words AND names the 3 required fields AND a rubric-grader scores
  faithfulness ≥ 4/5."
- **Grade the end state, not the path.** Don't require a specific tool sequence —
  that punishes valid alternative approaches and makes brittle criteria. Specify
  *what must be true when done*, not *how to get there*.
- Make success **multidimensional** when needed: outcome (the goal state) +
  constraints (finished within N steps / budget) + quality (a rubric).

## Part 2 — Build a small eval set

You don't need hundreds of cases to start. **20–50 tasks drawn from real failures
is a great start**; for a brand-new loop, even 5–10 well-chosen cases give signal,
because early changes have large effects.

Where cases come from:
1. Manual checks you'd run before trusting the loop → automate them.
2. Real failures you've already seen → turn each into a case.
3. **Balance positive and negative cases.** Test both when the behavior *should*
   happen and when it *shouldn't* (e.g. an agent that should search sometimes but
   not over-search). One-sided sets teach one-sided behavior.
4. For each case, have a **reference solution** proving it's solvable — if you can't
   solve your own task, the task is broken, not the agent.

## Part 3 — Choose graders

| Grader | Best for | Watch out for |
|---|---|---|
| **Code-based** (exit codes, regex/fuzzy match, state inspection, tool-call checks) | Deterministic outcomes — fast, cheap, reproducible | Brittle to valid variations; rejecting correct alternatives |
| **Model-based** (LLM-as-judge against a rubric) | Nuance, quality, tone | Must be calibrated to humans; grade each dimension in a separate call; give it an "Unknown" escape hatch |
| **Human** | Gold standard; calibrating the model grader | Slow; use to spot-check, not every run |

Prefer code-based where the outcome is objective; reserve model-based for genuine
nuance. **"Failures should seem fair"** — when a case fails, you should agree the
failure was deserved; if the grader rejected a valid solution, fix the grader, not
the loop.

## Part 4 — Reliability metric

Pick based on what the product needs:
- **pass@k** — succeeds at least once in k tries. Use when any one good result is
  enough (you'll pick the best).
- **pass^k** — succeeds *every* one of k tries. Use for anything user-facing where
  consistency matters. These diverge sharply as k grows, so choose deliberately.

For a long-running loop, **pass^k-style consistency is usually what you want** — it
has to work reliably, not just occasionally.

## Part 5 — Use evals in the improvement loop

- **Read the transcripts, not just the scores.** You won't know if a grader is
  working until you read why cases passed or failed. Failures should be
  understandable and fair.
- **Capability evals** start low and climb (measure progress on hard cases);
  **regression evals** stay ~100% and catch backsliding. When a capability eval
  saturates, graduate it into the regression set.
- Guard against eval-hacking: design graders so the loop must genuinely solve the
  task, not exploit a loophole (over-rigid string match, ambiguous spec).

## Part 6 — Wire the evals INTO the loop: golden set + calibration protocol

Per-increment verification catches broken increments; it cannot catch **drift** —
the loop's own judgment sliding across hundreds of increments (labeling criteria
loosening, research claims thinning, summaries bloating). For **quality-fuzzy
loops** (verification is judgment-based rather than a deterministic command),
design a calibration protocol the harness will run mid-loop:

- **Golden set**: K items with human-ratified expected outputs, built BEFORE the
  run (K ≥ 10, or 2% of total volume, whichever is larger; sample for diversity,
  include the hard cases). Store at `./loop-docs/golden.json` — human-owned, the
  loop never edits it.
- **Cadence**: a calibration increment every N increments (default: every 25, or
  10% of total, whichever is smaller — frequent enough that drift can't poison a
  large batch, cheap enough to stay under ~5% overhead; state the sizing reason).
- **The calibration increment**: re-process k golden items fresh + have the
  VERIFIER re-check k random already-completed items. Compare against expected.
- **Drift threshold**: agreement < X% (take X from the ratified 抽检一致 standard)
  → **pause auto-continue**, log `CALIBRATION FAILED`, escalate via the human gate
  with the disagreeing cases attached. Never continue past a failed calibration;
  never loosen the threshold to pass — that is reward hacking on yourself.
- **Deterministic loops** (a test suite proves each increment): the suite IS the
  calibration — say so explicitly and skip the protocol rather than cargo-culting
  golden sets where `npm test` already answers the question.

Handoff: loop-spec's interview identifies the family; you build the golden set
with the user during intake; **loop-engineering** embeds the protocol in the
harness.

## Output

Write an `EVAL.md` using `assets/eval-template.md`: the sharpened success criteria,
the case set (with grader type per case), the chosen metric, how to run it — and
for quality-fuzzy loops, the **calibration protocol** (golden set path & size,
cadence with sizing reason, drift threshold & action). Feed the sharpened criteria
back into the loop prompt (via **loop-engineering**) so the agent's self-check
matches what you measure.
