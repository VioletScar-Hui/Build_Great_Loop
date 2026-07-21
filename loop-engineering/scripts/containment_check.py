#!/usr/bin/env python3
"""Reference policy adapter; production hosts must bind equivalent OS controls."""

import argparse
import json
import os
from pathlib import Path


def stop(reason: str) -> None:
    print("DENY", reason)
    raise SystemExit(2)


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


parser = argparse.ArgumentParser()
parser.add_argument("policy")
parser.add_argument("action")
parser.add_argument("path")
args = parser.parse_args()

policy_path = Path(args.policy).resolve(strict=True)
policy = json.loads(policy_path.read_text(encoding="utf-8"))
root_value = policy.get("root")
if not isinstance(root_value, str) or not root_value.strip():
    stop("policy root missing")

configured_root = Path(root_value)
if not configured_root.is_absolute():
    configured_root = policy_path.parent / configured_root
try:
    trusted_root = configured_root.resolve(strict=True)
except OSError:
    stop("policy root unavailable")
if not trusted_root.is_dir():
    stop("policy root is not a directory")

requested = Path(args.path)
candidate = requested if requested.is_absolute() else trusted_root / requested
lexical = Path(os.path.abspath(candidate))
if not is_within(lexical, trusted_root):
    stop("path escapes trusted root")

probe = trusted_root
for part in lexical.relative_to(trusted_root).parts:
    probe = probe / part
    if probe.is_symlink():
        stop("symlink path")

resolved = candidate.resolve(strict=False)
if not is_within(resolved, trusted_root):
    stop("path escapes trusted root")

deny_roots = []
for value in policy.get("deny_paths", []):
    deny_path = Path(value)
    if not deny_path.is_absolute():
        deny_path = trusted_root / deny_path
    deny_path = deny_path.resolve(strict=False)
    if not is_within(deny_path, trusted_root):
        stop("deny path escapes trusted root")
    deny_roots.append(deny_path)

reason = None
if policy.get("cancel_requested"):
    reason = "active cancellation"
elif args.action in policy.get("deny_actions", []):
    reason = "denied action"
elif any(resolved == denied or is_within(resolved, denied) for denied in deny_roots):
    reason = "denied path"
elif args.action not in policy.get("allow_actions", []):
    reason = "not allowlisted"

if reason:
    stop(reason)
print("ALLOW")
