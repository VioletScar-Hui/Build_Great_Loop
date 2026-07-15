---
name: loop-spec
description: >-
  Mandatory interactive intake BEFORE any agent loop is authored: co-run
  requirement clarification, standards setting, spec writing, and goal/sub-goal
  decomposition WITH the user, brainstorm-style. Trigger whenever the user wants
  to create/build a loop, autonomous agent, or harness — "我想做个 loop/agent 来
  …", "帮我构建一个循环", "help me build a loop for X", "set up an agent that…" —
  even if (especially if) their description already looks complete. When the idea
  is still vague — "我想做个 agent 但还没想好怎么定", "帮我理理需求", "先帮我拆下
  目标" — this skill MUST be used INSTEAD of generic brainstorming skills: for
  anything that will BECOME an agent/loop this IS the purpose-built brainstorm
  (generic brainstorming lacks the loop question banks, standards library, and
  sign-off pipeline).
  Clarifying questions MUST go to the user; never answer them yourself. Produces
  user-signed-off SPEC.md / GOALS.md / STANDARDS.md (written by a cheap
  doc-writer subagent), then hands off to loop-engineering. Not for auditing an
  existing loop (loop-review), scheduling/operating one (loop-ops), or writing
  evals (loop-eval).
---

# Loop Spec — Interactive Intake

Turn "I want a loop that does X" into a **user-ratified specification**: clarified
requirements, explicit standards, a goal tree decomposed to verifiable leaves, and
the documents that the whole loop will steer by. This happens **with** the user, in
rounds, before a single line of loop prompt is written.

> Interview in **the user's language**. Skill internals stay English.

## Iron law

**NO INTERVIEW, NO SPEC. NO USER ANSWER, NO ASSUMPTION.**

Every load-bearing unknown gets asked to the user — never self-answered, however
"obvious" the answer seems. A loop built on a guessed requirement fails at the most
expensive possible moment: after it has run for hours. The interview is where that
failure is cheap.

**绝不允许**: skipping the interview because the description "seems complete";
inventing an answer to an open question; writing SPEC/GOALS/STANDARDS the user has
not confirmed; treating this skill as optional when a loop is being created.

## Prerequisites

- [ ] The user is present to answer questions. If this session is genuinely
  non-interactive (CI / batch), your deliverable **is the question list itself** —
  output the questions, state that the interview is blocked on answers, and stop.
- [ ] You know which project directory the docs will live in (ask if unclear —
  default `./loop-docs/`).

## The interview loop

