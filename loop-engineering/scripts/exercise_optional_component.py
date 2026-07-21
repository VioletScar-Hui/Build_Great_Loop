#!/usr/bin/env python3
"""Exercise one optional component against a hermetic evidence fixture."""
import argparse
import csv
import hashlib
import io
import json
import re
import sys
from datetime import datetime
from pathlib import Path


COMPONENTS = {"PROFILE", "RULES", "DEVIATIONS", "EXPLAIN"}


class FixtureError(Exception):
    """An actionable fixture or invocation error."""


def confined(root, relative):
    try:
        candidate = (root / relative).resolve()
    except (OSError, ValueError, TypeError) as exc:
        raise FixtureError(f"invalid confined path {relative!r}: {exc}") from exc
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise FixtureError(f"path escapes configured root: {relative}") from exc
    return candidate


def read_text(root, relative):
    path = confined(root, relative)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise FixtureError(f"cannot read required fixture {path}: {exc}") from exc
    except UnicodeError as exc:
        raise FixtureError(f"required fixture is not valid UTF-8: {path}: {exc}") from exc
    if not text.strip():
        raise FixtureError(f"required fixture is empty: {path}")
    return path, text


def read_json(root, relative):
    path, text = read_text(root, relative)
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise FixtureError(f"required fixture is malformed JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise FixtureError(f"required fixture must contain a JSON object: {path}")
    return path, value


def require_string(mapping, field, source):
    value = mapping.get(field)
    if not isinstance(value, str) or not value.strip():
        raise FixtureError(f"{source} requires non-empty string field {field!r}")
    return value


def require_bool(mapping, field, source):
    value = mapping.get(field)
    if not isinstance(value, bool):
        raise FixtureError(f"{source} requires boolean field {field!r}")
    return value


def digest(path):
    value = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                value.update(chunk)
    except OSError as exc:
        raise FixtureError(f"cannot hash evidence {path}: {exc}") from exc
    return value.hexdigest()


def evidence_ref(path, fixture_root, output_root):
    resolved = path.resolve()
    for name, root in (("fixture", fixture_root), ("output", output_root)):
        try:
            relative = resolved.relative_to(root)
        except ValueError:
            continue
        if not resolved.is_file():
            raise FixtureError(f"evidence is not a file: {resolved}")
        return {"root": name, "path": relative.as_posix(), "sha256": digest(resolved)}
    raise FixtureError(f"evidence is outside fixture/output roots: {resolved}")


def record_link(case):
    return {"case_id": case["case_id"], "run_id": case["run_id"]}


def parse_project_runtime(text):
    section = None
    values = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped[1:-1]
        elif section == "project":
            match = re.fullmatch(r'runtime\s*=\s*"([^"\r\n]+)"', stripped)
            if match:
                values.append(match.group(1))
    if len(values) != 1:
        raise FixtureError("project.toml must contain exactly one [project] runtime")
    return values[0]


def title_is_normalized(text):
    lines = text.splitlines()
    if len(lines) != 1 or not lines[0].startswith("Title: "):
        return False
    title = lines[0][len("Title: "):]
    return bool(title) and title == " ".join(title.split())


def write_output(output_root, relative, text):
    path = confined(output_root, relative)
    try:
        path.write_text(text, encoding="utf-8")
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        raise FixtureError(f"cannot write UTF-8 output {path}: {exc}") from exc
    return path


def parse_expected_rows(text):
    matches = re.findall(r"^Expected row count:\s*(\d+)\s*$", text, re.MULTILINE)
    if len(matches) != 1:
        raise FixtureError("PLAN.md must contain exactly one Expected row count")
    return int(matches[0])


def parse_csv_rows(text):
    rows = list(csv.reader(io.StringIO(text)))
    if len(rows) < 2 or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
        raise FixtureError("primary.csv must contain a header and rectangular data rows")
    return len(rows) - 1


def exercise_profile(case, fixture_root, output_root):
    profile_path, profile = read_text(fixture_root, "loop-profile.md")
    project_path, project = read_text(fixture_root, "environment/project.toml")
    requested_fact = require_string(case, "requested_fact", "case.json")
    requested_inference = require_string(case, "requested_inference", "case.json")
    decision_key = require_string(case, "decision_key", "case.json")
    report_lines = [line.split(":", 1)[1].strip() for line in profile.splitlines()
                    if line.strip().lower().startswith("- reports:")]
    if not report_lines or not report_lines[0]:
        raise FixtureError("loop-profile.md must contain a non-empty '- Reports:' preference")
    source = evidence_ref(profile_path, fixture_root, output_root)
    link = record_link(case)
    if requested_fact != "project_runtime":
        raise FixtureError(f"unsupported requested_fact: {requested_fact!r}")
    return [
        {**link, "record_type": "fact_lookup", "fact_key": requested_fact,
         "observed_value": parse_project_runtime(project),
         "evidence_ref": evidence_ref(project_path, fixture_root, output_root)},
        {**link, "record_type": "inference", "inference_key": requested_inference,
         "label": "inference", "statement": f"Prefer {report_lines[0]} for reports",
         "evidence_ref": source},
        {**link, "record_type": "decision", "decision_key": decision_key,
         "owner": "user", "status": "pending_user"},
    ]


def exercise_rules(case, fixture_root, output_root):
    rulebook_path, rulebook = read_text(fixture_root, "RULEBOOK.md")
    run_path, run_log = read_text(fixture_root, "run.log")
    failure_class = require_string(case, "failure_class", "case.json")
    affected = case.get("affected_work")
    if (not isinstance(affected, list) or not affected
            or any(not isinstance(item, str) or not item.strip() for item in affected)
            or len(affected) != len(set(affected))):
        raise FixtureError("case.json field 'affected_work' must be a non-empty list of unique strings")
    rules = [line.strip() for line in rulebook.splitlines()
             if line.strip() and not line.lstrip().startswith("#")]
    if not rules:
        raise FixtureError("RULEBOOK.md must contain at least one tactical rule")
    failures = []
    for line in run_log.splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[0] == case["run_id"] and parts[2] == "FAIL" and parts[3] == failure_class:
            failures.append(parts[1])
    if len(failures) < 2:
        raise FixtureError(
            f"run.log must contain at least two {failure_class!r} failures for run {case['run_id']!r}"
        )
    if set(failures) != set(affected) or len(failures) != len(set(failures)):
        raise FixtureError("run.log failure items must match case.json affected_work exactly once")
    revalidation_path, revalidation = read_json(fixture_root, "revalidation.json")
    for field in ("case_id", "run_id", "failure_class"):
        if revalidation.get(field) != case.get(field):
            raise FixtureError(f"revalidation.json field {field!r} must match case.json")
    source_results = revalidation.get("checks")
    if not isinstance(source_results, list) or len(source_results) != len(affected):
        raise FixtureError("revalidation.json requires one check per affected item")
    validated_results = []
    artifact_paths = []
    for result in source_results:
        if not isinstance(result, dict):
            raise FixtureError("each revalidation check must be a JSON object")
        for field in ("item_id", "command", "check_id", "artifact_path"):
            require_string(result, field, "revalidation.json check")
        canonical_path = f"affected/{result['item_id']}.txt"
        if result["artifact_path"] != canonical_path:
            raise FixtureError(
                f"artifact_path for {result['item_id']!r} must be {canonical_path!r}"
            )
        artifact_paths.append(result["artifact_path"])
        evidence_path, artifact = read_text(fixture_root, result["artifact_path"])
        status = "pass" if title_is_normalized(artifact) else "fail"
        if status != "pass":
            raise FixtureError(f"normalized-title check failed for {result['item_id']!r}")
        validated_results.append({
            "item_id": result["item_id"], "status": status,
            "command": result["command"], "check_id": result["check_id"],
            "evidence_path": result["artifact_path"],
            "evidence_ref": evidence_ref(evidence_path, fixture_root, output_root),
        })
    result_ids = [result["item_id"] for result in validated_results]
    check_ids = [result["check_id"] for result in validated_results]
    if (set(result_ids) != set(affected) or len(result_ids) != len(set(result_ids))
            or len(check_ids) != len(set(check_ids))
            or len(artifact_paths) != len(set(artifact_paths))):
        raise FixtureError(
            "revalidation must bind each affected item to unique check and artifact paths"
        )
    after_rule = f"R-02: Require normalized titles before accepting {failure_class}."
    revised_path = write_output(
        output_root, "revised-rulebook.md",
        rulebook.rstrip() + "\n\n" + after_rule + "\n",
    )
    link = record_link(case)
    return [
        {**link, "record_type": "rule_update", "failure_class": failure_class,
         "occurrence_count": len(failures), "before_rule": rules[0],
         "after_rule": after_rule,
         "evidence_ref": evidence_ref(revised_path, fixture_root, output_root),
         "failures": {"evidence_ref": evidence_ref(run_path, fixture_root, output_root)},
         "rulebook": {"evidence_ref": evidence_ref(rulebook_path, fixture_root, output_root)}},
        {**link, "record_type": "revalidation", "affected_work": affected,
         "results": validated_results,
         "evidence_ref": evidence_ref(revalidation_path, fixture_root, output_root)},
    ]


def exercise_deviations(case, fixture_root, output_root):
    plan_path, plan = read_text(fixture_root, "PLAN.md")
    observation_path, observation = read_text(fixture_root, "observation.log")
    plan_step = require_string(case, "plan_step", "case.json")
    expected = require_string(case, "expected", "case.json")
    planned_name = Path(plan_step.split()[-1]).name
    if planned_name not in plan:
        raise FixtureError(
            f"PLAN.md does not contain the input named by case plan_step: {planned_name!r}"
        )
    planned_path, csv_text = read_text(fixture_root, planned_name)
    expected_count = parse_expected_rows(plan)
    row_count = parse_csv_rows(csv_text)
    expected_text = f"{planned_name} contains {expected_count} rows"
    if expected != expected_text:
        raise FixtureError("case expected value does not match PLAN.md")
    observation_lines = [line.strip() for line in observation.splitlines() if line.strip()]
    if len(observation_lines) != 1:
        raise FixtureError("observation.log must contain exactly one structured observation")
    match = re.fullmatch(
        r"(\S+) observed (\S+) row_count=(\d+) at plan_step=(\S+)",
        observation_lines[0],
    )
    expected_step = f"{plan_step.split()[0]}-{Path(planned_name).stem}"
    if (not match or match.groups()
            != (case["run_id"], planned_name, str(row_count), expected_step)):
        raise FixtureError("observation.log does not exactly corroborate the observed row count")
    deviation_id = "deviation-001"
    link = record_link(case)
    return [{
        **link, "record_type": "deviation", "deviation_id": deviation_id,
        "plan_step": plan_step, "expected": expected,
        "expected_row_count": expected_count, "observed_row_count": row_count,
        "observed": f"{planned_name} contains {row_count} rows",
        "decision": "stop this plan step and retain the original scope",
        "retro_citation": f"{case['case_id']}:{deviation_id}",
        "evidence_ref": evidence_ref(observation_path, fixture_root, output_root),
        "plan": {"evidence_ref": evidence_ref(plan_path, fixture_root, output_root)},
        "observed_artifact": {"evidence_ref": evidence_ref(planned_path, fixture_root, output_root)},
        "corroboration": {"evidence_ref": evidence_ref(observation_path, fixture_root, output_root)},
    }]


def exercise_explain(case, fixture_root, output_root):
    report_path, report = read_json(fixture_root, "build-report.json")
    summary_path, summary = read_text(fixture_root, "change-summary.md")
    verification_path, verification = read_text(fixture_root, "verification.log")
    comprehension_path, comprehension = read_json(fixture_root, "comprehension.json")
    delivery_class = require_string(case, "delivery_class", "case.json")
    substantial = require_bool(case, "substantial", "case.json")
    build = require_string(report, "build", "build-report.json")
    if report.get("run_id") != case["run_id"]:
        raise FixtureError("build-report.json run_id must match case.json")
    if build != "pass":
        raise FixtureError("build-report.json build must be 'pass'")
    tests = report.get("tests")
    if (not isinstance(tests, dict)
            or type(tests.get("passed")) is not int or type(tests.get("failed")) is not int
            or tests["passed"] < 0 or tests["failed"] < 0):
        raise FixtureError("build-report.json requires nonnegative integer test counts")
    if tests["failed"] != 0:
        raise FixtureError("build-report.json contains failed tests")
    summary_lines = [line.strip() for line in summary.splitlines()
                     if line.strip() and not line.lstrip().startswith("#")]
    if not summary_lines:
        raise FixtureError("change-summary.md must contain a material change statement")
    verification_lines = [line.split() for line in verification.splitlines() if line.strip()]
    if (not verification_lines
            or any(len(parts) != 3 or parts[0] != case["run_id"] or parts[1] != "PASS"
                   for parts in verification_lines)):
        raise FixtureError("verification.log must contain only PASS results for the case run_id")
    for field in ("case_id", "run_id", "delivery_class", "substantial"):
        if comprehension.get(field) != case.get(field):
            raise FixtureError(f"comprehension.json field {field!r} must match case.json")
    outcome = comprehension.get("outcome")
    if outcome not in {"comprehension_recorded", "waived"}:
        raise FixtureError(
            "comprehension.json outcome must be 'comprehension_recorded' or 'waived'"
        )
    for field in ("actor", "decision", "reason", "timestamp", "action_digest"):
        require_string(comprehension, field, "comprehension.json")
    try:
        parsed_timestamp = datetime.fromisoformat(comprehension["timestamp"].replace("Z", "+00:00"))
    except ValueError as exc:
        raise FixtureError("comprehension.json timestamp must be ISO-8601") from exc
    if parsed_timestamp.tzinfo is None:
        raise FixtureError("comprehension.json timestamp must include a timezone")
    action_digest = digest(summary_path)
    if comprehension["action_digest"] != action_digest:
        raise FixtureError("comprehension.json action_digest does not match change-summary.md")
    link = record_link(case)
    return [
        {**link, "record_type": "claim", "delivery_class": delivery_class,
         "substantial": substantial,
         "claim": f"Build {build}; tests passed={tests['passed']}, failed={tests['failed']}",
         "evidence_ref": evidence_ref(report_path, fixture_root, output_root)},
        {**link, "record_type": "claim", "delivery_class": delivery_class,
         "substantial": substantial,
         "claim": f"Verification passed: {', '.join(parts[2] for parts in verification_lines)}",
         "evidence_ref": evidence_ref(verification_path, fixture_root, output_root)},
        {**link, "record_type": "comprehension_gate", "delivery_class": delivery_class,
         "substantial": substantial,
         **{field: comprehension[field] for field in
            ("outcome", "actor", "decision", "reason", "timestamp", "action_digest")},
         "evidence_ref": evidence_ref(comprehension_path, fixture_root, output_root),
         "action": {"evidence_ref": evidence_ref(summary_path, fixture_root, output_root)}},
    ]


EXERCISERS = {
    "PROFILE": exercise_profile,
    "RULES": exercise_rules,
    "DEVIATIONS": exercise_deviations,
    "EXPLAIN": exercise_explain,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", required=True, choices=sorted(COMPONENTS))
    parser.add_argument("--fixture-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    fixture_root = args.fixture_dir.resolve()
    output_root = args.output_dir.resolve()
    if not fixture_root.is_dir():
        raise FixtureError(f"fixture directory does not exist: {fixture_root}")
    if not output_root.is_dir():
        raise FixtureError(f"output directory does not exist: {output_root}")
    _, case = read_json(fixture_root, "case.json")
    for field in ("case_id", "component", "run_id"):
        require_string(case, field, "case.json")
    if case["component"] != args.component:
        raise FixtureError(
            f"case.json component {case['component']!r} does not match --component {args.component!r}"
        )
    records = EXERCISERS[args.component](case, fixture_root, output_root)
    receipt = {
        "case_id": case["case_id"],
        "component": case["component"],
        "run_id": case["run_id"],
        "records": records,
    }
    payload = json.dumps(receipt, ensure_ascii=False, sort_keys=True).encode("utf-8")
    sys.stdout.buffer.write(payload + b"\n")


if __name__ == "__main__":
    try:
        main()
    except (FixtureError, OSError, UnicodeError, ValueError, TypeError) as exc:
        sys.stderr.buffer.write(f"error: {exc}\n".encode("utf-8", errors="replace"))
        raise SystemExit(2)
