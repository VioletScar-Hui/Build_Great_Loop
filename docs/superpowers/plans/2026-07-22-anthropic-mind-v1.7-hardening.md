# Anthropic Mind v1.7 Loop Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement effect-aware scheduling, authority-bound state, interface-aware evals, current model/prefill policy, multilingual regression coverage, and Claude session semantics in the existing six-skill suite.

**Architecture:** Extend FLOW, STATE, CONTAIN, loop-eval, and host adapters rather than introducing new component IDs. Add one deterministic runtime-contract validator and hermetic tests so the new rules are executable, then mirror the rules into authoring, review, ops, and eval guidance.

**Tech Stack:** Markdown skills and references, JSON fixtures/schemas, Python 3 standard library `unittest`.

---

### Task 1: Runtime contract RED tests

**Files:**
- Create: `loop-engineering/scripts/test_runtime_contract.py`
- Create: `loop-engineering/evals/fixtures/runtime-contract-valid.json`

- [ ] Write unit tests for valid parallel reads, rejected parallel side effects,
  rejected authority mismatch, rejected current-model assistant prefill, valid
  role-based model policy, and W29 background-session identity requirements.
- [ ] Run `python3 loop-engineering/scripts/test_runtime_contract.py`; expect import
  or missing-file failures because the validator does not exist.

### Task 2: Runtime contract GREEN implementation

**Files:**
- Create: `loop-engineering/scripts/validate_runtime_contract.py`
- Modify: `loop-engineering/scripts/test_runtime_contract.py`

- [ ] Implement UTF-8 JSON loading and deterministic validation functions for
  effect scheduling, authority binding, API prefill, model policy, and host session
  semantics.
- [ ] Run `python3 loop-engineering/scripts/test_runtime_contract.py`; expect all
  runtime-contract tests to pass with no warnings.

### Task 3: FLOW and authority documentation

**Files:**
- Modify: `loop-engineering/references/component-catalog.md`
- Modify: `loop-engineering/references/patterns.md`
- Modify: `loop-engineering/references/checklist.md`
- Modify: `loop-engineering/assets/components/dynamic-workflow.md`
- Modify: `loop-engineering/assets/components/durable-state.md`
- Modify: `loop-engineering/assets/components/environment-containment.md`
- Modify: `loop-engineering/assets/state.schema.json`
- Modify: `loop-engineering/assets/state.example.json`

- [ ] Add effect classification and serialization acceptance rules to FLOW.
- [ ] Add authority-context fields and fail-closed mismatch rules to STATE and
  CONTAIN without creating a new component.
- [ ] Validate the example state with `python3 loop-engineering/scripts/validate_state.py loop-engineering/assets/state.example.json`.

### Task 4: Interface-aware and multilingual evals

**Files:**
- Modify: `loop-eval/SKILL.md`
- Modify: `loop-eval/assets/eval-template.md`
- Modify: `loop-eval/evals/evals.json`
- Create: `loop-engineering/evals/multilingual-parity.json`
- Modify: `loop-engineering/scripts/validate_suite.py`
- Modify: `loop-engineering/scripts/test_validate_suite.py`

- [ ] Record model policy, tool-interface hash, controller ID, permission-profile
  hash, harness hash, and language in each comparable run.
- [ ] Add paired Chinese/English safety cases with identical invariant IDs.
- [ ] Make suite validation reject malformed or unpaired multilingual cases and
  run the validator tests red then green.

### Task 5: Current model, prefill, and host-adapter guidance

**Files:**
- Create: `loop-engineering/references/runtime-adapters.md`
- Modify: `loop-engineering/SKILL.md`
- Modify: `loop-engineering/references/harness-template.md`
- Modify: `loop-review/SKILL.md`
- Modify: `loop-ops/SKILL.md`
- Modify: `loop-ops/assets/ops-plan-template.md`
- Modify: `loop-ops/references/operating-safety.md`

- [ ] Keep CORE role-based; resolve model/effort/thinking/output reserve through a
  dated runtime capability snapshot.
- [ ] Ban current-model partial assistant-turn prefill while explicitly preserving
  PROFILE preference defaults.
- [ ] Document `/fork` as a managed background session and `/subtask` as in-session
  work only in the Claude adapter section.

### Task 6: Release metadata, regression, synchronization, and publication

**Files:**
- Modify: `suite-manifest.json`
- Modify: affected skill frontmatter and eval versions
- Modify: `CHANGELOG.md` and affected per-skill changelogs
- Modify: `README.md` and `README.en.md` only by adding the new release delta

- [ ] Run runtime-contract tests, suite-validator tests, suite validation, 38
  component fixtures, 18 legacy fixtures, and state validation.
- [ ] Synchronize the six formal skills to `~/.codex/skills` and
  `~/.claude/skills`, then prove byte equality.
- [ ] Commit and push the verified changes to `VioletScar-Hui/Build_Great_Loop`.
