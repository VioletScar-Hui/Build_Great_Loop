---
name: loop-spec
description: >-
  Clarify and scope a NEW agent loop before its harness is authored. Use when the
  user wants to create an autonomous/repeating agent, asks to turn a vague idea
  into a loop, or has not yet settled success criteria, boundaries, risk, or
  budget. First test whether a loop is justified; route one-shot or deterministic
  tasks to a simpler workflow. Use proportionate intake: confirm only
  load-bearing decisions, offer visible reversible defaults for minor details,
  and write durable SPEC/STANDARDS/GOALS artifacts only when the loop's scale or
  lifespan benefits from them. Hands settled intent to loop-engineering. Not for
  reviewing an existing harness (loop-review), measuring it (loop-eval), running
  it on a schedule (loop-ops), or post-run analysis (loop-retro).
metadata:
  version: 4.1.0
---

# Loop Spec — Interactive Intake

Turn "I want a loop that does X" into a **user-ratified specification**: clarified
requirements, explicit standards, a goal tree decomposed to verifiable leaves, and
the documents that the whole loop will steer by. This happens **with** the user, in
rounds, before a single line of loop prompt is written.

> Interview in **the user's language**. Skill internals stay English.

## Core rule

**NO HIDDEN LOAD-BEARING ASSUMPTIONS.**

Ask the user about decisions that materially change success, safety, scope, cost,
or irreversible effects. For minor, reversible details, state a concrete default
and let the user override it. A loop built on a guessed load-bearing requirement
fails at the most expensive moment: after it has run for hours. A loop that asks
about every harmless detail never gets built.

Do not invent answers to unresolved high-impact questions or silently turn an
ordinary task into an autonomous loop. Do not require ceremony merely because the
word "loop" appears.

## Prerequisites

- [ ] The user is present to answer questions. If this session is genuinely
  non-interactive (CI / batch), your deliverable **is the question list itself** —
  output the questions, state that the interview is blocked on answers, and stop.
- [ ] You know which project directory the docs will live in (ask if unclear —
  default `./loop-docs/`).

## The interview loop

Run phases in order. Each phase has a **verify** gate — do not advance until it
passes. Ask **2–4 questions per round** using structured options (use the
available structured-question capability with concrete choices and your
recommendation first; otherwise use numbered questions in chat). Never ask a
wall of ten questions, and never re-ask known information. Apply the PROFILE
intake precedence only when task-relevant stable preferences or discoverable
environment facts exist; otherwise skip PROFILE entirely, including lite loops.
When selected, follow `../loop-engineering/assets/components/profile.md` only for
input classes actually present: inspect and source each discoverable fact; visibly
prefill each stable preference with an override; label and confirm each context
inference. Do not perform or manufacture actions for absent classes. Leave every
load-bearing decision to the user. The ≤4-per-round grouping applies to **every
list you put in front of the user, in every phase** — Phase 1 questions, Phase 2
open points, sign-off items — and to non-interactive deliverables too (Round 1 =
the blocking minimum, later rounds follow-ups). A wall of questions is a wall even
on paper, and even when you call them "open points".

One more universal rule: **every deliverable that pauses for user input ends with
a one-line "what happens next"** — through docs sign-off → harness authoring
(loop-engineering) → the final stop-condition confirmation before delivery. The
user should never wonder where they are in the pipeline.

### Phase 0 — Frame & path selection

Restate the user's goal in ONE sentence ("你要的是：…，对吗？") plus what you think
is *out* of scope.

**Loop-worthiness gate.** Before choosing an intake path, ask whether repetition
and model-driven decisions are actually needed. Prefer a normal command, script,
workflow, or single agent run when the task is one-shot, the route is fully known,
or deterministic automation can solve it. Explain the simpler option and continue
with loop intake only when the loop earns its extra latency, cost, and operational
risk.

**Path selection (proportionate intake).** A gate that is disproportionate gets
bypassed, and a bypassed gate protects nothing. Use the following as heuristics,
not universal laws. The **lite criteria — all four should hold**:

