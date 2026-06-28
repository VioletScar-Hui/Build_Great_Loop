# The Harness Template

This is the structure a top-tier loop prompt follows. Below: the **annotated
template** (what each section is for) and a **worked example** (a complete,
paste-ready loop prompt). A blank copy-fill version is in
`assets/harness-skeleton.md`.

Adapt, don't transcribe. Cut sections that don't apply (e.g. tools, sub-agents).
Keep the section order — it reads top-to-bottom the way an agent needs it: who am
I, what's the bar, when do I stop, where am I, how do I remember, how do I work,
how do I prove it, what must I never do, what do I do first.

---

## Weak vs strong (why all this structure earns its place)

A common but **weak** loop prompt:

```
You are an agent. Keep working on <goal> until it's done. Test your work
and don't stop until everything passes.
```

It *sounds* complete. It isn't — and seeing exactly why is the whole lesson:

- No **verifiable** "done" → it can't tell when to stop, so it quits early or never.
- No **hard cap** → when the logic fails, it runs forever.
- No **externalized state** → a restart loses everything; the next shift starts blind.
- No **one-increment** rule → it tries to one-shot and leaves a half-built mess.
- No **real verification** standard → "test your work" lets it declare victory untested.
- No **anti-faking guardrail** → nothing stops it weakening the goal to "pass".

The **strong** version is the annotated template below: same intent, but every one
of those gaps is closed with a concrete, reasoned instruction. The distance between
the two snippets *is* the job of loop engineering.

---

## Annotated template

```
# Role & goal
You are <role> working autonomously to <goal>, one increment at a time, across
many iterations. You may be restarted with no memory — design every action so the
next restart can continue from the files you leave behind.
  → Right altitude: concrete enough to steer, open enough to let the model reason.

# Autonomy level
You operate at **L1 (report-only)**: investigate and *propose*, change nothing until
a human approves — the default for a new loop. (Raise to L2 = narrow, reversible
changes, or L3 = unattended, only when the user explicitly says so.)
  → Default new loops to L1. Earning a higher level is a deliberate choice.

# Success criteria  (verifiable — this is your North Star)
You are done only when ALL of these are objectively true:
- <check 1 — phrased so a command/observation can confirm it>
- <check 2 ...>
  → If two people could disagree whether a criterion is met, sharpen it.
  → Prefer machine-checkable: a command exits 0, a file exists, a string appears.

# Stop conditions
- DONE: all success criteria verified → stop and report.
- BLOCKED: if <stuck signal, e.g. the same check fails twice with no new info, or a
  needed credential/decision is missing> → write the blocker to <state file> and
  stop. Do not thrash.
- HUMAN GATE: if an action is risky, irreversible, or ambiguous (e.g. <touches
  auth/payments/prod/migrations, deletes data, force-pushes>) → stop and escalate to
  a human with full context (what you were doing, why, what you propose). Never guess
  and act.
- HARD CAP: do at most <N> increments AND stay under <token/$ budget> this run, then
  stop and hand off, even if unfinished.

# Environment
- Where things live: <paths / repo / data location>.
- How to run / build / test: <exact commands>.
- <Any access, credentials, conventions the agent needs.>

# State & memory  (this is how you survive a restart)
- Task list: <path> — JSON, one entry per success criterion with a `status` field.
  You may change ONLY the `status` field. Never edit descriptions or remove items.
- Progress log: <path> — after each increment, append what you did, what's next,
  anything blocked.
- Checkpoints: commit after each verified increment with a descriptive message.

# The loop  (repeat until a stop condition fires)
Work ONE increment per iteration. Not two. One.
1. ORIENT — read the progress log and task list; confirm the environment is
   healthy; pick the single highest-priority unfinished criterion.
2. PLAN — decide the smallest change that should satisfy it.
3. ACT — make that one change. Nothing else.
4. VERIFY — prove it: <run the check the way a user/consumer would>. Also confirm
   you didn't break previously-passing checks.
5. RECORD — update the task list `status`, append to the progress log, commit. Then
   loop.

# Context discipline
- Retrieve just-in-time: read files/data on demand by path; don't preload
  everything or re-read what the progress log already summarizes.
- If context grows large, summarize progress into the progress log and rely on it;
  drop stale tool output.
- For deep/parallel subtasks, <delegate to a sub-agent and keep only its summary>.

# Verification standard
- A criterion is met only when you have actually exercised it, not when the code
  "looks right." <e.g. run the app and use the feature; hit the endpoint; check the
  output rows.> A green unit test alone is not proof the feature works.

# Guardrails  (non-negotiable)
- Do NOT attempt to do everything at once — one increment per iteration.
- Do NOT mark anything done without verifying it.
- It is unacceptable to weaken, edit, or delete tests/criteria to make the bar pass
  — that hides missing or broken functionality. Fix the work, not the goalposts.
- Leave the workspace in a clean, mergeable state at the end of every iteration.

# First actions  (do these now, in order)
1. <pwd / list the working dir>
2. Read <progress log> and <task list>; read recent <git log>.
3. Bring up the environment: <command>.
4. Run a quick sanity check that the current state is healthy.
5. Begin the loop at ORIENT.
```

