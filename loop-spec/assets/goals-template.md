# GOALS — <task name>

> The user-approved goal tree from Phase 3. Leaf granularity: one loop increment,
> independently verifiable, ≤1 dependency. The loop may flip `status` only —
> never edit descriptions, add, or remove nodes. Structure changes are human-only.

## Goal tree

- **G — <the one-sentence goal>**
  - **G1 — <sub-goal>**
    - [ ] G1.1 <leaf task> · accept: <which STANDARDS check> · deps: none · status: pending
    - [ ] G1.2 <leaf task> · accept: <check> · deps: G1.1 · status: pending
  - **G2 — <sub-goal>**
    - [ ] G2.1 <leaf task> · accept: <check> · deps: none · status: pending

Legal `status`: pending | in_progress | done | blocked

## Leaf count & order
- Total leaves: <N> · Suggested execution order: <G1.1 → G1.2 → G2.1 …>
- User approved this tree on: <date>
