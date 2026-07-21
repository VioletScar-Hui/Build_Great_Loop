#!/usr/bin/env python3
"""Dependency-free semantic checks for loop state (schema is also provided)."""
import json
import sys
from pathlib import Path


def fail(message):
    print(f"INVALID: {message}", file=sys.stderr)
    raise SystemExit(1)


def main():
    if len(sys.argv) != 2:
        fail("usage: validate_state.py STATE.json")
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    required = {"schema_version", "loop_id", "goal_digest", "run_id", "items", "budget"}
    missing = required - data.keys()
    if missing:
        fail(f"missing top-level fields: {sorted(missing)}")
    if data["schema_version"] != "1.0":
        fail("unsupported schema_version")
    ids = [item.get("id") for item in data["items"]]
    if None in ids or len(ids) != len(set(ids)):
        fail("item ids must be present and unique")
    for item in data["items"]:
        status = item.get("status")
        if status not in {"pending", "in_progress", "done", "blocked"}:
            fail(f"{item.get('id')}: invalid status")
        if status == "in_progress" and not (item.get("claim") and item.get("idempotency_key")):
            fail(f"{item['id']}: in_progress requires claim and idempotency_key")
        if status == "done":
            receipt = item.get("verification") or {}
            if not item.get("output_ref") or receipt.get("result") != "pass" or not receipt.get("evidence_ref"):
                fail(f"{item['id']}: done requires output_ref and passing evidence receipt")
    budget = data["budget"]
    if budget.get("increments_max", 0) < 1 or budget.get("increments_used", -1) < 0:
        fail("invalid increment budget")
    if budget["increments_used"] > budget["increments_max"]:
        fail("hard cap exceeded")
    print("VALID")


if __name__ == "__main__":
    main()