1. Estimated **< 20 increments**;
2. **No irreversible or risky actions** (nothing that would trip a human gate:
   deletes, prod, payments, auth, force-push…);
3. Budget **< $0.5**;
4. Writes **only inside the workspace**.

All four hold → *propose* the lite path in the same breath as the framing
("体量很小，走轻量：3 个问题就够。还是你想走完整访谈？"). The user confirms the
path — eligibility is judged by the criteria, **never by the user's framing or
urgency** ("很小/很急" is not a criterion).

- **Lite path** = the 3-question micro-interview below, then an **inline spec**
  (restated in chat for confirmation — no `./loop-docs/`, formatting helper, or
  goal tree). loop-engineering's final stop-condition confirmation **still
  applies**.
- **One-way ratchet**: if any micro-answer reveals risk or scale beyond the
  criteria, upgrade to the full path immediately. Never downgrade mid-flow.

**Micro-interview (lite path, exactly these three — each with a numeric default):**
1. 完成的机器可检标准是什么？（哪条命令/观察能证明做完了）
2. 失败怎么处理 + 有什么绝对不能碰的？（✦默认：跳过并记录；只写工作区）
3. 上限：最多多少增量 / 多少预算？（✦默认：增量 = 条目数 ×1.2 封顶，预算 $0.3 —
   lite 判据本就要求 <$0.5。默认值必须是具体数字，"跑跑看再定"不算上限）

**Verify (both paths)**: the user explicitly confirms the framing AND the path.
No confirmation, no progress.

### Phase 1 — Clarify (需求澄清 · brainstorm)

Identify the task family and **pull its question bank**
(`references/question-banks.md`) — that's the floor: every load-bearing question
in the bank must end up user-answered or visibly already-answered (confirm, don't
re-ask). Then add task-specific questions the bank can't know. This is also the
**brainstorm**: each round, offer at least one option the user likely hasn't
considered (a simpler alternative, a riskier-but-faster path, an adjacent
opportunity) — diverge first, then converge on decisions.

For shared, team, connector-backed, or multi-tenant loops, settle the authority
boundary as a load-bearing decision: tenant/channel/principal, connector identity,
memory namespace, and who may change the permission snapshot. Do not infer these
from channel visibility or a previous run. Personal single-user loops may mark
the shared-authority questions N/A with a reason.

**Why**: users under-specify what they've never watched fail, and interviewers
under-ask what they've never watched fail — the bank encodes the failures already
watched. Options teach users what's decidable.

**Verify**: you can list zero remaining load-bearing unknowns. Anything genuinely
undecidable now goes into SPEC.md's Open Questions **by user consent**, not by
silent omission.

### Phase 2 — Standards (标准制定)

Turn quality expectations into **machine-checkable standards**: acceptance checks,
quality bars, hard constraints/red lines, and the budget class (time/token).
**Draft from the standards library** (`references/standards-library.md`) — pull
the family's proven patterns, instantiate the thresholds from Phase 1 answers —
then walk the user through each: they approve, edit, or strike. Don't invent from
scratch what the library already hardened; do add task-specific standards the
library can't know. For quality-fuzzy tasks, the 抽检一致 pattern is the
calibration anchor the harness will check mid-run (loop-eval owns the golden set).

**Verify**: every standard is (a) checkable by a command or observation, and
(b) explicitly approved by the user. "尽量好" is not a standard; "每条摘要 ≤50 字
且非空" is.

### Phase 3 — Goal tree (目标/子目标拆解)

Decompose: goal → sub-goals → **leaf tasks**. Granularity standard for a leaf:

- Completable in **one loop increment** (one iteration, one session at most);
- **Independently verifiable** against a Phase-2 standard;
- Has an explicit dependency on at most one other leaf (else split it).

Present the tree (indented list with per-leaf acceptance checks). The user prunes,
reorders, and approves.

**Verify**: user has approved the tree, and every leaf names its acceptance check.

### Phase 4 — Durable artifacts when useful

For multi-session, high-risk, team-owned, or recurring loops, write the approved
decisions into the project (default `./loop-docs/`), one file per template:

