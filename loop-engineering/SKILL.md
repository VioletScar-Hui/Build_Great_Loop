---
name: loop-engineering
description: >-
  Author a NEW, ready-to-run prompt or harness for a long-running iterative agent
  after its goal and load-bearing decisions are settled. Use for
  iterate-until-passing, multi-session, self-verifying, research, coding, or bulk
  processing loops that need state, stop conditions, and recovery. If intent is
  still unsettled, use loop-spec first. If a harness already exists and the user
  wants it improved or diagnosed, use loop-review first. Use loop-eval for test
  design, loop-ops for scheduling/unattended operation, and loop-retro after a
  real run. The deliverable is the smallest sufficient paste-ready harness, not
  the task itself. Trigger only when the user explicitly wants a reusable loop
  prompt/harness; direct requests to fix, run, or iterate on the task itself are
  ordinary execution. Requests that include actual scheduling/operation are led
  by loop-ops; when called by loop-ops, return only the per-run prompt.
metadata:
  version: 7.1.0
---

# Loop Engineering

Loop engineering is the craft of designing the *harness* around a model so it can
run **repeatedly and autonomously toward a goal** — across many turns and even
across context resets — without going off the rails. The model is the engine; the
loop is everything else: the goal it steers by, the state it remembers, the
verification that keeps it honest, and the conditions that tell it to stop.

Your job when this skill triggers: take the user's task description and produce a
**complete loop prompt** they can paste into a fresh agent and run. The deliverable
is the **prompt** — not advice about loops, and **not the task itself done for
them**. Write the paste-ready prompt and stop there. Only go on to actually execute
or build what the prompt describes if the user *explicitly* asks (e.g. "run it",
"execute", "跑一遍", "show it working"). If they just say "use loop-engineering for
X" or "build me a loop that does X", they want the prompt, not X.

> Respond and write the produced prompt in **the user's language**. Keep this
> skill's internal reasoning in English; switch to their language for the
> deliverable and the conversation.

## The mental model

> "Imagine a software project staffed by engineers working in shifts, where each
> new engineer arrives with no memory of what happened on the previous shift."
> — *Anthropic, Effective harnesses for long-running agents*

Every loop iteration is a fresh shift worker. They are smart but amnesiac. A good
loop hands each shift: a clear goal, the current state written down, a way to
verify their own work, and a rule for when to stop. Design for the amnesiac.

## The two things that break loops

Almost every loop failure is one of these. Design against both, explicitly:

1. **Over-ambition** — the agent tries to one-shot the whole thing, runs out of
   context mid-way, and leaves a half-built mess the next shift can't read.
   *Antidote:* one increment per iteration.
2. **False completion** — the agent sees partial progress and declares victory
   without testing. *Antidote:* mandatory self-verification that tests the result
   the way a user would, plus verifiable success criteria.

If a loop prompt you write doesn't visibly defend against these two, it isn't done.

## The five beats (the loop skeleton)

Every iteration runs the same cycle. Bake these five beats into the prompt:

1. **Orient** — read the current state before doing anything (progress file, task
   list, git log, last error). Where am I? What's the next unfinished thing?
2. **Plan** — choose the *single* smallest increment that moves toward the goal.
3. **Act** — do that one increment. Nothing more.
4. **Verify** — prove it works. Test as a user would, not just "the code looks
   right." A green unit test is not proof the feature works.
5. **Record** — write progress to durable state, leave the workspace clean, so the
   next (amnesiac) shift can pick up instantly.

Then loop — until a stop condition fires.

## The seven design dimensions

A top-tier loop prompt answers all seven. When authoring, walk this list and make
sure each is concretely specified, not hand-waved. Deep guidance for each lives in
`references/principles.md` (read it before authoring your first loop).

1. **Goal & success criteria** — verifiable enough that two people would agree
   it's met. "Works well" is not a criterion; "all 12 acceptance checks pass" is.
2. **Stop conditions** — when to stop succeeding (done), stop trying (blocked/
   escalate), and a hard cap (max iterations / budget) so it can't loop forever.
3. **The loop skeleton** — the five beats, with one increment per iteration.
4. **State & memory** — what gets written where, so progress survives a context
   reset. Externalize to files; don't trust the context window.
5. **Context discipline** — keep the working set small and high-signal;
   just-in-time retrieval over preloading; compaction/cleanup as it grows.
