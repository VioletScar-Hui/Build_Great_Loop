---
name: loop-engineering
description: >-
  Author top-tier prompts and harnesses for long-running, iterative AI agent
  loops ("loop engineering"). Use this WHENEVER the user wants to build, design,
  or improve an agent that runs repeatedly toward a goal — iterate-until-passing
  loops, autonomous coding/build agents, research or data-processing agents,
  self-verifying or self-correcting agents, multi-session agents that must
  survive context resets, or any "keep going until it's done" / "run it in a
  loop" / "long-running agent" task. Also trigger when the user asks for a prompt
  that sets up an agentic loop, a harness, a verification loop, or success/stop
  conditions for an agent. The output is a complete, ready-to-paste loop prompt.
  Pair with loop-spec (intake), loop-eval (success criteria/evals), and
  loop-review (audit an existing loop).
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
   recovery-oriented error handling.
7. **Verification & guardrails** — how each iteration self-checks, plus explicit
   guardrails against the anti-patterns (no faking, no editing tests to pass).

## Operational rigor (what separates good from top-tier)

Most prompts get the seven dimensions *present*. Top-tier prompts get them
*right*. Four upgrades do most of that work — apply them by default:

1. **Make every success criterion machine-checkable.** "Works well" can't be
   verified; "`npm test` exits 0", "the output CSV has N non-empty rows", "the
   endpoint returns 200" can. If a criterion genuinely needs human judgment, say
   exactly what the human checks.
2. **Make resume crash-safe and idempotent.** A long loop *will* be interrupted
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

## Workflow for authoring a loop prompt

1. **Get a spec.** If the user's description is thin, don't guess — run a quick
   intake. Use the **loop-spec** skill for a structured interview, or ask inline:
   *what's the goal, how do we know it's done, what environment/tools, what should
   never happen, when should it give up?* A loop is only as good as its goal.

2. **Pick a pattern.** Map the task to a loop pattern (iterate-until-green,
   orchestrator-worker, spec→build→verify, parallel map-reduce, debug loop,
   research loop). See `references/patterns.md` — it gives the skeleton, when to
   use each, and the failure mode each guards against.

3. **Assemble the harness.** Fill the annotated template in
   `references/harness-template.md` (blank copy in `assets/harness-skeleton.md`).
   Walk the seven dimensions; cut anything that isn't pulling weight. Aim for the
   *smallest set of high-signal tokens* that fully specifies the behavior.

4. **Wire in verification.** Decide how the loop proves each increment, and how
   the human will measure overall quality. For real success criteria and eval
   design, use the **loop-eval** skill.

5. **Self-review before delivering.** Run the produced prompt past the checklist
   in `references/checklist.md` (the same one **loop-review** uses). Fix any gap.
   Then hand the user the finished prompt.

## Output contract

Deliver a single, paste-ready prompt with clearly delineated sections (use XML
tags or Markdown headers — structure helps the model navigate). It must include,
at minimum: role/goal, machine-checkable success criteria, stop conditions (with a
deliberately sized hard cap), the environment, the state/memory mechanism (with
crash-safe, idempotent resume), the five-beat loop, the self-verification step,
context discipline, guardrails, a glanceable operator status/summary, and a
concrete "first actions / session startup" block. Keep prose lean and explain
*why* each instruction matters — modern models follow reasoning better than they
follow bare commands.

After the prompt, give a 2–4 line note: which pattern you used, the key design
choices, and what the user should tune for their case.

## The quality bar

Before you call a loop prompt done, it should pass all of these:

- A fresh agent could start from it with zero extra context.
- Success is **machine-checkable**, not vibes. Stop conditions are explicit,
  including a hard cap (sized on purpose) so it can't run forever.
- Progress survives a context reset, and **resume is crash-safe** — interrupt it at
  any instant and it continues cleanly, nothing lost or done twice.
- It does one increment at a time (sized to the smallest verifiable unit) and
  verifies before moving on.
- It defends against over-ambition and false completion by name.
- A human can glance at a status/summary to see the loop's health.
- Every instruction earns its place; nothing speculative or redundant.

## Rationalizations to refuse

Under time pressure the *authoring* agent (you) will be tempted to cut the very
corners this skill exists to prevent. Each shortcut below feels reasonable in the
moment; each is how a loop ships broken. When you catch yourself thinking the left
column, apply the right.

| The tempting shortcut | Why it's wrong |
|---|---|
| "Fastest way to help is to just build the thing they described." | The deliverable of *this skill* is the loop **prompt**, not the executed task. Hand over the paste-ready prompt and stop; only run/build it yourself if the user explicitly asks. This is the most common drift — guard it hardest. |
| "The user's description is detailed enough — skip the spec." | A loop is only as good as its goal. Confirm the success criteria are *verifiable* and a stop condition exists before you write a line; a fuzzy goal is the #1 failure source. |
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
- `references/harness-template.md` — the annotated prompt template + worked
  example (step 3).
- `references/context-and-state.md` — deep dive on context engineering, memory,
  and surviving resets (dimensions 4–5).
- `references/checklist.md` — the audit checklist for self-review (step 5).
- `assets/harness-skeleton.md` — blank template to copy-fill.
