#!/usr/bin/env python3
"""Deterministically select harness components from declared task features."""
import json
import sys
from pathlib import Path


class InputError(Exception):
    """A concise selector input error."""


def enabled(features, name):
    return features.get(name) is True


def main():
    if len(sys.argv) != 2:
        raise InputError("usage: select_components.py FEATURES.json")
    path = Path(sys.argv[1])
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        raise InputError(f"cannot read UTF-8 features file {path}: {exc}") from exc
    try:
        features = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InputError(f"features file is malformed JSON: {path}: {exc}") from exc
    if not isinstance(features, dict):
        raise InputError(f"features file must contain a JSON object: {path}")

    selected = ["CORE"]
    if enabled(features, "stable_preferences_available") or enabled(features, "environment_facts_discoverable"):
        selected.append("PROFILE")
    if (enabled(features, "cross_runs") or enabled(features, "recovery_promised")
            or enabled(features, "large_replayable_fanout")):
        selected.append("STATE")
    if (enabled(features, "consequential_or_subjective")
            or (enabled(features, "mutates") and features.get("autonomy") in {"L2", "L3"})
            or (enabled(features, "substantial_merge_or_ship")
                and features.get("autonomy") in {"L2", "L3"})):
        selected.append("VERIFY")
    if enabled(features, "repeated_failure_class"):
        selected.append("RULES")
    if enabled(features, "plan_uncertainty_material"):
        selected.append("DEVIATIONS")
    if enabled(features, "substantial_merge_or_ship"):
        selected.append("EXPLAIN")
    if enabled(features, "fuzzy_at_scale"):
        if "VERIFY" not in selected:
            selected.append("VERIFY")
        selected.append("CAL")
    if features.get("autonomy") == "L3" or enabled(features, "recovery_promised"):
        selected.append("SHAKE")
    if enabled(features, "large_replayable_fanout"):
        selected.append("FLOW")
    if features.get("autonomy") in {"L2", "L3"}:
        selected.append("CONTAIN")
    payload = json.dumps({"components": selected}, ensure_ascii=False).encode("utf-8")
    sys.stdout.buffer.write(payload + b"\n")


if __name__ == "__main__":
    try:
        main()
    except (InputError, OSError, UnicodeError, ValueError, TypeError) as exc:
        sys.stderr.buffer.write(f"error: {exc}\n".encode("utf-8", errors="replace"))
        raise SystemExit(2)