6. **Tools** — the minimal set of clear, consolidated tools the loop needs, with
   recovery-oriented error handling. Classify calls as read-only or
   side-effecting; parallelize only independent reads and serialize effects.
7. **Verification & guardrails** — how each iteration self-checks, plus explicit
   guardrails against the anti-patterns (no faking, no editing tests to pass).

## Operational rigor

Use the smallest set of controls that closes demonstrated risks. The core floor
is verifiable success, explicit stop conditions, one increment at a time, durable
state when work spans runs, and real verification. Add the following when the
task characteristics justify them:

1. **Make every success criterion machine-checkable.** "Works well" can't be
   verified; "`npm test` exits 0", "the output CSV has N non-empty rows", "the
   endpoint returns 200" can. If a criterion genuinely needs human judgment, say
   exactly what the human checks.
2. **When work spans runs, make resume crash-safe and idempotent.** A long loop
   *will* be interrupted
   mid-iteration. Claim the work item before acting (mark it in-progress), make
   the Record step atomic, and ensure resuming never double-processes or corrupts
   state. The test: killed at any instant, the next run picks up cleanly — nothing
   lost, nothing done twice.
3. **Size the increment and the cap on purpose.** The increment is the *smallest
   unit you can independently verify*. The hard cap is *large enough to make real
   progress, small enough to stay inside the context/time budget* — state the
   reasoning; don't drop in a random number.
4. **Give the operator a glanceable signal.** A one-line status or end-of-run
   summary (done / in-progress / blocked / remaining) lets a human check the
   loop's health without reading everything. Long-running means unattended, and
   unattended means it has to report.
5. **Match autonomy to trust, and gate the rest.** State an **autonomy level** —
   L1 report-only / L2 assisted (narrow reversible changes) / L3 unattended — and
   **default a new loop to L1**; earning a higher level is a deliberate decision,
   not a default. Route risky, irreversible, or ambiguous actions to a **human
   gate**: stop and escalate *with full context* rather than guess and act. For
   L2/L3, require the runtime environment—not prompt text—to enforce permissions,
   denylists, approval gates, and cancellation. Make the hard cap an externally
   enforced counter such as increments/tool calls/wall time; tokens/$ are hard
   caps only when a runtime meter can stop work, otherwise they are observed
   metrics. Never estimate them from model prose. Remember the loop
   **amplifies judgment — good and bad**, so keep its output
   small enough that a human will actually read it. For running a loop *recurring
   or unattended*, hand off to the **loop-ops** skill.

## Workflow for authoring a loop prompt

1. **Check readiness.** If success, scope, safety boundaries, or budget still have
   unresolved load-bearing choices, hand off to **loop-spec**. Do not re-interview
   when the user already supplied and confirmed those choices. A short, low-risk
   loop may use an inline mini-spec; a durable/high-risk loop should have
   SPEC/STANDARDS/GOALS files.

2. **Pick a pattern.** Map the task to a loop pattern (iterate-until-green,
   orchestrator-worker, spec→build→verify, parallel map-reduce, debug loop,
   research loop). See `references/patterns.md` — it gives the skeleton, when to
   use each, and the failure mode each guards against.

3. **Select components, then assemble.** Read
   `references/component-catalog.md`, record selected component IDs with an
   observed trigger, start from `assets/harness-core.md`, and add only the
   selected clauses from `assets/components/`. For the new lifecycle controls,
   read the selected leaf directly: `assets/components/profile.md`,
   `assets/components/rules.md`, `assets/components/deviations.md`, or
   `assets/components/explainer.md`. Use `assets/harness-skeleton.md` as the
   assembly sheet. Walk the seven dimensions; cut anything that isn't pulling
   weight. The catalog owns trigger, dependency, and acceptance detail; this
   skill only routes selected IDs to their leaves. With no optional trigger,
   keep the manifest and runtime CORE-only.

4. **Wire in verification.** Decide how the loop proves each increment, and how
   the human will measure overall quality. For real success criteria and eval
   design, use the **loop-eval** skill.

   When the harness uses tools, shared state, provider model controls, or a host
   session command, emit and validate the applicable runtime contract from
   `references/runtime-adapters.md`. Bind STATE/CONTAIN to one authority context;
   do not treat PROFILE defaults as API assistant prefill.

5. **Self-review before delivering.** Run the produced prompt past the checklist
   in `references/checklist.md` (the same one **loop-review** uses). Fix any gap.