- `SPEC.md` — framing, decisions from Phase 1, open questions (user-consented);
- `STANDARDS.md` — the approved standards, each with its check;
- `GOALS.md` — the approved goal tree with per-leaf acceptance checks;
- `PLAN.md` — skeleton only (the loop's plan-iteration cycle will fill it).

Write them directly, or delegate formatting only when it would flood the main
context or is a repeated side task. If delegating, choose the cheapest model that
can reliably preserve the approved content; do not hard-code a model name. The
writer formats and does not invent. Review the output and show the user a compact
summary for sign-off.

For a genuinely lite loop, keep the approved mini-spec inline. Do not create four
files just to satisfy the process.

**Verify**: files exist on disk, match the interview, and the user has signed off.

### Repeat

Any correction at any gate → return to the earliest affected phase. The interview
exits only through the checklist below.

## Rationalizations table

| The excuse | Why it's invalid |
|---|---|
| "用户的描述已经够详细了，直接开写。" | Detail ≠ decisions. Phase 0/2/3 confirmations take minutes; a wrong guess costs an overnight run. Run the interview — it's short when the user truly has decided everything. |
| "问这么多会烦到用户。" | Batched structured options (2–4/round) are fast to answer. What annoys users is a loop that did the wrong thing unattended. |
| "这个问题我可以合理假设。" | If it's load-bearing, ask. If it isn't, don't ask AND don't assume — leave it to the executing loop's judgment. |
| "文档可以之后再补。" | The docs ARE the loop's steering state. A loop without STANDARDS.md re-invents its quality bar every iteration. |
| "先给个初版提示词，跑起来再迭代。" | An unratified loop prompt is exactly the deliverable this skill exists to prevent. Spec first. |
| "用户说这是小任务/很赶，走轻量吧。" | Lite eligibility is judged by the four criteria, not by framing or urgency. An irreversible action stays full-path however "small" the task sounds — and pressure is precisely when gates earn their keep. |

## Good / bad interview (contrast)

**Bad**: "请把你的需求、目标、标准、边界、环境、预算都告诉我。" (one wall, no
options, user does all the work)

**Good**: "两个定向问题：① 500 个文件处理失败时，你要 跳过并记录（推荐）/ 停下等你 /
重试 3 次？② 结果给谁用——人读还是下游程序读？另外有个你可能没想过的选项：其实可以
先只跑 50 个做质量抽检，再放量，要吗？"

## Exit conditions

**Full path — only when ALL boxes are ticked may you hand off:**

- [ ] Phase 0 framing explicitly confirmed by the user.
- [ ] Zero load-bearing unknowns un-asked; open questions are user-consented.
- [ ] Every standard machine-checkable AND user-approved.
- [ ] Goal tree approved; every leaf has an acceptance check and fits one increment.
- [ ] Durable loops: SPEC.md / STANDARDS.md / GOALS.md / PLAN.md exist and match
      the approved decisions. Lite loops: the inline mini-spec is confirmed.

**Lite path — all of these instead:**

- [ ] All four lite criteria verified AND the user confirmed the path choice.
- [ ] The three micro-answers came from the user (not assumed).
- [ ] The inline spec was restated in chat and confirmed.
- [ ] No answer revealed risk/scale that demands the full path (else ratchet up).

Then hand off to **loop-engineering** to author the harness. Tell the user what
comes next: loop-engineering will assemble the harness and will reconfirm stop
conditions only if the chosen autonomy/risk level requires a final human gate.

## Assets & references

- `references/question-banks.md` — load-bearing questions by task family
  (Phase 1's floor). **Read when the family is identified.**
- `references/standards-library.md` — proven machine-checkable standard patterns
  by family (Phase 2's drafting source).
- `assets/spec-template.md` · `assets/standards-template.md` ·
  `assets/goals-template.md` · `assets/plan-template.md` — artifact templates.
- `assets/formatting-helper-brief.md` — optional reusable formatting brief; use a helper
  only when context isolation or repetition justifies it.
