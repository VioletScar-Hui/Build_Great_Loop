# Harness assembly sheet

Start with `harness-core.md`. Add only components selected from
`../references/component-catalog.md`, and copy their runtime clauses from
`components/`. Do not leave headings for omitted components.

Selected component manifest:

```yaml
components:
  - id: CORE
    reason: <why>
  # - id: STATE|VERIFY|CAL|SHAKE|FLOW|CONTAIN
  #   reason: <observed trigger>
```

Assembly checks:

- Every selected component has its acceptance check instantiated.
- Dependencies and composition rules pass.
- The final prompt contains no unavailable command, tool, model, path, or budget.
- A simple one-session L1 loop normally contains CORE only.
