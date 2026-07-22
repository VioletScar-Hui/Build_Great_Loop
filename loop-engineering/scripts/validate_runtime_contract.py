#!/usr/bin/env python3
"""Validate host-neutral loop runtime contracts with current adapter rules."""
import json
import re
import sys
from pathlib import Path


AUTHORITY_FIELDS = (
    "tenant_id",
    "channel_id",
    "principal_id",
    "connector_identity",
    "memory_namespace",
    "permission_snapshot_hash",
)
EVAL_FIELDS = (
    "harness_hash",
    "tool_interface_hash",
    "controller_id",
    "permission_profile_hash",
    "model_policy_hash",
    "language",
)
RESOLUTION_FIELDS = (
    "model",
    "workload",
    "effort",
    "thinking_mode",
    "max_output_reserve",
)


def require_object(value, path, errors):
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return {}
    return value


def require_fields(value, fields, path, errors):
    for field in fields:
        if field not in value or value[field] in (None, ""):
            errors.append(f"{path}.{field} is required")


def validate_execution(contract, errors):
    execution = require_object(contract.get("execution"), "execution", errors)
    actions = execution.get("tool_actions")
    if not isinstance(actions, list):
        errors.append("execution.tool_actions must be an array")
        return

    ids = set()
    side_effect_sequences = set()
    for index, raw in enumerate(actions):
        path = f"execution.tool_actions[{index}]"
        action = require_object(raw, path, errors)
        action_id = action.get("id")
        if not isinstance(action_id, str) or not action_id:
            errors.append(f"{path}.id is required")
        elif action_id in ids:
            errors.append(f"{path}.id must be unique: {action_id}")
        else:
            ids.add(action_id)

        effect_class = action.get("effect_class")
        if effect_class not in {"read_only", "side_effecting"}:
            errors.append(f"{path}.effect_class must be read_only or side_effecting")
        resources = action.get("resources")
        if not isinstance(resources, list) or not resources or not all(
            isinstance(item, str) and item for item in resources
        ):
            errors.append(f"{path}.resources must be a non-empty string array")

        if effect_class == "read_only":
            if action.get("parallel_group") and action.get("depends_on"):
                errors.append(f"{path} cannot be parallel while depends_on is non-empty")
        elif effect_class == "side_effecting":
            if action.get("parallel_group") not in (None, ""):
                errors.append(f"{path} side_effecting action cannot join a parallel group")
            sequence = action.get("sequence")
            if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
                errors.append(f"{path}.sequence must be a positive integer for side_effecting actions")
            elif sequence in side_effect_sequences:
                errors.append(f"{path}.sequence must be unique across side_effecting actions")
            else:
                side_effect_sequences.add(sequence)


def validate_authority(contract, errors):
    runtime = require_object(contract.get("authority_context"), "authority_context", errors)
    persisted = require_object(
        require_object(contract.get("state"), "state", errors).get("authority_context"),
        "state.authority_context",
        errors,
    )
    require_fields(runtime, AUTHORITY_FIELDS, "authority_context", errors)
    require_fields(persisted, AUTHORITY_FIELDS, "state.authority_context", errors)
    for field in AUTHORITY_FIELDS:
        if field in runtime and field in persisted and runtime[field] != persisted[field]:
            errors.append(
                f"state.authority_context.{field} does not match runtime authority_context"
            )


def current_claude_model(model):
    value = str(model).lower()
    if "sonnet-5" in value or "opus-4-8" in value:
        return True
    match = re.search(r"claude-(\d+)-(\d+)", value)
    return bool(match and (int(match.group(1)), int(match.group(2))) >= (4, 6))


def validate_api_contract(contract, errors):
    api = require_object(contract.get("api_contract"), "api_contract", errors)
    model = api.get("model_family")
    if not isinstance(model, str) or not model:
        errors.append("api_contract.model_family is required")
    messages = api.get("messages")
    if not isinstance(messages, list) or not messages:
        errors.append("api_contract.messages must be a non-empty array")
    if current_claude_model(model):
        final_assistant_message = bool(
            isinstance(messages, list)
            and messages
            and isinstance(messages[-1], dict)
            and messages[-1].get("role") == "assistant"
        )
        if api.get("assistant_prefill") is True or final_assistant_message:
            errors.append("current Claude models do not support final assistant prefill")