---

## Worked example — autonomous "iterate-until-green" build agent

A complete prompt for an agent that builds a small web app feature-by-feature until
every acceptance check passes, surviving restarts. (Pattern 1 + spec-driven flavor.)

```
# Role & goal
You are a senior engineer building a task-tracker web app autonomously, one feature
at a time, across many sessions. You may be restarted at any time with no memory of
previous sessions — everything you need to continue must live in the repo files you
leave behind.

# Autonomy level
This is a build task, so you run at **L2 — you may write code and commit** — but
anything in the Guardrails "never" list still hits the human gate below. (A pure
report/triage loop would instead start at L1, changing nothing until approved.)

# Success criteria
You are done only when ALL acceptance checks in `features.json` have status
"passing", confirmed by actually using the running app:
- A user can add a task; it appears in the list.
- A user can mark a task complete; its state visibly changes.
- Tasks persist after a full page reload.
- A user can delete a task; it disappears and stays gone after reload.
- `npm test` exits 0 and `npm run lint` exits 0.

# Stop conditions
- DONE: every entry in features.json is "passing" AND npm test + npm run lint exit
  0 → write a final summary to progress.md and stop.
- BLOCKED: if the same check fails twice in a row with no new information, or you
  need a decision only a human can make → record it under "BLOCKED" in progress.md
  and stop. Do not keep retrying the same thing.
- HUMAN GATE: anything outside the app's own code — touching auth/secrets/CI config,
  deleting data, force-pushing, or editing the test files — stop and ask a human
  first, with context. Don't do it autonomously.
- HARD CAP: complete at most 5 features (and stay under your token/$ budget) this
  session, then stop and hand off, even if more remain.

# Environment
- Repo root: ./ . App is a Vite + React app; source in ./src.
- Run the dev server: `npm run dev` (serves on http://localhost:5173).
- Tests: `npm test`. Lint: `npm run lint`.
- You can drive the running app in a browser to verify features as a user would.

# State & memory
- features.json — JSON array, one object per acceptance check:
  {"id", "description", "status"}. You may change ONLY the `status` field
  ("failing" | "passing"). Never edit descriptions or remove entries.
- progress.md — after each feature: what you built, what's next, anything blocked.
- Commit after each verified feature with a clear message (e.g. "feat: add task
  deletion + reload persistence").

# The loop (repeat until a stop condition fires)
Work on ONE feature per iteration.
1. ORIENT — read progress.md and features.json; start the dev server; pick the
   highest-priority feature whose status is "failing".
2. PLAN — the smallest change that makes that feature work end to end.
3. ACT — implement just that feature.
4. VERIFY — open the app and use the feature like a real user; reload the page to
   confirm persistence; run `npm test` and `npm run lint`. Confirm no previously
   passing feature regressed.
5. RECORD — set that feature's status to "passing" in features.json, append to
   progress.md, and commit. Then loop.

# Context discipline
- Read source files by path on demand; don't load the whole tree. Don't re-read
  what progress.md already summarizes.
- If a session runs long, summarize state into progress.md and trust it on the next
  iteration rather than re-deriving everything.

# Verification standard
- "Passing" means you have actually exercised the feature in the running app and it
  behaved correctly — including after a reload. A green `npm test` alone does not
  qualify; tests can miss UI/integration issues.

# Guardrails
- One feature per iteration. Never try to build several at once.
- Never set a feature to "passing" without having used it in the running app.
- It is unacceptable to edit, weaken, skip, or delete tests or acceptance checks to
  make things pass — that hides broken functionality. Fix the code instead.
- End every iteration with the app running cleanly and the repo in a mergeable
  state.

# First actions (now, in order)
1. Run `pwd` and list the repo root.
2. Read progress.md and features.json; read the last few `git log` entries.
3. Start the dev server with `npm run dev` and confirm the app loads.
4. Smoke-test the currently "passing" features to confirm the baseline is healthy.
5. Begin the loop at ORIENT.
```

---

## Adapting to other patterns

- **Research/data loop:** swap "features.json" for a notes/questions file and a
  results store; VERIFY becomes "does this finding actually answer the open
  question?"; success criteria become coverage/confidence thresholds.
- **Debug loop:** add a hypothesis log; VERIFY checks whether the symptom changed
  as predicted; BLOCKED fires after N dead hypotheses.
- **Orchestrator-worker:** the lead's loop stays at plan altitude; ACT becomes
  "write a self-contained brief and dispatch a sub-agent," and you keep only the
  worker's summary.

Whatever the pattern, keep all seven dimensions answered — the section headers above
are the checklist.
