# Loop Engineering — Principles

The distilled, sourced foundation behind the seven design dimensions. Read this
before authoring your first loop. Each section ends with *what to put in the
prompt* — the concrete move, not just the theory.

**Contents**
1. Goal & success criteria
2. Stop conditions
3. The loop skeleton
4. State & memory across resets
5. Context discipline
6. Tools
7. Verification & guardrails
8. Anti-patterns (the things that actually kill loops)
9. Sources

---

## 1. Goal & success criteria

A loop steers by its success criteria the way a ship steers by a star. If the
criterion is fuzzy, the loop wanders or quits early.

- **Make it verifiable.** The test from the evals literature: *a good criterion is
  one where two domain experts would independently reach the same pass/fail
  verdict.* If reasonable people would disagree on whether it's met, it's not a
  criterion yet — sharpen it.
- **Prefer a checklist of concrete checks** over one vague goal. "Build a working
  todo app" → a list of acceptance checks ("can add a task", "tasks persist after
  reload", "can mark complete"), each independently testable.
- **Grade the output, not the path.** Don't hardcode "call tool X then tool Y" —
  that punishes valid alternative approaches and makes brittle loops. Specify the
  *end state* you want; let the agent find the route.

*What to put in the prompt:* an explicit, enumerated success criteria block. Where
possible, make each item machine-checkable (a command that exits 0, a file that
exists, a string that appears).

---

## 2. Stop conditions

A loop without stop conditions is a runaway. Three kinds, all three needed:

- **Done** — the success criteria are met. The loop verifies this, then halts.
- **Blocked / escalate** — the agent is stuck (same error twice, a missing
  credential, an ambiguous requirement). Define what "stuck" looks like and what
  to do: write the blocker to state and stop, or escalate to a human, rather than
  thrashing.
- **Hard cap** — a maximum number of iterations, wall-clock, or token/cost budget.
  This is the seatbelt: even if logic fails, the loop can't run forever. Make the
  cost ceiling explicit (tokens/$), not just an iteration count.
- **Autonomy level & human gate** — state how much the loop may do on its own: L1
  report-only, L2 assisted (narrow, reversible changes), L3 unattended. Default a
  new loop to **L1**. Route risky / irreversible / ambiguous actions to a **human
  gate** — stop and escalate *with full context* rather than act. (For running a
  loop recurring or unattended, see the **loop-ops** skill.)

