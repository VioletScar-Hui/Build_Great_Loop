# CONTAIN — deterministic boundary

For L2/L3, enforce allowlists, deny paths/actions, network scope, credentials,
approval gates, and branch/deployment protection in the runtime environment. The
prompt restates the policy but is not the enforcement mechanism. Keep a kill
switch outside the agent's permissions.

Resolve a concrete authority context before any tool call. Credentials, connector
identity, data visibility, memory namespace, and event ownership must all match
that context. Missing or changed tenant/channel/principal/permission snapshots
fail closed; channel visibility never implies connector-data authority.

Acceptance: a seeded prompt-injection request for a forbidden action is blocked
by the environment and logged, even if the model attempts it. A second seed using
another channel/principal cannot read the first seed's memory or reuse its token.
