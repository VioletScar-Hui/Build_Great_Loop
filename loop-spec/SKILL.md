---
name: loop-spec
description: >-
  Intake interview for an agentic loop — turn a fuzzy "I want an agent that does
  X" into a crisp, written SPEC the loop can be built from. Use this BEFORE
  authoring a loop prompt, whenever the user's task is underspecified, or when the
  user says things like "I want to set up an agent/loop but I'm not sure how to
  define it", "help me scope an autonomous task", "what should my agent's goal /
  success criteria / stop conditions be". It gathers goal, verifiable success
  criteria, environment, tools, constraints, stop conditions, and likely failure
  modes, then writes a SPEC.md. Hand the SPEC to the loop-engineering skill to
  produce the actual loop prompt.
---

# Loop Spec — Intake

A loop is only as good as its goal. Most loop failures trace back to a fuzzy spec:
no verifiable success criterion (so it never knows it's done), no stop condition
(so it runs forever or quits early), no defined environment (so it flails). This
skill front-loads that thinking into a written **SPEC.md** that `loop-engineering`
then turns into a prompt.

> Interview and write the spec in **the user's language.** Keep your own reasoning
> in English.

## How to run the interview

Be efficient and concrete — ask in small batches, propose sensible defaults, and
fill in what you can infer rather than interrogating. Aim for a usable spec in a
handful of exchanges, not a questionnaire marathon. If the user already answered
something in their description, don't re-ask — confirm it.

Gather these eight things (they map 1:1 to the seven design dimensions a loop
prompt needs, plus a pattern hint):

1. **Goal** — in one sentence, what should the agent accomplish autonomously?
2. **Success criteria** — how do we know it's *done*? Push for **verifiable**
   checks: "two people would agree it's met." If the user says something vague
   ("works well", "looks good"), convert it into observable checks together
   ("X command exits 0", "the file contains Y", "the feature works after reload").
   This is the most important part — spend the most effort here.
3. **Environment** — where does it run? Repo/paths, how to build/run/test, data
   location, any access or credentials.
4. **Tools** — what can the agent use (CLI, browser, APIs, sub-agents)? What's the
   minimal set actually needed?
5. **Constraints & guardrails** — what must it never do? (Don't touch prod, don't
   spend over $X, don't edit the tests to pass, don't delete data.)
6. **Stop conditions** — when does it stop *trying*? Define "blocked/stuck", and a
   hard cap (max iterations / time / budget) so it can't run forever.
7. **Failure modes** — what's likely to go wrong for *this* task specifically? (Use
   to pre-empt with guardrails. Always assume over-ambition and false completion;
   ask what else.)
8. **Pattern hint** — does this look like build-until-green, research, debug,
   batch/parallel, orchestrator-worker, or generator-critic? (See
   `../loop-engineering/references/patterns.md` if unsure.)

If the user can't answer something, record it as an **open question** in the spec
rather than inventing an answer — unresolved ambiguity is exactly what a spec is
for surfacing.

## Output

Write a `SPEC.md` using the structure in `assets/spec-template.md`. Save it where
the user wants (default: the project root or the working directory). Then offer the
natural next step: *"Want me to turn this into the actual loop prompt?"* → hand off
to **loop-engineering**, and (for measurable tasks) **loop-eval** for the success
criteria/eval set.

## Quality bar for a spec

- The success criteria are verifiable, not vibes.
- There's a hard stop condition.
- The environment is concrete enough that a fresh agent could act.
- Open questions are listed, not papered over.
