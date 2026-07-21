# EXPLAIN — evidence-linked delivery comprehension

Trigger: a merge or shipment is substantial. At runtime, explain material claims
from inspectable evidence and record the comprehension result or an explicit
waiver before completing delivery.

Evidence format: emit `claim` records with delivery class, substantial flag,
claim, and hashed `evidence_ref`; emit a `comprehension_gate` record with outcome
`comprehension_recorded` or `waived`, actor, decision, reason, timestamp, action
digest, and hashed evidence. A change summary alone is not comprehension evidence.

Acceptance fixture: the substantial merge/ship summary cites build/change
evidence and records the comprehension gate outcome.

Non-applicability: omit EXPLAIN for insubstantial delivery. EXPLAIN cannot replace
verification, and substantial merge/ship work cannot silently skip comprehension.
