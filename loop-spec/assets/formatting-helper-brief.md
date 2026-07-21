# Optional formatting helper — reusable brief

Use this helper when formatting would flood the main context or the same task
recurs. Choose the cheapest capable model and a delegation mechanism available in
the current environment; do not hard-code either. Paste this brief, filling <...>:

```
You are the formatting helper for a loop project. Using ONLY the interview
conclusions below (do not invent, do not embellish), write/update these files in
<docs dir, default ./loop-docs/>, following the given templates exactly:

- SPEC.md       ← template: <paste or path>
- STANDARDS.md  ← template: <...>
- GOALS.md      ← template: <...>
- PLAN.md       ← template: <...> (skeleton only unless plan content provided)

Interview conclusions (verbatim):
<framing / decisions / standards / goal tree / open questions>

Rules: preserve the user's wording for decisions; every standard keeps its check
command; goal-tree leaves keep accept/deps/status fields; if something is missing
from the conclusions, leave the template placeholder and list it at the end under
"MISSING" — never fill gaps yourself. Reply with the file list you wrote + the
MISSING list.
```

Main agent then reviews the files against the interview, fixes drift, and shows
the user a summary for sign-off. During the loop's execution, invoke the same
formatting capability to keep PLAN.md and status fields current (Record beat).

## Optional persistence (reusable across sessions)

If the environment supports reusable helper capabilities, register this brief
through that capability. Do not require a host-specific path, role format, model,
or tool name. Persist it only if the role is repeatedly useful across sessions.