*What to put in the prompt:* a stop-conditions block naming each of these, with the
exact signal for each ("if the same test fails twice with no new information, stop
and report"; "do at most N increments / $X per run"; "anything touching
auth/payments/migrations → human gate").

---

## 3. The loop skeleton

The five beats — **Orient → Plan → Act → Verify → Record** — exist to defeat the
two killer failure modes (over-ambition, false completion).

- **One increment per iteration is the single most important rule.** Anthropic
  found that asking the agent to "work on only one feature at a time … turned out
  to be critical to addressing the agent's tendency to do too much at once." Small
  units keep each shift inside its context budget and leave clean handoffs.
- **Orient first.** Every shift starts amnesiac. Before acting, it reads the
  current state and picks up where the last shift left off. Skipping this is how
  loops rebuild things that already exist or build on broken foundations.
- **Record last.** Leave the workspace in a "clean state" — *the kind of code you'd
  merge to main: no major bugs, orderly, documented, easy for the next dev to
  continue.* The next shift's Orient depends on this shift's Record.

*What to put in the prompt:* the five beats as the explicit per-iteration
procedure, with "exactly one increment" stated and motivated.

---

## 4. State & memory across resets

The context window is volatile working memory. Anything that must survive a reset
goes to **durable external state** — files, a task list, version control.

- **A progress file** (e.g. `progress.md` / `claude-progress.txt`): a running log
  of what's done, what's in flight, what's blocked, and what's next. This is the
  handoff note between shifts.
- **A structured task list**, ideally JSON. Anthropic notes the model "is less
  likely to inappropriately change or overwrite JSON files compared to Markdown,"
  and recommends constraining the agent to flip only a `passes`/`status` field so
  it can't quietly rewrite the goalposts.
- **Version control as a checkpoint.** Commit after each verified increment with a
  descriptive message. This makes progress legible and failed steps revertible.
- **Crash-safe, idempotent resume.** State only helps if a restart can trust it.
  Claim a work item before acting, make the Record step atomic, and guard writes so
  resuming never double-processes or corrupts state — a loop *will* be killed
  mid-iteration, and that must be harmless. See `context-and-state.md`.
- **Structured note-taking** generalizes beyond code: the agent writes notes to
  memory outside the context window and pulls them back later. This is how an agent
  sustains "multi-hour" tasks across resets — it reads its own notes and continues.

*What to put in the prompt:* name the state files, their format, when to read them
(Orient) and when to write them (Record), and any "you may only change this field"
constraints that protect the goal definition.

---

## 5. Context discipline

> "Find the smallest set of high-signal tokens that maximize the likelihood of
> some desired outcome." — *Anthropic, Effective context engineering*

Context is a finite resource, and **context rot** is real: as tokens pile up, recall
and long-range reasoning degrade — a gradient, not a cliff, but real. Treat the
context window like an attention budget to be spent carefully.

- **Right altitude for the system prompt.** Avoid both failure modes: too low
  (brittle hardcoded if-this-then-that logic) and too high (vague guidance with no
  concrete signal). Aim for specific-enough-to-guide, flexible-enough-to-let-the-
  model-reason. Organize into clear sections (XML tags / Markdown headers).
- **Just-in-time over preloading.** Instead of dumping all data up front, give the
  agent lightweight identifiers (file paths, queries, links) and tools to pull
  detail on demand. Mirrors how humans use file systems and bookmarks instead of
  memorizing everything. A hybrid (preload a little, retrieve the rest) is often
  best.
- **Compaction.** When the window fills, summarize the trajectory into a fresh
  window — preserve architectural decisions, unresolved bugs, key details; discard
  redundant tool outputs. Tune for recall first (lose nothing important), then
  precision. The safest, lightest compaction: clear old tool results once they've
  been used.
- **Sub-agents for depth.** Spin a sub-agent with a clean context to do deep or
  parallel work; it returns a condensed 1–2k-token summary instead of its whole
  exploration. Keeps the main loop's context clean.

*What to put in the prompt:* a short "context discipline" block — retrieve
just-in-time, don't re-read what's already summarized, compact/note when the window
grows, delegate deep dives to sub-agents and keep only their summaries.

See `context-and-state.md` for the deep dive on dimensions 4–5.

---

## 6. Tools

> "Tools are a new kind of software — a contract between deterministic systems and
> non-deterministic agents." — *Anthropic, Writing effective tools for agents*

If the loop has tools, design them for an amnesiac with a token budget, not for a
REST client.

- **Few, high-impact, consolidated.** Build a handful of tools for the workflows
  that matter, not a wrapper per API endpoint. One `schedule_event` beats
  `list_users` + `list_events` + `create_event`. "If a human engineer can't say
  which tool to use, an agent can't either."
- **High-signal, token-efficient returns.** Return names not UUIDs, `file_type`
  not `mime_type`. Offer a concise vs. detailed mode. Paginate/filter/truncate by
  default.
- **Error messages that teach recovery.** A good error models the fix: "too many
  results — narrow with `search_logs(query=…, time_range='last_24h')`." Treat
  errors as the next prompt the agent will read.
- **Namespace** when there are many: `asana_search`, `jira_search`.

*What to put in the prompt:* if you're specifying tools, list the minimal set with
one-line purposes, expected inputs, and what good vs. error returns look like.

---

## 7. Verification & guardrails

Verification is what separates a loop that *works* from a loop that *claims to
work*.

- **Self-verification is mandatory and must be real.** The dominant failure is
  "marking a feature complete without proper testing." The fix is to make the agent
  exercise the result the way a user would (run it, click it, hit the endpoint) —
  not just confirm the code compiles. Anthropic found giving the agent the means to
  actually test "dramatically improved performance."
- **Verify before Record, Record before next.** No increment counts as done until
  it's verified and the state reflects it.
- **External evals for the human.** The loop's self-check tells the agent when to
  continue; a small external eval set tells *you* whether the loop is any good. Use
  the **loop-eval** skill to design these.

*What to put in the prompt:* a verification block specifying how each increment is
proven, and a guardrails block (next section).

---

## 8. Anti-patterns (the things that actually kill loops)

Name these in the prompt so the agent designs against them:

- **One-shotting** — attempting everything at once. → one increment per iteration.
- **False completion** — declaring done without testing. → mandatory real
  verification + verifiable criteria.
- **Reward hacking** — editing/deleting tests or weakening checks to make the bar
  turn green. State plainly: *it is unacceptable to remove or edit tests/criteria
  to pass; that hides missing or broken functionality.* Constrain which fields the
  agent may change.
- **Context bloat / rot** — letting the window fill with stale tool dumps. →
  context discipline (§5).
- **Thrashing** — repeating a failing action with no new information. → "stuck"
  detection in stop conditions (§2).
- **Brittle path-checking** — over-specifying the exact steps. → grade the end
  state, not the route (§1).
- **Silent drift** — quietly rewriting the goal/spec. → protect the goal definition
  in durable state; only a human changes it.
- **Straight to unattended** — letting the loop act on its own before report-only
  (L1) has shown it behaves. → earn autonomy in stages (L1 → L2 → L3).
- **Comprehension debt** — the loop ships faster than any human reads it. A loop
  amplifies judgment, good *and* bad. → keep output reviewable and read what it
  ships; don't just press go.

---

## 9. Sources

- Anthropic — *Effective harnesses for long-running agents* (shift-work framing,
  two-phase init/coding agents, progress file + git, one-increment rule, mandatory
  verification, JSON task list, clean-state definition).
- Anthropic — *Effective context engineering for AI agents* (context as finite
  resource, context rot, system-prompt altitude, just-in-time retrieval,
  compaction, structured note-taking, sub-agents, "smallest set of high-signal
  tokens").
- Anthropic — *Writing effective tools for agents* (consolidation, namespacing,
  high-signal returns, recovery-oriented errors, the "contract" framing).
- Anthropic — *Demystifying evals for AI agents* (verifiable criteria / "two
  experts agree", grade the output not the path, pass@k vs pass^k, small eval sets,
  code-based vs model-based graders, "failures should seem fair").
- Anthropic — *AI-driven code migration* (claude.com/blog/ai-code-migration:
  rulebook-driven regeneration / "fix the process, not the code", discarded rules
  stress-test, adversarial dual review with escalation, model tiering by role,
  derive-the-queue-from-disk / self-writing queue, verification placement by
  cost, build-daemon serialization, phase-gated pipeline of loops).
- GitHub — *Spec-driven development* and *agentic primitives / context
  engineering* (write the spec first; small composable units; reliable workflows).
- GitHub — *Continuous AI / agentic CI* (verification loops in automation).
- Sourcegraph — *Agentic Coding in 2026* (context engineering for large codebases).
- OpenAI — *Codex best practices* (clear task setup, verification, iteration).
