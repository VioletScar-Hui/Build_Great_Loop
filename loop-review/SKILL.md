---
name: loop-review
description: >-
  Audit and harden an EXISTING agentic-loop prompt or harness against
  loop-engineering best practices. Use this whenever the user has an agent/loop
  iterative/autonomous prompt and wants it reviewed, critiqued, scored, or made
  more reliable — or when
  they describe loop misbehavior and want to know why: "my agent runs forever /
  never stops", "it quits too early", "it says it's done but it isn't", "it keeps
  redoing the same thing", "it forgets progress after a restart", "it edits the
  tests to pass", "review/improve my iterative agent prompt", "why is my loop flaky". It
  produces a scored report — critical gaps first, each with a concrete fix — and
  can rewrite the prompt to close them. Exclude one-shot chatbot/system prompts.
  If symptoms belong to a completed run or run artifacts, loop-retro diagnoses
  first. Whole-harness audits are led here even when criteria are the suspected
  defect. This skill also owns maintenance audits of this six-skill router.
metadata:
  version: 4.1.0
---

# Loop Review

Audit an existing loop prompt or harness and tell the user exactly where it will
break and how to fix it. The job is diagnosis + concrete fixes, not a vague "looks
good." Most loop pathologies map to a specific missing piece — find it.

> Write the report in **the user's language**; reasoning in English.

## Inputs

Get the artifact to review: the loop prompt / system prompt / harness (paste, file
path, or repo). If the user describes a *symptom* instead, the symptom map below
points straight at the likely gap. If they have a SPEC or success criteria, read
those too — a loop that doesn't match its spec is itself a finding.

## How to audit

Run the artifact against the shared checklist in
`../loop-engineering/references/checklist.md` (the same seven dimensions
`loop-engineering` builds to). For each item, decide pass / gap / N/A, and for
each gap note the **exact missing thing** and a **one-line fix**. Mark conditional
items N/A with evidence; do not penalize a one-session L1 loop for machinery it
does not need. Read
`../loop-engineering/references/principles.md` if you need the "why" behind a
dimension.

Also parse its component manifest against
`../loop-engineering/references/component-catalog.md`: flag a missing triggered
component, an included component with no trigger, a selected component with no
reachable runtime clause or emitted evidence (dead), an unmet dependency, or an
acceptance check that is only promised rather than exercised. Audit `PROFILE`,
`RULES`, `DEVIATIONS`, and `EXPLAIN` explicitly when present or triggered, using
their direct leaves in `../loop-engineering/assets/components/`. Missing
structured evidence makes the applicable acceptance check a gap, not a pass.
For L2/L3, prompt-only safety is a critical gap unless environment enforcement
evidence is supplied.

When FLOW, shared/team memory, provider controls, or host session commands are
present, also audit `../loop-engineering/references/runtime-adapters.md` and the
runtime contract. Flag parallel side effects, missing/changed authority context,
unhashed control interfaces, obsolete assistant prefill, stale model capability
snapshots, and unverified `/fork` or `/subtask` semantics. For shared/team L2/L3,
cross-namespace memory or credential access is a critical gap.

Be a tough but fair reviewer:
- **Critical gaps first.** The items that cause runaway, drift, or fake success
  (no hard cap, no verifiable criteria, no externalized state, no real
  verification, no anti-reward-hacking guardrail). Any one of these means "not
  ready."
- **Then non-critical gaps, ranked by impact.** Don't bury the big fix under nits.
- **Then what it already does well** — so the user knows what *not* to touch
  (surgical changes only).
- **Quote the prompt** when pointing at a problem; concrete beats abstract.

## Symptom → likely gap

Use this to go straight to the cause when the user reports a behavior:

| Symptom | Likely missing piece | Dimension |
|---|---|---|
| Runs forever / never stops | No hard cap; no verifiable "done" | B, A |
| Quits too early / gives up | "Blocked" not defined, or criteria too vague to confirm done | B, A |
| "Done" but it isn't | Verification not mandatory/real; criteria not verifiable | G, A |
| Repeats the same failed action | No "stuck" detection; no hypothesis/progress log | B, D |
| Forgets progress after restart | State not externalized to files | D |
| Edits tests / weakens checks to pass | No anti-reward-hacking guardrail; goal not protected | G, D |
| Tries to do everything at once | No "one increment per iteration" rule | C |
| Slows down / loses the thread over time | No context discipline / compaction / notes | E |
| Picks the wrong next thing | No Orient step / no prioritized task list | C, D |
| Parallel workers overwrite or double-send | Side effects placed in a parallel group | F, D |
| Another channel sees prior memory | State/connector not bound to authority context | D, I |
| Same model scores change after tool swap | Control interface omitted from eval identity | G, F |

## Output

A `LOOP-REVIEW.md` (or inline report) with:
1. **Verdict** — ready / not ready, and the headline reason.
2. **Score** — critical gap count + total gap count (from the checklist).
3. **Critical gaps** — each: what's missing, why it bites, the one-line fix.
4. **Other gaps** — ranked by impact.
5. **Strengths** — what's already good; leave it alone.

Then offer to **apply the fixes**: rewrite the prompt closing the gaps (using the
`loop-engineering` template), changing only what the findings require — don't
gold-plate a prompt that's mostly fine. When applying fixes, snapshot the original,
change one conceptual component at a time, and compare representative runs so you
can tell which change helped. Do not replace the whole harness merely to make it
look more systematic.
