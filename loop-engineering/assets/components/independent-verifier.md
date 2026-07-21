# VERIFY — evidence receipt

The maker cannot mark its own item `done`. A verifier receives the criterion,
artifact reference, and allowed check, then writes:

```json
{"check":"<id>","evidence_ref":"<immutable path/hash>","result":"pass|fail|unknown","verifier_id":"<identity>","verified_at":"<ISO-8601>"}
```

`unknown` never counts as pass. A receipt without inspectable evidence is invalid.
Acceptance: a seeded plausible claim with missing evidence is rejected.
