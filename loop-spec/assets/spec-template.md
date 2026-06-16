# Loop Spec: <task name>

> The contract for the loop. `loop-engineering` turns this into a prompt;
> `loop-eval` turns the success criteria into a measurable eval set. Only a human
> edits this file.

## Goal
<One sentence: what the agent accomplishes autonomously.>

## Success criteria  (verifiable — done = all true)
- [ ] <Check 1 — confirmable by a command or direct observation>
- [ ] <Check 2>
- [ ] <Check 3>

## Environment
- **Location:** <repo / paths / data>
- **Run / build / test:** <exact commands>
- **Access / conventions:** <credentials, style, anything the agent must know>

## Tools available
- <tool — one-line purpose; keep the set minimal>

## Constraints & guardrails  (must never happen)
- <e.g. don't touch production / don't exceed $X / don't edit tests to pass>

## Stop conditions
- **Done:** all success criteria verified.
- **Blocked:** <what "stuck" looks like> → record + stop / escalate.
- **Hard cap:** <max iterations / time / budget>.

## Likely failure modes  (for this task specifically)
- Over-ambition (one-shotting) and false completion are assumed; guard against both.
- <Other task-specific risks.>

## Pattern hint
<build-until-green | research | debug | batch/parallel | orchestrator-worker |
generator-critic — see loop-engineering/references/patterns.md>

## Open questions  (unresolved — needs a human decision)
- <Anything the spec couldn't pin down. Don't invent answers here.>
