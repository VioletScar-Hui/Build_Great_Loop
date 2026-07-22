# Loop Patterns Library

Pick the pattern that fits the task, then assemble the harness around it. Each
pattern lists *when to use it*, its *skeleton*, the *state it needs*, and the
*failure mode it guards against*. Patterns compose — a research loop often nests an
orchestrator-worker; a build loop often nests generator-critic.

---

## 1. Iterate-until-green (the canonical loop)

The default for "build/fix X until it meets a bar." A single agent works one
increment at a time against a checklist of verifiable checks.

**Use when:** there's an objective pass/fail bar (tests, acceptance checks, a
linter, a schema) and the work decomposes into increments.

**Skeleton:**
```
Orient: read progress + task list, pick the highest-priority failing check.
Plan:   the one change that should make that check pass.
Act:    make the change.
Verify: run the check (and the existing ones — don't regress).
Record: mark it passing, commit, update progress. Loop.
Stop:   all checks pass | hard cap hit | stuck on the same check twice.
```

**State:** task list (JSON, status per check), progress file, git.

**Guards against:** over-ambition (one check at a time) and false completion (a
check only flips when it actually passes).

---

## 2. Spec → Build → Verify (spec-driven)

Write the spec first, then loop against it. The spec is the durable contract; the
build loop just makes reality match it.

**Use when:** requirements are non-trivial or ambiguous, or multiple people/agents
must agree on "what we're building." (GitHub's spec-driven development.)

**Skeleton:**
```
Phase 0 (once): produce SPEC.md — goal, acceptance criteria, constraints.
Then run iterate-until-green with the spec's criteria as the checklist.
Any time reality and spec disagree, the spec wins (or a human amends the spec).
```

**State:** SPEC.md (protected — only a human edits it), plus the iterate-until-green
state.

**Guards against:** silent drift (the spec is the fixed star) and false completion
(criteria come from the spec, not the agent's mood).

---

## 3. Orchestrator–Worker (sub-agents)

A lead agent holds the plan and clean context; it dispatches sub-agents to do deep
or specialized work, each returning a condensed summary.

**Use when:** subtasks need a lot of context to do but only a little to report
(deep code search, document analysis, a self-contained build step), or you want
separation of concerns (a tester agent, a cleanup agent).

**Skeleton:**
```
Lead Orient: read plan, pick the next subtask.
Lead Plan:   write a crisp, self-contained brief for a worker.
Dispatch:    worker runs in its own context, does the deep work.
Collect:     worker returns a 1–2k-token summary (not its whole trace).
Lead Verify+Record: integrate, verify, update plan. Loop.
```

**State:** lead's plan/progress file; workers are stateless beyond their brief +
returned summary.

**Guards against:** context bloat (deep exploration stays inside workers) and
over-ambition (lead stays at plan altitude).

---

## 4. Parallel map-reduce (fan-out / fan-in)

Many independent items, same operation. Process in parallel, then merge.

**Use when:** items don't depend on each other — classify N documents or summarize
N tickets. A migration may fan out its independent reads/computation, but its
side effects still need ordered serialization. If order or shared mutable state
cannot be isolated, don't use this pattern.

**Skeleton:**
```
Map:    split into independent units; run the same per-unit loop on each (often
        as parallel sub-agents).
Effect: classify calls as read_only or side_effecting. Parallelize only independent
        reads; enqueue mutations with a unique sequence and lease/fencing token.
Reduce: merge results after required effects commit; resolve conflicts; verify the aggregate.
```

**State:** a manifest of units with per-unit status (so a reset can resume the
unfinished ones); a results store; for mutations, an ordered effect queue whose
claims bind the run and authority context.

**Guards against:** lost progress on large batches (manifest = resumable) and
context bloat (each unit is isolated).

---

## 5. Debug loop

A disciplined loop for "something is broken." Reproduce before you theorize; change
one thing at a time.

**Use when:** fixing a bug, a flaky test, or unexpected behavior.

**Skeleton:**
```
Orient:  reproduce the failure reliably; capture the exact symptom.
Plan:    form ONE hypothesis about the cause; predict what a test would show.
Act:     make the smallest probe/change to test that hypothesis.
Verify:  did the symptom change as predicted? If not, the hypothesis was wrong.
Record:  log the hypothesis + result (so you don't retest it). Loop.
Stop:    symptom gone + root cause understood | escalate after N dead hypotheses.
```

**State:** a hypothesis log (tested theories + outcomes), the repro steps.

**Guards against:** thrashing (each cycle is a falsifiable hypothesis, logged) and
false completion (root cause must be understood, not just symptom masked).

---

## 6. Research / explore loop

Gather, synthesize, note, repeat — for open-ended investigation where you don't
know the answer shape up front.

**Use when:** literature/market/codebase research, due diligence, "find out X."

**Skeleton:**
```
Orient: read the notes-so-far; identify the biggest open question.
Plan:   the next query/source most likely to close it.
Act:    retrieve (just-in-time — keep identifiers, not full dumps).
Verify: does this actually answer the question, or raise a better one?
Record: write findings + new questions to a notes file. Loop.
Stop:   questions answered to the required confidence | coverage cap | diminishing
        returns.
```

**State:** a notes file (findings + open questions + sources), ideally with
citations.

**Guards against:** context bloat (notes externalize findings; raw sources stay
out) and aimless wandering (always driven by the biggest open question).

---

## 7. Generator–Critic (reflection)

Produce a draft, critique it against explicit criteria, revise. A quality loop you
nest inside others.

**Use when:** output quality is subjective-but-improvable (writing, design, a plan,
a piece of code) and a single pass isn't good enough.

**Skeleton:**
```
Generate: produce a draft.
Critique: score it against named criteria; list specific, actionable defects.
Revise:   fix the top defects.
Stop:     no defect above threshold | improvement per round goes flat | round cap.
```

**State:** the criteria (fixed), the current draft, the last critique.

**Guards against:** false completion (an explicit critic gate) — but cap the rounds,
or it polishes forever past diminishing returns.

---

## Choosing fast

- Objective bar, incremental work → **iterate-until-green** (1).
- Fuzzy/contested requirements → wrap it in **spec-driven** (2).
- Deep subtasks / specialization → **orchestrator-worker** (3).
- Many independent items → **parallel map-reduce** (4).
- Something's broken → **debug loop** (5).
- Open-ended "find out" → **research loop** (6).
- "Make it better" quality pass → **generator-critic** (7), nested.
