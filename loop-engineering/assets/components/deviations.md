# DEVIATIONS — plan mismatch ledger

Trigger: plan uncertainty is material. At runtime, compare the planned expectation
with observed evidence and append one citable record before deciding how to
continue.

Evidence format: each `deviation` record contains a stable `deviation_id`, plan
step, expected state, observed state, hashed `evidence_ref`, decision, and a
`retro_citation` linking the same record to its run and case.

Acceptance fixture: the planned row count differs from the observed CSV row count;
one structured observation corroborates the mismatch, and the append-style record
contains expected, observed, separate evidence references, decision, and a valid
retrospective citation.

Non-applicability: omit DEVIATIONS when plan uncertainty is immaterial. A
deviation records what changed; it is never permission to expand scope.
