#!/usr/bin/env python3
"""Regression tests for authority-bound STATE transitions."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Dict, Optional, Tuple


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "loop-engineering" / "scripts" / "state_transition.py"
EXAMPLE = ROOT / "loop-engineering" / "assets" / "state.example.json"


def claim(
    state: Dict, run_id: Optional[str]
) -> Tuple[subprocess.CompletedProcess, Dict]:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "state.json"
        path.write_text(json.dumps(state), encoding="utf-8")
        command = ["python3", str(SCRIPT), str(path), "claim", "item-1"]
        if run_id is not None:
            command.extend(["--run-id", run_id])
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        return result, json.loads(path.read_text(encoding="utf-8"))


class StateTransitionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_claim_requires_run_id(self) -> None:
        result, state = claim(self.state, None)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("RUN ID REQUIRED", result.stderr + result.stdout)
        self.assertEqual(state["items"][0]["status"], "pending")

    def test_idempotency_key_is_bound_to_authority_context(self) -> None:
        other = json.loads(json.dumps(self.state))
        other["authority_context"]["channel_id"] = "channel-other"
        other["authority_context"]["memory_namespace"] = (
            "tenant-example/channel-other/loop-agent-example"
        )

        first_result, first = claim(self.state, "run-a")
        second_result, second = claim(other, "run-a")

        self.assertEqual(first_result.returncode, 0, first_result.stderr)
        self.assertEqual(second_result.returncode, 0, second_result.stderr)
        self.assertNotEqual(
            first["items"][0]["idempotency_key"],
            second["items"][0]["idempotency_key"],
        )

    def test_claim_records_authority_digest(self) -> None:
        result, state = claim(self.state, "run-a")
        self.assertEqual(result.returncode, 0, result.stderr)
        claim_data = state["items"][0]["claim"]
        self.assertEqual(claim_data["run_id"], "run-a")
        self.assertRegex(claim_data["authority_digest"], r"^sha256:[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main(verbosity=2)
