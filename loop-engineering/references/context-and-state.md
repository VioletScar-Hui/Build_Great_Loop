# Context & State — Deep Dive

How a loop survives context resets (dimension 4) and spends its attention budget
well (dimension 5). These are the two dimensions most often skipped, and the two
that most often decide whether a long-running loop succeeds.

---

## Why this matters

The context window is **volatile working memory**, and it degrades as it fills
(*context rot* — a gradient of declining recall, not a cliff). So a loop needs two
things: durable memory *outside* the window, and discipline about what goes *inside*
it. The guiding principle: **find the smallest set of high-signal tokens that
maximize the chance of the desired outcome.**

---

## Durable state: what to write down

The rule of thumb: **anything that must survive a reset goes to a file.** The
minimal kit:

### Progress file (`progress.md` or `claude-progress.txt`)
The handoff note between shifts. Keep it short and current:
- What's done (and verified).
- What's in flight right now.
- What's blocked, and why.
- The single next thing to do.

Update it in the **Record** beat, every iteration. Read it in **Orient**, every
iteration.

### Task list (prefer JSON)
The structured source of truth for "what counts as done."
```json
[
  { "id": 1, "description": "Users can add a task", "status": "passing" },
  { "id": 2, "description": "Tasks persist after reload", "status": "failing" }
]
```
Two reasons to prefer JSON over Markdown: the model is **less likely to silently
rewrite a JSON file**, and you can constrain it to change only one field (e.g.
`status`) — which stops it from quietly editing the goal. Spell that constraint out
in the prompt: *"You may change only the `status` field; never edit descriptions or
remove items."*

### Version control
Commit after each *verified* increment with a descriptive message. This gives you a
legible history and a way to revert a bad step. If git isn't available, snapshot the
working directory some other way.

### Crash-safety & idempotent resume
Externalized state only helps if a restart can *trust* it. A loop will eventually be
killed mid-iteration — design so that's harmless:
- **Claim before you act.** Mark the work item `in-progress` (or equivalent) *before*
  doing the work. On restart, an item still stuck `in-progress` is the tell that the
  last shift may have crashed mid-step — re-verify it rather than assuming it's done.
- **Make Record atomic.** Update state in an order that's safe if interrupted — e.g.
  append the result, *then* flip the status to `done`; or write to a temp file and
  rename. Never leave a half-written record a future Orient could mistake for
  complete.
- **Make resume idempotent.** Resuming must never double-process (check "already
  done?" before acting) and never corrupt (append-only, or status-guarded writes).
  The bar: if the process dies at *any* instant, the next run continues cleanly with
  nothing lost and nothing done twice.

### Notes / memory (for non-code or long research)
Structured note-taking generalizes the progress file: the agent writes findings,
maps, tallies, decisions to a notes file outside the window and reads them back
later. This is what lets an agent run for hours across many resets — it reconstructs
its working state from its own notes.

---

## The session-startup checklist (the Orient beat, expanded)

Every fresh shift should run a fixed startup sequence before touching anything.
A good default:
1. Confirm where you are (`pwd`, list the working dir).
2. Read the progress file and the recent git log.
3. Read the task list; pick the highest-priority unfinished item.
4. Bring the environment up (start the server / load the data / open the file).
5. Run a quick sanity check that the current state is healthy *before* building on
   it (don't build on a broken foundation).

This costs a few tokens and saves entire wasted iterations. Put it in the prompt as
an explicit "first actions" block.

---

## Spending the attention budget (context discipline)

### Just-in-time retrieval
Don't preload everything. Give the agent lightweight identifiers (file paths,
queries, URLs) and tools to pull detail on demand — like a human using a file
system instead of memorizing every document. Metadata (names, folders, timestamps)
is itself signal; let the agent use it to decide what to load. A **hybrid** is often
best: preload the few things always needed (a CLAUDE.md, the spec), retrieve the
rest.

### Keep the working set small
- Don't re-read what's already summarized in the progress file.
- Don't paste large files when a path + targeted read will do.
- Prefer tools that return high-signal slices over raw dumps.

### Compaction (when the window fills)
Summarize the trajectory into a fresh window: **preserve** architectural decisions,
unresolved bugs, key implementation details and constraints; **discard** redundant
tool outputs and resolved chatter. Tune for recall first (don't drop anything that
turns out to matter), then trim for precision. The safest, lightest form: clear old
tool results once they've been consumed — there's rarely a reason to keep a raw tool
dump in context after it's been used.

### Sub-agents for depth
When a subtask needs heavy exploration, delegate it to a sub-agent with a clean
context. It can burn tens of thousands of tokens internally and return a condensed
1–2k-token summary. The main loop keeps a clean context and only sees conclusions.
Good for: deep search, large-document analysis, parallel independent work.

---

## Matching the technique to the task

- **Compaction** — best for tasks needing lots of back-and-forth in one flow;
  keeps conversational continuity.
- **Note-taking / progress file** — best for iterative work with clear milestones;
  cheap, durable, resumable.
- **Sub-agents** — best for research/analysis with parallelizable depth.

Most real loops use **all three**: a progress file + task list as the backbone,
compaction when a single run gets long, and sub-agents for the deep dives.

---

## Putting it in the prompt

A solid state-&-context block names:
- the exact state files, their format, and the "only change field X" constraints;
- when to read (Orient) and write (Record) them;
- the startup checklist;
- one line of context discipline (retrieve just-in-time, don't re-read summarized
  material, compact/note when the window grows, delegate deep dives).
