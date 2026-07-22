# Anthropic Mind v1.7 Loop Hardening Design

## Goal

Absorb the seven relevant Anthropic Mind v1.7 updates without adding new harness
components or making host-specific behavior part of CORE.

## Architecture

Strengthen four existing surfaces:

1. `FLOW` owns effect-aware scheduling: independent reads may run in parallel;
   side effects and shared-state operations are serialized.
2. `STATE` and `CONTAIN` own authority binding: durable state, memory, credentials,
   and events carry the same tenant/channel/principal namespace and fail closed on
   mismatch.
3. `loop-eval` treats the control interface, permission profile, model/effort
   resolution, and language as first-class eval variables.
4. Host adapters own current Claude behavior: model effort defaults, removal of
   assistant-turn prefill, and `/fork` versus `/subtask` semantics.

The deterministic boundary is a runtime-contract validator. Documentation tells
the authoring skills when to emit the contract; fixtures prove that invalid
parallel writes, authority drift, obsolete prefill, and stale host semantics are
rejected.

## Required behavior

- A tool action declares `read_only` or `side_effecting` and the resources it
  touches. Only independent read-only actions may share a parallel group.
- Side effects use a unique ordered sequence; shared resources cannot be mutated
  at the same sequence.
- Persisted state and runtime authority match on tenant, channel, principal,
  connector identity, memory namespace, and permission snapshot hash.
- Eval records include hashes/identifiers for the tool interface, controller, and
  permission profile, in addition to the existing skill/fixture/runner/grader
  hashes.
- API contracts reject a final partial assistant prefill for current Claude
  models. PROFILE's user-visible preference defaults remain valid and are named
  separately.
- Model policy stays role-based and host-neutral in CORE; adapters resolve model,
  effort, thinking mode, and output reserve from a dated capability snapshot.
- Safety and routing evals include paired Chinese/English cases with identical
  behavioral invariants.
- Claude Code W29+ maps `/fork` to a separately managed background session and
  `/subtask` to in-session work. Background sessions require independent run,
  lease, budget, and cancellation identities.

## Non-goals

- No new optional component ID.
- No mandatory Claude model or command in CORE.
- No claim that translated wording must be identical; multilingual eval compares
  decisions and safety invariants.
- No production scheduler or identity provider implementation.

## Verification

The release gate requires red/green unit tests for the runtime validator, existing
38 component assertions and 18 legacy assertions, suite validation, multilingual
fixture validation, and byte-identical Codex/Claude installed copies.