6. **Confirm only when the risk warrants a gate.** For L2/L3 autonomy,
   unattended operation, irreversible actions, or stop conditions not previously
   ratified, present done / blocked / hard-cap conditions and wait for user
   confirmation. For L1 report-only or reversible workspace-local loops whose
   stop conditions were already confirmed, restate them in the delivery note and
   proceed; an extra blocking turn adds no safety.

## Output contract

Deliver a single, paste-ready prompt with clearly delineated sections and a short
selected-component manifest. It must include: role/goal, the separately ratified
autonomy level (default L1 when unset; intake approval never promotes it), verifiable
success criteria, stop conditions with a deliberately sized enforceable cap, a human
gate for risky/irreversible/ambiguous actions, the environment, the five-beat
loop, real self-verification, guardrails, a glanceable status, and concrete first
actions. Add durable state plus crash-safe idempotent resume when the work spans
runs or promises interruption recovery. Add context-compaction rules when the
working set can grow materially.

**Complexity budget — omit modules whose trigger is absent:**

| Module | Include only when |
|---|---|
| `PROFILE` | Selected by the component-catalog trigger |
| Durable resume protocol | Work spans sessions/runs or promises interruption recovery |
| Sub-agent roles | Isolation, repeated specialization, or independent judgment offsets coordination cost |
| Plan-review cycle | An increment is complex or risky enough that an unchecked plan is material |
| `RULES` | Selected by the component-catalog trigger |
| `DEVIATIONS` | Selected by the component-catalog trigger |
| `EXPLAIN` | Selected by the component-catalog trigger |
| Calibration/golden set | Quality is judgment-based and volume is large enough to drift |
| Shakedown/kill test | L3 or multi-session recovery will be relied upon |
| Four-file loop-docs set | Team ownership, long lifespan, or auditability warrants durable steering docs |

For a small deterministic one-session loop, the correct output is a short flat
harness with none of those modules. Do not mention omitted machinery just to show
you considered it. Never invent a token/$ budget or tool/model name. Name the
external controller for hard caps; label unenforced token/$ values as observed
metrics or placeholders.

Add **sub-agent orchestration only when it pays for itself**: the side task would
flood the main context, independent verification materially reduces risk, or the
same specialist role recurs. A single agent is the default for tightly coupled or
small work. When roles are justified:

- Use only the roles needed: decomposer for genuinely complex leaves,
  plan-reviewer for high-risk plans, independent verifier for fuzzy or consequential
  outcomes, and a formatting helper only for repeated formatting work. Brief each role
  self-contained and use the cheapest capable model available at runtime; never
  hard-code a model or tool name the user's environment may not provide.
- **Docs & workspace integrity**: when ratified steering documents are required,
  verify their expected versions/digests. Missing or changed SPEC/STANDARDS/GOALS
  is a blocking human gate; the loop may create operational state/log files but
  must never reconstruct human-owned goalposts.
- **Plan-iteration cycle when needed**: for complex/high-risk leaves, propose →
  review → revise (cap review rounds) → proceed within the ratified autonomy
  level. Do not force a reviewer round on trivial increments.
- **Shakedown protocol**: before L3 or multi-session unattended use, run 2–3
  supervised increments, test the verifier, and deliberately interrupt once if
  crash-resume is a requirement. One-session L1 loops do not need a ceremonial
  kill test.
- **Calibration protocol (quality-fuzzy loops)**: when per-increment verification
  is judgment-based (labeling, research, summarizing), the harness runs a
  **calibration increment** on a cadence — golden-set items re-processed + random
  completed items re-checked by the VERIFIER; agreement below the ratified
  threshold pauses auto-continue and escalates with the disagreeing cases
  (protocol designed with **loop-eval**). Deterministic loops state explicitly
  that the test suite is the calibration and skip it — don't cargo-cult golden
  sets where `npm test` already answers the question.

**Lite contract** — use a flat harness and inline mini-spec. Keep verifiable
criteria, one increment per iteration, a budget-inclusive hard cap, and a status
line. Add durable crash-safe state only if work must survive interruption. Add
human confirmation only when the risk rule above requires it. Proportionality
keeps the safety controls that match the actual failure modes.

After the prompt, give a 2–4 line note: which pattern you used, the key design
choices, and what the user should tune for their case.

## The quality bar

Before you call a loop prompt done, it should pass all of these:

- A fresh agent could start from it with zero extra context.
- Success is **machine-checkable**, not vibes. Stop conditions are explicit,
  including a hard cap (sized on purpose) so it can't run forever.