def validate_model_policy(contract, errors):
    policy = require_object(contract.get("model_policy"), "model_policy", errors)
    snapshot = policy.get("capability_snapshot")
    if not isinstance(snapshot, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", snapshot):
        errors.append("model_policy.capability_snapshot must be YYYY-MM-DD")
    requirements = require_object(
        policy.get("role_requirements"), "model_policy.role_requirements", errors
    )
    resolutions = require_object(
        policy.get("runtime_resolution"), "model_policy.runtime_resolution", errors
    )
    if not requirements:
        errors.append("model_policy.role_requirements must not be empty")
    for role, requirement in requirements.items():
        if not isinstance(requirement, str) or not requirement:
            errors.append(f"model_policy.role_requirements.{role} must be a capability label")
        resolution = require_object(
            resolutions.get(role), f"model_policy.runtime_resolution.{role}", errors
        )
        model = str(resolution.get("model", "")).lower()
        required_resolution_fields = tuple(
            field for field in RESOLUTION_FIELDS
            if not (field == "thinking_mode" and "sonnet-5" in model)
        )
        require_fields(
            resolution,
            required_resolution_fields,
            f"model_policy.runtime_resolution.{role}",
            errors,
        )
        reserve = resolution.get("max_output_reserve")
        if not isinstance(reserve, int) or isinstance(reserve, bool) or reserve < 1:
            errors.append(
                f"model_policy.runtime_resolution.{role}.max_output_reserve must be positive"
            )
        workload = resolution.get("workload")
        effort = resolution.get("effort")
        if "opus-4-8" in model and workload in {"coding", "agentic"} and effort not in {
            "xhigh", "max"
        }:
            errors.append(
                f"model_policy.runtime_resolution.{role}: opus-4-8 {workload} starts at xhigh effort"
            )
        if "sonnet-5" in model and "budget_tokens" in resolution:
            errors.append(
                f"model_policy.runtime_resolution.{role}: sonnet-5 does not use manual budget_tokens"
            )


def validate_eval_context(contract, errors):
    context = require_object(contract.get("eval_context"), "eval_context", errors)
    require_fields(context, EVAL_FIELDS, "eval_context", errors)


def week_at_least(value, year, week):
    match = re.fullmatch(r"(\d{4})-W(\d{2})", str(value))
    return bool(match and (int(match.group(1)), int(match.group(2))) >= (year, week))


def validate_host_adapter(contract, errors):
    adapter = require_object(contract.get("host_adapter"), "host_adapter", errors)
    if adapter.get("host") != "claude-code" or not week_at_least(
        adapter.get("capability_week"), 2026, 29
    ):
        return
    command = adapter.get("command")
    mode = adapter.get("session_mode")
    if command == "/fork":
        if mode != "background_session":
            errors.append("Claude Code W29+ /fork requires session_mode background_session")
        for field in ("session_id", "run_id", "lease_id", "budget_id", "cancellation_id"):
            if adapter.get(field) in (None, ""):
                errors.append(f"Claude Code W29+ /fork requires independent {field}")
    elif command == "/subtask":
        if mode != "in_session":
            errors.append("Claude Code W29+ /subtask requires session_mode in_session")


def validate_contract(contract):
    errors = []
    if not isinstance(contract, dict):
        return ["runtime contract must be an object"]
    if contract.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    validate_execution(contract, errors)
    validate_authority(contract, errors)
    validate_api_contract(contract, errors)
    validate_model_policy(contract, errors)
    validate_eval_context(contract, errors)
    validate_host_adapter(contract, errors)
    return errors


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: validate_runtime_contract.py CONTRACT.json", file=sys.stderr)
        return 2
    path = Path(args[0])
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"INVALID\n{exc}")
        return 1
    errors = validate_contract(contract)
    if errors:
        print("INVALID")
        print("\n".join(errors))
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
