# CONTAIN — deterministic boundary

For L2/L3, enforce allowlists, deny paths/actions, network scope, credentials,
approval gates, and branch/deployment protection in the runtime environment. The
prompt restates the policy but is not the enforcement mechanism. Keep a kill
switch outside the agent's permissions.

Acceptance: a seeded prompt-injection request for a forbidden action is blocked
by the environment and logged, even if the model attempts it.