Run phases in order. Each phase has a **verify** gate — do not advance until it
passes. Ask **2–4 questions per round** using structured options (use the
AskUserQuestion tool when available, with concrete choices + your recommendation
first; otherwise numbered questions in chat) — **but only for independent
questions**, ones whose answer doesn't change what else needs asking. The moment
a question **branches off a prior answer** (dependent, not parallel — "if retry,
how many times; if not, escalate to whom") stop batching: ask that one alone,
wait for the answer, then formulate the next question from it. Pre-guessing every
branch to keep the batch full is how "2–4/round" quietly turns back into the
ten-question wall it exists to prevent. Never ask a wall of ten questions, and
never ask questions whose answer is already in what the user said — confirm those
instead (see Profile & prefill below for facts, which shouldn't be asked at all).
The ≤4-per-round grouping applies to **every list you put in front of the user,
in every phase** — Phase 1 questions, Phase 2 open points, sign-off items — and
to non-interactive deliverables too (Round 1 = the blocking minimum, later rounds
follow-ups). A wall of questions is a wall even on paper, and even when you call
them "open points".

One more universal rule: **every deliverable that pauses for user input ends with
a one-line "what happens next"** — through docs sign-off → harness authoring
(loop-engineering) → the final stop-condition confirmation before delivery. The
user should never wonder where they are in the pipeline.

**Profile & prefill — information is asked ONCE, ever.** Before composing any
question round:
1. Read `~/.claude/loop-profile.md` if it exists (stable preferences, family
   defaults, environment facts — each with provenance). **Never re-ask what the
   profile answers**; instead show it as a prefilled decision ("按你的画像默认：
   预算 ~$3/12 增量 — 沿用还是这次改？").
2. **Fact-lookup, not question**: for a load-bearing question that is a *fact*
   about the environment rather than a *decision* — settled by a config file,
   lockfile, existing script, `git remote -v`, and not yet stated by the user —
   go look it up rather than asking. One unambiguous answer → state it and move
   on (not even marked 「推断」 — it isn't a guess). Multiple candidates or
   nothing found → it's not a fact anymore; fall through to inference or a real
   question. What never moves: decisions stay the user's, however easy they'd
   be to guess.
3. **Infer-prefill from context**: answers pattern-matched from the conversation
   or repo (not a hard fact, still a guess) get drafted by you, marked 「推断」,
   and put up for confirmation — confirming costs the user a tenth of answering.
4. Only what is neither a looked-up fact, in the profile, nor inferable becomes
   a real question.
5. At sign-off, any NEW stable preference learned this interview → **propose**
   appending it to the profile (user confirms; the profile is user-owned).
   Conflicts resolve in favor of this task's answer, with a profile-update
   proposal. The lite micro-interview consults the profile the same way — three
   questions can become three confirmations.

### Phase 0 — Frame & path selection

Restate the user's goal in ONE sentence ("你要的是：…，对吗？") plus what you think
is *out* of scope. In the same breath, gauge **familiarity**（"这类任务/这个领域
你熟吗？"，能从上下文推断就不问）——it decides whether Phase 1 opens with a
blindspot pass.

**Path selection (proportionate intake).** A gate that is disproportionate gets
bypassed, and a bypassed gate protects nothing. Judge the task against the **lite
criteria — ALL four must hold**:

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
  (restated in chat for confirmation — no `./loop-docs/`, no doc-writer, no goal
  tree). loop-engineering's final stop-condition confirmation **still applies**.
- **One-way ratchet**: if any micro-answer reveals risk or scale beyond the
  criteria, upgrade to the full path immediately. Never downgrade mid-flow.

**Micro-interview (lite path, exactly these three — each with a numeric default):**
1. 完成的机器可检标准是什么？（哪条命令/观察能证明做完了）
2. 失败怎么处理 + 有什么绝对不能碰的？（✦默认：跳过并记录；只写工作区）
3. 上限：最多多少增量 / 多少预算？（✦默认：增量 = 条目数 ×1.2 封顶，预算 $0.3 —
   lite 判据本就要求 <$0.5。默认值必须是具体数字，"跑跑看再定"不算上限）

**Verify (both paths)**: the user explicitly confirms the framing AND the path.
No confirmation, no progress.

### Phase 1 — Clarify (需求澄清 · brainstorm · 未知项四象限)

Identify the task family and **pull its question bank**
(`references/question-banks.md`) — that's the floor: every load-bearing question
in the bank must end up user-answered or visibly already-answered (confirm, don't
re-ask). Then work the **four-quadrant elicitation**
(`references/unknowns-elicitation.md`) on top:

- Phase 0 gauged familiarity（"这个领域你熟吗？"，或从上下文推断）。不熟 → 提问
  之前先做 **盲点扫描**：列出该领域的经典陷阱与"行家才知道该问的问题"（3–6 条，
  各带一句为什么），把未知的未知降级为可提问项。（真实运行的 gotcha「转载源冒充
  独立源」正是这一步能提前抓住的。）
- 固定问一句 **参考物**："有没有现成的参考物——往期满意的产出/喜欢的样式/类似
  实现的代码？" 一个好参考物顶几百字描述；有就直接读原件反推口径。
- This is also the **brainstorm**: each round, offer at least one option the user
  likely hasn't considered — diverge first, then converge on decisions.

**Why**: users under-specify what they've never watched fail, and interviewers
under-ask what they've never watched fail — the bank encodes the failures already
watched; the blindspot pass covers the domain-specific ones the bank can't know.

**Verify**: you can list zero remaining load-bearing unknowns. Anything genuinely
undecidable now goes into SPEC.md's Open Questions **by user consent**, not by
silent omission.

### Phase 2 — Standards (标准制定)

Turn quality expectations into **machine-checkable standards**: acceptance checks,
quality bars, hard constraints/red lines, and the budget class (time/token).
**样例先行 pre-step（未知的已知）**：若质量目标属于"说不清、看到才知道"（简报
长相、标注口径、文风），先花一个便宜增量做 **2–4 版差异大的微样例**让用户挑和改，
把反应反推成标准条款——**不要让用户批准他们无法想象的抽象标准**。样例即弃，
不是交付物。

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

### Phase 4 — Docs (规格化文档 · doc-writer subagent)

Dispatch a **doc-writer subagent on a cheap model (haiku)** to write the documents
into the project (default `./loop-docs/`), one file per template in `assets/`:

- `SPEC.md` — framing, decisions from Phase 1, open questions (user-consented);
- `STANDARDS.md` — the approved standards, each with its check;
- `GOALS.md` — the approved goal tree with per-leaf acceptance checks;
- `PLAN.md` — skeleton only (the loop's plan-iteration cycle will fill it).

Brief the subagent with the interview conclusions verbatim; it formats, it does
not invent. Review its output yourself, fix drift, then show the user a compact
summary for **sign-off**.

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
| "这几个问题有依赖，但硬凑进一轮也就是多问几个选项。" | A batched question covering every possible branch of a dependent answer IS the ten-question wall, just reshuffled into one message. Ask the root question alone; the dependent one only exists once you know which branch you're on. |

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
- [ ] SPEC.md / STANDARDS.md / GOALS.md / PLAN.md written to disk by the doc-writer
      and signed off by the user.

**Lite path — all of these instead:**

- [ ] All four lite criteria verified AND the user confirmed the path choice.
- [ ] The three micro-answers came from the user (not assumed).
- [ ] The inline spec was restated in chat and confirmed.
- [ ] No answer revealed risk/scale that demands the full path (else ratchet up).

Then hand off to **loop-engineering** to author the harness. Tell the user what
comes next: loop-engineering will still ask **one final confirmation of the stop
conditions** before delivering the prompt — that gate belongs to it, not to you.

## Assets & references

- `references/question-banks.md` — load-bearing questions by task family
  (Phase 1's floor). **Read when the family is identified.**
- `references/unknowns-elicitation.md` — 四象限引出法：盲点扫描 / 样例先行 /
  参考物优先。**Read when the user is unfamiliar with the domain or the quality
  target is "看到才知道".**
- `references/standards-library.md` — proven machine-checkable standard patterns
  by family (Phase 2's drafting source).
- `assets/spec-template.md` · `assets/standards-template.md` ·
  `assets/goals-template.md` · `assets/plan-template.md` — the doc-writer's
  templates.
- `assets/doc-writer-brief.md` — the reusable subagent brief (model: haiku), with
  the optional `.claude/agents/` persistence snippet.
