# Loop Prompt Checklist

The audit used both for self-review (before delivering a loop prompt) and by the
**loop-review** skill (to grade an existing one). Each item is a yes/no question
about the *prompt*, with the failure it catches. A top-tier loop prompt answers
"yes" to all of them.

Score by counting the gaps. Any **Critical** gap means the loop is not ready —
those are the items that cause runaway, drift, or fake success.

---

## A0. Interview & delivery gates (for loops built with this skill group)
- [ ] **(Critical)** Was the spec **interview-ratified** — clarifications answered
      by the user (not assumed), standards/goal-tree signed off? *(Catches: loops
      built on guessed requirements.)*
- [ ] **(Critical)** Were the stop conditions given a **final user confirmation**
      immediately before delivery? *(Catches: a wrong "done" running unattended.)*
- [ ] Does the harness build in **sub-agent orchestration** (decomposer /
      plan-reviewer / verifier / doc-writer@haiku) and scaffold
      `./loop-docs/` (SPEC/STANDARDS/GOALS/PLAN)? *(Catches: monologue prompts
      that re-derive plans and standards every iteration.)*
- [ ] Is there a **plan→review→revise cycle** (≤2 rounds) with default
      **auto-continue** for interview-ratified loops? *(Catches: per-round
      approval stalls, and unreviewed plans.)*
- [ ] Is there a **shakedown protocol** — supervised first increments, a
      deliberate mid-increment kill + clean-resume check, verifier-fired check —
      gating auto-continue? *(Catches: crash-safety that was never tested.)*
- [ ] Is the path **proportionate** — lite (flat harness) only when all four lite
      criteria held AND the user confirmed; full ceremony otherwise? Lite never
      waives state/cap/kill-test/stop-confirmation. *(Catches: over-process that
      gets bypassed, and lite-as-escape-hatch.)*
- [ ] For quality-fuzzy loops, is there a **calibration protocol** (golden set,
      cadence with sizing reason, drift threshold → pause + escalate)? For
      deterministic loops, is calibration **explicitly waived with the reason**
      (the test suite is the calibration)? *(Catches: judgment drift across
      hundreds of increments — and cargo-culted golden sets.)*

## A. Goal & success criteria
- [ ] **(Critical)** Are success criteria explicit and **verifiable** — two people
      would agree whether they're met? *(Catches: endless wandering, fake success.)*
- [ ] Are they a checklist of concrete checks rather than one vague goal?
- [ ] Is each criterion **machine-checkable** (a command/observation confirms it),
      not something only a human can eyeball? *(Catches: unverifiable "done".)*
- [ ] Does it grade the **end state**, not a hardcoded sequence of steps?
      *(Catches: brittleness, punishing valid approaches.)*

## B. Stop conditions
- [ ] **(Critical)** Is there a **hard cap** (max iterations / time / budget) so it
      can't run forever? *(Catches: runaway loops.)*
- [ ] Is the cap (and the increment size) **chosen on purpose**, with stated
      reasoning — not an arbitrary number? *(Catches: caps too big to be safe, too
      small to progress.)*
- [ ] Is "done" defined as *verified* criteria met?
- [ ] Is "blocked/stuck" defined, with what to do (stop + report, or escalate)?
      *(Catches: thrashing.)*
- [ ] Does the cap include a **cost/token budget**, not just an iteration count?
      *(Catches: runaway spend.)*
- [ ] Is there a **human gate** — risky / irreversible / ambiguous actions stop and
      escalate *with full context*? *(Catches: unattended damage.)*
- [ ] Is an **autonomy level** stated (L1 report-only / L2 assisted / L3 unattended),
      starting at L1 for anything new? *(Catches: going unattended too soon.)*

## C. The loop skeleton
- [ ] **(Critical)** Is it **one increment per iteration**? *(Catches: over-ambition
      / one-shotting.)*
- [ ] Are the five beats present — Orient, Plan, Act, Verify, Record?
- [ ] Does each iteration **Orient first** (read state before acting)?

## D. State & memory across resets
- [ ] **(Critical)** Is progress **externalized to files** so it survives a context
      reset? *(Catches: total progress loss on reset.)*
- [ ] **(Critical)** Is resume **crash-safe and idempotent** — claim-before-act /
      atomic record, so a mid-iteration crash never double-processes or corrupts
      state? *(Catches: duplicated work, corrupted state on restart.)*
- [ ] Are the state files named, with a format (progress file + task list)?
- [ ] Is the goal/spec **protected** (only a human edits it; agent may change only a
      status field)? *(Catches: silent goal drift.)*

## E. Context discipline
- [ ] Is there guidance to retrieve **just-in-time** rather than preload everything?
- [ ] Is there a plan for a growing window (compaction / clear stale tool results /
      notes)?
- [ ] Are sub-agents used for deep/parallel work where appropriate (return summaries,
      not full traces)?

## F. Tools (if the loop uses tools)
- [ ] Is the tool set **minimal and consolidated** (no redundant/overlapping tools)?
- [ ] Do tool returns look **high-signal and token-efficient**?
- [ ] Do error paths **teach recovery** (the error models the fix)?

## G. Verification & guardrails
- [ ] **(Critical)** Is self-verification **mandatory and real** — exercising the
      result like a user, not just "looks right"? *(Catches: false completion.)*
- [ ] Does it verify **before** recording and moving on?
- [ ] **(Critical)** Are the anti-patterns named — no faking, **no editing/removing
      tests or criteria** to pass? *(Catches: reward hacking.)*

## H. Output / form
- [ ] Could a **fresh agent start from this prompt with zero extra context**?
- [ ] Are sections clearly delineated (XML tags / Markdown headers)?
- [ ] Is the system prompt at the **right altitude** — specific enough to guide,
      not so rigid it's brittle?
- [ ] Does every instruction **earn its place** (nothing speculative or redundant)?
- [ ] Are instructions **explained** (the *why*), so the model can reason past the
      letter of them?

## I. Operability (for anything long-running / unattended)
- [ ] Does it give the operator a **glanceable status or end-of-run summary** (done
      / in-progress / blocked / remaining)? *(Catches: silent unattended failure.)*
- [ ] On "blocked", does it leave a **clear, human-readable handoff** of what's
      needed? *(Catches: a stuck loop nobody can unstick.)*
- [ ] Is the output kept **reviewable** — volume/cadence within what a human will
      actually read (comprehension debt)? *(Catches: shipping faster than anyone
      checks.)*
- [ ] For recurring / unattended runs, are the operating controls covered (denylist,
      kill switch, minimal scopes)? *(If so, design them with the **loop-ops** skill.)*

---

## Scoring

- **Critical gaps (count):** any > 0 → not ready. List them first.
- **Total gaps (count):** overall health. 0 = top-tier; 1–3 = solid, minor polish;
  4–8 = needs work; 9+ = rebuild around the seven dimensions.

For a review, report: the critical gaps (with the exact missing thing and a one-line
fix), then the non-critical gaps ranked by impact, then what the prompt already does
well (so the user knows what not to touch).
