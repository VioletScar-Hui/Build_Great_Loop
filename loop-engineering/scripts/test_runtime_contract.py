#!/usr/bin/env python3
"""Tests for effect, authority, model, prefill, eval, and host contracts."""
import copy
import json
import unittest
from pathlib import Path

from validate_runtime_contract import validate_contract


FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "evals/fixtures/runtime-contract-valid.json"
)


class RuntimeContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def errors_for(self, update):
        candidate = copy.deepcopy(self.contract)
        update(candidate)
        return validate_contract(candidate)

    def test_reference_contract_is_valid(self):
        self.assertEqual(validate_contract(self.contract), [])

    def test_parallel_read_only_actions_are_allowed(self):
        actions = self.contract["execution"]["tool_actions"]
        self.assertEqual(actions[0]["parallel_group"], actions[1]["parallel_group"])
        self.assertEqual(validate_contract(self.contract), [])

    def test_side_effect_cannot_join_parallel_group(self):
        errors = self.errors_for(
            lambda value: value["execution"]["tool_actions"].append({
                "id": "write-report",
                "effect_class": "side_effecting",
                "resources": ["reports/final.md"],
                "parallel_group": "reads",
                "sequence": 1,
            })
        )
        self.assertTrue(any("side_effecting" in error and "parallel" in error for error in errors), errors)

    def test_side_effect_sequences_must_be_unique(self):
        def duplicate_sequence(value):
            value["execution"]["tool_actions"].extend([
                {"id": "write-a", "effect_class": "side_effecting", "resources": ["a"], "sequence": 1},
                {"id": "write-b", "effect_class": "side_effecting", "resources": ["b"], "sequence": 1},
            ])

        errors = self.errors_for(duplicate_sequence)
        self.assertTrue(any("sequence" in error and "unique" in error for error in errors), errors)

    def test_authority_mismatch_fails_closed(self):
        errors = self.errors_for(
            lambda value: value["state"]["authority_context"].update(
                {"channel_id": "channel-other"}
            )
        )
        self.assertTrue(any("authority_context" in error and "channel_id" in error for error in errors), errors)

    def test_current_claude_partial_assistant_prefill_is_rejected(self):
        def enable_prefill(value):
            value["api_contract"]["assistant_prefill"] = True
            value["api_contract"]["messages"][-1] = {
                "role": "assistant", "content": "{"
            }

        errors = self.errors_for(enable_prefill)
        self.assertTrue(any("assistant prefill" in error for error in errors), errors)

    def test_current_claude_final_assistant_message_is_rejected_without_flag(self):
        def append_implicit_prefill(value):
            value["api_contract"].pop("assistant_prefill", None)
            value["api_contract"]["messages"].append({
                "role": "assistant", "content": "{"
            })

        errors = self.errors_for(append_implicit_prefill)
        self.assertTrue(any("assistant prefill" in error for error in errors), errors)

    def test_profile_defaults_are_not_api_prefill(self):
        self.contract["profile_defaults"] = {"language": "zh-CN"}
        self.assertEqual(validate_contract(self.contract), [])

    def test_opus_agentic_resolution_below_xhigh_is_rejected(self):
        def lower_effort(value):
            value["model_policy"]["runtime_resolution"]["planner"] = {
                "model": "claude-opus-4-8",
                "workload": "agentic",
                "effort": "high",
                "thinking_mode": "adaptive",
                "max_output_reserve": 4096,
            }

        errors = self.errors_for(lower_effort)
        self.assertTrue(any("opus-4-8" in error and "xhigh" in error for error in errors), errors)

    def test_sonnet_five_defaults_to_adaptive_thinking(self):
        self.contract["model_policy"]["runtime_resolution"]["worker"] = {
            "model": "claude-sonnet-5",
            "workload": "tool_use",
            "effort": "medium",
            "max_output_reserve": 2048,
        }
        self.assertEqual(validate_contract(self.contract), [])

    def test_eval_context_requires_control_interface_and_permission_hashes(self):
        def remove_hash(value):
            del value["eval_context"]["tool_interface_hash"]

        errors = self.errors_for(remove_hash)
        self.assertTrue(any("tool_interface_hash" in error for error in errors), errors)

    def test_fork_background_session_requires_independent_control_ids(self):
        def remove_lease(value):
            del value["host_adapter"]["lease_id"]

        errors = self.errors_for(remove_lease)
        self.assertTrue(any("/fork" in error and "lease_id" in error for error in errors), errors)

    def test_subtask_is_in_session_not_background(self):
        def use_subtask(value):
            value["host_adapter"] = {
                "host": "claude-code",
                "capability_week": "2026-W29",
                "command": "/subtask",
                "session_mode": "in_session",
            }

        self.assertEqual(self.errors_for(use_subtask), [])


if __name__ == "__main__":
    unittest.main()