- If the loop spans runs or promises recovery, progress survives a context reset
  and resume is crash-safe; otherwise the prompt explicitly scopes itself to one
  session.
- It does one increment at a time (sized to the smallest verifiable unit) and
  verifies before moving on.
- It defends against over-ambition and false completion by name.
- A human can glance at a status/summary to see the loop's health.
- Load-bearing decisions came from the user or are visible, reversible defaults.
- Sub-agent roles, docs scaffolding, review cycles, calibration, and shakedown are
  present only where the task's scale, uncertainty, or risk justifies them.
- Every instruction earns its place; nothing speculative or redundant.

## Rationalizations to refuse

Under time pressure the *authoring* agent (you) will be tempted to cut the very
corners this skill exists to prevent. Each shortcut below feels reasonable in the
moment; each is how a loop ships broken. When you catch yourself thinking the left
column, apply the right.

| The tempting shortcut | Why it's wrong |
|---|---|
| "Fastest way to help is to just build the thing they described." | The deliverable of *this skill* is the loop **prompt**, not the executed task. Hand over the paste-ready prompt and stop; only run/build it yourself if the user explicitly asks. This is the most common drift — guard it hardest. |
| "The user's description is detailed enough — skip readiness." | Detail can still hide load-bearing ambiguity. Check success, scope, risk, and budget; invoke loop-spec only for unresolved decisions. |
| "Stop conditions were already covered — ask again anyway." | Repetition is not a safety control. Reconfirm only for unattended/risky autonomy or when the prior decision is missing or stale. |
| "Sub-agents make every harness stronger." | They add context boundaries, latency, and coordination failure. Use them when isolation, repetition, or independent judgment has measurable value. |
| "Every loop needs a kill test." | Interruption testing is essential when resume is promised. It is noise for a one-session report-only loop. |
| "Every increment is verified — calibration is redundant." | Per-increment checks are made by the same judgment that drifts. The golden set is the fixed star: it catches your criteria sliding across hundreds of increments, which no single increment's check can see. |
| "This loop is simple — it doesn't need a hard cap." | Every loop needs a seatbelt. No hard cap means it runs forever the moment the logic fails. Always include one. |
| "I'll just explain how to set the loop up." | The deliverable is the paste-ready prompt itself, not advice about loops. Write the prompt. |
| "'Works well' is a fine success criterion." | If two people could disagree whether it's met, it isn't a criterion. Make each one machine-checkable. |
| "The model will test its own work, so verification is optional." | False completion is the #1 way loops fail. Verification must be mandatory and actually exercise the result. |
| "Keeping state in the conversation is fine." | The context window resets. Anything that must survive a restart goes to a file. |
| "Crash-safety is overkill here." | A long loop *will* be interrupted mid-step. Claim-before-act + atomic record is the floor, not a luxury. |
| "I'm unsure what they want, but I'll pick something reasonable and proceed." | When a load-bearing requirement is genuinely ambiguous, surface it / ask the human — don't bake a guess into a loop that then runs unattended. |

## Reference files

Read these as needed — don't load everything up front (practice what you preach):

- `references/principles.md` — the distilled best-practices behind all seven
  dimensions, with sources. **Read before authoring your first loop.**
- `references/patterns.md` — the loop-pattern library (step 2).
- `references/component-catalog.md` — optional component triggers, dependencies,
  and acceptance checks (step 3).
- `assets/harness-core.md` and `assets/components/` — composable runtime clauses.
- `references/harness-template.md` — legacy worked example; consult only when an
  example is needed, never copy it wholesale.
- `references/context-and-state.md` — deep dive on context engineering, memory,
  and surviving resets (dimensions 4–5).
- `references/runtime-adapters.md` — effect scheduling, authority binding,
  model/effort resolution, current prefill compatibility, eval identity, and
  verified host-session semantics.
- `references/checklist.md` — the audit checklist for self-review (step 5).
- `assets/harness-skeleton.md` — modular assembly sheet.
- `assets/state.schema.json`, `assets/state.example.json`, and
  `scripts/validate_state.py` — STATE contract and deterministic checks.
- `scripts/select_components.py`, `scripts/state_transition.py`,
  `scripts/build_workflow.py`, `scripts/containment_check.py`, and
  `scripts/validate_runtime_contract.py` — deterministic selector, runtime
  contract, and reference implementations used by component fixtures.
