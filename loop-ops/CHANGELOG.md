# Changelog — loop-ops

## 3.1.0 — 2026-07-22

- Bound operations, recovery, memory, and connector use to explicit authority
  context and documented Claude Code W29 background-session semantics.

## 3.0.1 — 2026-07-22

- Rejected non-positive reservations and caps.
- Made repeated reservations idempotent before capacity checks and rejected
  mismatched duplicate amounts.
- Added ledger-integrity validation, atomic replacement, and cross-platform
  sidecar locking for POSIX and Windows hosts.

## 3.0.0 — 2026-07-21

- Added the host-neutral operating layer, control-state/event schemas, quota
  controller, recurring patterns, and operational safety guidance.
