---
name: loop-retro
description: >-
  Post-run retrospective for an agent loop — close the improvement flywheel.
  Reads the ACTUAL run artifacts (progress log / run-log / state files / PLAN
  history / loop-docs) and produces: an evidence-cited diagnosis, concrete
  harness revision proposals, gotcha eval cases from real failures, and
  SPEC/STANDARDS revision proposals for human ratification. Trigger AFTER a loop
  has run: "loop 跑完了帮我复盘", "看看运行记录哪里出问题", "这个循环为什么
  thrash / 超预算了", "分析一下 run log", "post-mortem my loop", "did my loop
  actually do a good job". Not for auditing a loop prompt BEFORE it runs
  (loop-review), operating/scheduling a loop (loop-ops), or building one
  (loop-spec / loop-engineering).
---

# Loop Retro — the improvement flywheel

A loop that runs and is never read back teaches you nothing. This skill turns one
real run into three upgrades: a **harder harness**, a **gotcha eval** that keeps
the failure from recurring unnoticed, and **sharper standards**. Run it after
every significant run — especially the bad ones, but not only the bad ones.

> Report in **the user's language**. Skill internals stay English.

## Iron law

**EVIDENCE ONLY. PROPOSE, DON'T EDIT. REAL FAILURES ONLY.**

- Every finding cites a concrete line from the artifacts — no vibes-based diagnosis.
- Ratified documents (SPEC/STANDARDS/GOALS) and the harness prompt are **never
  silently modified** — you produce proposals; the human ratifies.
- Gotcha eval cases record only failures that **actually happened** in this run.
  Never invent hypothetical failures — that's loop-eval's job, done before the run.

## Prerequisites

- [ ] Run artifacts exist and are readable: progress log / run-log, state files
  (task list / manifest), PLAN.md history if present. (Verify: list the loop's
  working directory.) If nothing was persisted, say so — that IS finding #1
  (the harness failed the state-externalization bar) — and stop there.
- [ ] The harness prompt itself (to propose revisions against).
- [ ] loop-docs (SPEC/STANDARDS/GOALS) if the loop was interview-ratified.

## Process

### Step 1 — Collect evidence

Inventory the artifacts, then extract the run's vitals (script the counting where
possible — read the whole log via commands, not by skimming the tail):

increments attempted/completed/failed · retries per item (max & distribution) ·
human-gate hits and outcomes · budget burned vs. cap · wall-clock · verifier
activity (how many verdicts, any failures caught?) · resume events (crashes, and
whether resume was clean) · **PLAN.md `## Deviations` entries** — each one is a
map-vs-territory gap caught mid-flight; a run with zero deviations logged and
visible surprises in the output means the protocol was skipped (itself a finding).

**Checkpoint**: a vitals table with numbers, each traceable to the log.

### Step 2 — Diagnose against the failure taxonomy

Walk the taxonomy; for each hit, cite the evidence line:

| Failure class | Signature in the log |
|---|---|
| Thrash | same item retried with the same error, no new information |
| Drift | quality/consistency degrades across increments (early vs. late samples differ) |
| Gate misfire | human gate fired on trivia (false positive) or missed a risky act (false negative) |
| Standard too loose/strict | verifier passed something a human would fail, or blocked reasonable work |
| Verifier rubber-stamping | 100% pass verdicts, near-zero verdict variance, or a pass on later-known-broken work |
| Resume failure | duplicate/missing items after a restart; state file corruption |
| Budget overrun | spend exceeded cap, or cap hit with disproportionate progress |
| Comprehension debt | output volume nobody read; status lines missing or useless |

**Also mine the non-failures** (this is not optional): cost per increment vs.
expectation, standards that never once failed (possibly too loose to matter),
gates never hit (possibly miscalibrated), increments that were trivially small
(cap too conservative).

### Step 3 — Produce the flywheel triad

1. **Harness revision proposals** — for each diagnosis, a concrete before→after
   edit to the harness prompt (quote the current line, give the replacement).
2. **Gotcha eval case(s)** — for each real failure, one runnable eval case in the
   manual format (`category: "gotcha"`, prompt reproducing the situation,
   assertions phrased as "没有重复 <the observed failure>"). Append to the
   project's `loop-docs/gotchas.json` (create if absent).
3. **SPEC/STANDARDS revision proposals** — marked explicitly **"需人工签核"**;
   listed separately, never applied.

### Step 3.5 — Sedimentation check（retro → skill 沉淀判定）

A loop that ran well is a **candidate skill** — this is where one-off work turns
into compounding assets. Run the three-criteria precheck from skill-craft:

- 会重复吗？（这个 loop 还会再跑 / 同类任务还会出现 ≥3 次？）
- 有跑偏风险吗？（本次 retro 的 findings 就是证据）
- 有可验收交付物吗？（harness + 产出文件即是）

All three hold → add a **沉淀提案** to the report: hand the harness, SPEC
decisions, and gotchas to **skill-craft Task A** as raw material（三判据证据已
现成）。A thin-shell skill (description + a one-page router to the LOOP-PROMPT)
is often enough — the marginal value is natural-language triggering. Not all
three → say so and skip; don't sediment single-use work.

### Step 4 — Report and hand decisions to the human

Write `RETRO.md` in the loop's directory using `assets/retro-template.md`
(summary → vitals → findings w/ evidence → the triad → sedimentation check →
decision list). Present the user a compact decision list: which revisions to
apply, which proposals to ratify, whether to sediment. Applying ratified harness
edits is **loop-review --fix territory or a follow-up request** — not something
you do unasked. **Profile feedback**: any stable preference this run revealed
(e.g. a cap style, a red line) → propose appending to `~/.claude/loop-profile.md`.
**Comprehension check（对抗理解债）**: for runs that produced substantial output
the user hasn't read, offer a quiz — "要不要我出 5 道关于这次产出的测验，帮你
确认真的读懂了它交付的东西？" A loop the user can't pass a quiz on is a loop
they're trusting blind; accepting unread output is how comprehension debt
compounds. Offer, don't force.

## Rationalizations table

| The excuse | Why it's invalid |
|---|---|
| "Log 太长，看看结尾就行。" | Vitals need the full pass — thrash and drift live in the middle. Count with commands if reading is impractical. |
| "这个失败是偶发的，不值得记 gotcha。" | It happened, so it's real — that's the whole bar. One line of eval today beats re-debugging it next month. |
| "顺手把 harness / STANDARDS 改了吧，反正结论明确。" | Ratified artifacts are human-owned. Propose with before→after; let the human apply or ratify. |
| "循环成功结束了，没什么可复盘的。" | Success hides miscalibration: standards that never failed, gates never hit, budget 3× oversized. Mine the non-failures. |
| "凭整体印象给结论就够了。" | A finding without a cited log line is an opinion. Evidence only. |

## Exit conditions

**All boxes ticked before you call the retro done:**

- [ ] Vitals table extracted, numbers traceable to artifacts.
- [ ] Every finding cites concrete evidence (line/quote).
- [ ] Triad produced: harness revisions (before→after) + ≥0 gotcha cases (every
      real failure captured, none invented) + standards proposals (marked 需签核).
- [ ] Sedimentation check run (three-criteria precheck; 沉淀提案 or explicit skip).
- [ ] Nothing ratified was edited; `RETRO.md` written; decision list presented.

## Assets

- `assets/retro-template.md` — the RETRO.md structure.
