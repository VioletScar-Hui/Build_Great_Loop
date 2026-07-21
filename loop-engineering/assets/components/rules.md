# RULES — tactical learning

Trigger: the same failure class has occurred repeatedly. At runtime, identify the
existing tactical rule, revise it narrowly for that failure class, and revalidate
all affected work before continuing.

Evidence format: emit a `rule_update` record with the failure class, occurrence
count, before/after rule, and hashed evidence; emit a `revalidation` record that
maps every affected item to its sourced command, check ID, checked result, and
hashed evidence file. The runtime validates and relays these results; it never
authors a passing result.

Acceptance fixture: a repeated normalized-title failure changes the applicable
tactical rule and every listed affected item has a passing revalidation result.

Non-applicability: omit RULES for a first or unrelated failure. RULES may revise
tactical rules, never human-owned success criteria; affected work must be
revalidated after any revision.
