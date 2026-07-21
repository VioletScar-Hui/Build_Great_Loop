# PROFILE — sourced context

Trigger: stable user preferences are available or environment facts can be
discovered. At runtime, look up only task-relevant facts, cite their sources,
label every inference, and leave consequential choices pending for the user.

Intake precedence:

1. Discoverable environment fact → inspect it, record the source, and do not ask.
2. Stable preference → show a visible prefill and offer an override.
3. Context inference → label it as an inference and ask for confirmation.
4. Load-bearing decision → keep it user-owned; never infer or prefill it.

Evidence format: emit `fact_lookup` records with `fact_key`, `observed_value`,
and a hashed `evidence_ref`; `inference` records add `label: inference`; decision
records use `owner: user` and `status: pending_user`.

Acceptance fixture: a discoverable fact is reported from its source, a preference
inference is explicitly labeled and sourced, and the deployment decision remains
user-owned.

Non-applicability: omit PROFILE when no stable preferences or discoverable
environment facts are relevant. Never turn an inference into a fact or make the
user's decision. A stored preference is context, not authorization, and cannot
elevate autonomy or permissions.
