#!/usr/bin/env python3
"""Hermetic release gate for adversarial-components.json (31 effect checks)."""
import csv
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
FIXTURES = ROOT / "evals/fixtures"
EVIDENCE_FIXTURES = FIXTURES / "component-evidence"
EXERCISER = SCRIPTS / "exercise_optional_component.py"
checks = []


def ok(name, value):
    checks.append((name, bool(value)))


def run_capture(*args, env=None):
    return subprocess.run(
        [str(arg) for arg in args], capture_output=True, text=True, encoding="utf-8",
        env=env,
    )


def run_checked(*args):
    result = run_capture(*args)
    if result.returncode != 0:
        command = " ".join(str(arg) for arg in args)
        stderr = result.stderr.strip() or "(no stderr)"
        stdout = result.stdout.strip() or "(no stdout)"
        raise RuntimeError(
            f"command failed with exit {result.returncode}: {command}\n"
            f"stdout: {stdout}\nstderr: {stderr}"
        )
    return result


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot read valid JSON from {path}: {exc}") from exc


def select(name):
    result = run_checked(
        sys.executable, SCRIPTS / "select_components.py", FIXTURES / f"{name}.json"
    )
    try:
        return json.loads(result.stdout)["components"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise RuntimeError(
            f"selector returned invalid JSON for fixture {name}: {result.stdout!r}"
        ) from exc


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def meaningful(value):
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return value is not None


def nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())


def project_runtime(path):
    section = None
    values = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped[1:-1]
        elif section == "project":
            match = re.fullmatch(r'runtime\s*=\s*"([^"\r\n]+)"', stripped)
            if match:
                values.append(match.group(1))
    if len(values) != 1:
        raise RuntimeError("project.toml must contain exactly one [project] runtime")
    return values[0]


def normalized_title(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) != 1 or not lines[0].startswith("Title: "):
        return False
    title = lines[0][len("Title: "):]
    return bool(title) and title == " ".join(title.split())


def expected_rows(path):
    matches = re.findall(
        r"^Expected row count:\s*(\d+)\s*$",
        path.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if len(matches) != 1:
        raise RuntimeError("PLAN.md must contain exactly one Expected row count")
    return int(matches[0])


def csv_rows(path):
    rows = list(csv.reader(io.StringIO(path.read_text(encoding="utf-8"))))
    if len(rows) < 2 or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
        raise RuntimeError("observed CSV is malformed")
    return len(rows) - 1


def structured_observation(path):
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) != 1:
        return None
    match = re.fullmatch(r"(\S+) observed (\S+) row_count=(\d+) at plan_step=(\S+)", lines[0])
    return match.groups() if match else None


def evidence_refs(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "evidence_ref":
                yield child
            else:
                yield from evidence_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from evidence_refs(child)


def evidence_ref_valid(ref, fixture_dir, output_dir):
    if not isinstance(ref, dict) or set(ref) != {"root", "path", "sha256"}:
        return False
    if not all(nonempty_string(ref.get(field)) for field in ("root", "path", "sha256")):
        return False
    if ref["root"] not in {"fixture", "output"}:
        return False
    if len(ref["sha256"]) != 64 or any(char not in "0123456789abcdef" for char in ref["sha256"].lower()):
        return False
    base = fixture_dir if ref["root"] == "fixture" else output_dir
    base = base.resolve()
    candidate = (base / ref["path"]).resolve()
    if candidate != base and base not in candidate.parents:
        return False
    return candidate.is_file() and sha256(candidate) == ref["sha256"]


def parse_receipt(stdout):
    try:
        receipt = json.loads(stdout)
    except (json.JSONDecodeError, TypeError):
        return None
    return receipt if isinstance(receipt, dict) else None


def receipt_valid(receipt, component, case, fixture_dir, output_dir):
    if not isinstance(receipt, dict):
        return False
    if not all(nonempty_string(case.get(field)) for field in ("case_id", "component", "run_id")):
        return False
    if not all(nonempty_string(receipt.get(field)) for field in ("case_id", "component", "run_id")):
        return False
    if case.get("component") != component:
        return False
    if receipt.get("component") != component or receipt.get("case_id") != case.get("case_id"):
        return False
    run_id = receipt.get("run_id")
    if run_id != case.get("run_id"):
        return False
    records = receipt.get("records")
    if not isinstance(records, list) or not records:
        return False
    if not all(
        isinstance(record, dict)
        and all(nonempty_string(record.get(field)) for field in ("case_id", "run_id", "record_type"))
        and record.get("case_id") == receipt["case_id"]
        and record.get("run_id") == run_id
        for record in records
    ):
        return False
    refs = list(evidence_refs(receipt))
    return bool(refs) and all(
        evidence_ref_valid(ref, fixture_dir, output_dir) for ref in refs
    )


def records_of(receipt, record_type):
    if not isinstance(receipt, dict) or not isinstance(receipt.get("records"), list):
        return []
    return [
        record for record in receipt["records"]
        if isinstance(record, dict) and record.get("record_type") == record_type
    ]


def has_record_evidence(record):
    return isinstance(record.get("evidence_ref"), dict)


def profile_fact_property(receipt, case, fixture_dir=None):
    expected = project_runtime(fixture_dir / "environment/project.toml") if fixture_dir else None
    return any(
        nonempty_string(case.get("requested_fact"))
        and record.get("fact_key") == case["requested_fact"]
        and nonempty_string(record.get("observed_value"))
        and (fixture_dir is None or record.get("observed_value") == expected)
        and (fixture_dir is None
             or record.get("evidence_ref", {}).get("root") == "fixture"
             and record.get("evidence_ref", {}).get("path") == "environment/project.toml")
        and has_record_evidence(record)
        for record in records_of(receipt, "fact_lookup")
    )


def profile_inference_property(receipt, case):
    return any(
        nonempty_string(case.get("requested_inference"))
        and record.get("inference_key") == case["requested_inference"]
        and record.get("label") == "inference"
        and nonempty_string(record.get("statement"))
        and has_record_evidence(record)
        for record in records_of(receipt, "inference")
    )


def profile_decision_property(receipt, case):
    return any(
        nonempty_string(case.get("decision_key"))
        and record.get("decision_key") == case["decision_key"]
        and record.get("owner") == "user"
        and record.get("status") == "pending_user"
        for record in records_of(receipt, "decision")
    )


def rules_update_property(receipt, case, fixture_dir=None, output_dir=None):
    expected_rule = f"R-02: Require normalized titles before accepting {case.get('failure_class')}."
    return any(
        nonempty_string(case.get("failure_class"))
        and record.get("failure_class") == case["failure_class"]
        and isinstance(record.get("occurrence_count"), int)
        and record["occurrence_count"] >= 2
        and nonempty_string(record.get("before_rule"))
        and nonempty_string(record.get("after_rule"))
        and record["before_rule"] != record["after_rule"]
        and (fixture_dir is None or record.get("after_rule") == expected_rule)
        and (output_dir is None
             or record.get("evidence_ref", {}).get("root") == "output"
             and record.get("evidence_ref", {}).get("path") == "revised-rulebook.md"
             and (output_dir / "revised-rulebook.md").read_text(encoding="utf-8")
             == ((fixture_dir / "RULEBOOK.md").read_text(encoding="utf-8").rstrip()
                 + "\n\n" + expected_rule + "\n"))
        and has_record_evidence(record)
        for record in records_of(receipt, "rule_update")
    )


def rules_revalidation_property(receipt, case, fixture_dir=None):
    expected = case.get("affected_work")
    if not isinstance(expected, list) or not expected or not all(nonempty_string(item) for item in expected):
        return False
    if len(expected) != len(set(expected)):
        return False
    for record in records_of(receipt, "revalidation"):
        affected = record.get("affected_work")
        results = record.get("results")
        if (not isinstance(affected, list) or not affected
                or not all(nonempty_string(item) for item in affected)
                or len(affected) != len(set(affected))
                or set(affected) != set(expected)
                or not isinstance(results, list)
                or len(results) != len(expected)):
            continue
        if not all(isinstance(result, dict)
                   and nonempty_string(result.get("item_id"))
                   and nonempty_string(result.get("status"))
                   and nonempty_string(result.get("command"))
                   and nonempty_string(result.get("check_id"))
                   and nonempty_string(result.get("evidence_path"))
                   and isinstance(result.get("evidence_ref"), dict)
                   for result in results):
            continue
        result_ids = [result["item_id"] for result in results]
        if (len(result_ids) == len(set(result_ids))
                and set(result_ids) == set(expected)
                and all(result["status"] == "pass" for result in results)
                and has_record_evidence(record)):
            if fixture_dir is None:
                return True
            source = read_json(fixture_dir / "revalidation.json")
            checks_by_item = {
                check.get("item_id"): check for check in source.get("checks", [])
                if isinstance(check, dict) and nonempty_string(check.get("item_id"))
            }
            if set(checks_by_item) != set(expected):
                continue
            artifact_paths = [check.get("artifact_path") for check in checks_by_item.values()]
            if (not all(nonempty_string(path) for path in artifact_paths)
                    or len(artifact_paths) != len(set(artifact_paths))
                    or any(check.get("artifact_path") != f"affected/{item}.txt"
                           for item, check in checks_by_item.items())):
                continue
            source_ref = record["evidence_ref"]
            if source_ref.get("root") != "fixture" or source_ref.get("path") != "revalidation.json":
                continue
            evidence_matches = True
            for result in results:
                check = checks_by_item[result["item_id"]]
                artifact_path = check.get("artifact_path")
                if (not nonempty_string(artifact_path)
                        or result.get("command") != check.get("command")
                        or result.get("check_id") != check.get("check_id")
                        or result.get("evidence_path") != artifact_path
                        or result.get("status") != (
                            "pass" if normalized_title(fixture_dir / artifact_path) else "fail"
                        )
                        or result["evidence_ref"].get("root") != "fixture"
                        or result["evidence_ref"].get("path") != artifact_path):
                    evidence_matches = False
                    break
            if not evidence_matches:
                continue
            return True
    return False


def deviation_mismatch_records(receipt, case):
    return [record for record in records_of(receipt, "deviation") if
        nonempty_string(case.get("plan_step"))
        and nonempty_string(case.get("expected"))
        and record.get("plan_step") == case["plan_step"]
        and record.get("expected") == case["expected"]
        and nonempty_string(record.get("deviation_id"))
        and nonempty_string(record.get("observed"))
        and record["expected"] != record["observed"]
        and nonempty_string(record.get("decision"))
        and has_record_evidence(record)
    ]


def deviation_mismatch_property(receipt, case, fixture_dir=None):
    if fixture_dir is None:
        return bool(deviation_mismatch_records(receipt, case))
    expected_count = expected_rows(fixture_dir / "PLAN.md")
    observed_count = csv_rows(fixture_dir / "primary.csv")
    corroborated = structured_observation(fixture_dir / "observation.log") == (
        case["run_id"], "primary.csv", str(observed_count), "read-primary"
    )
    return any(
        corroborated
        and record.get("expected_row_count") == expected_count
        and record.get("observed_row_count") == observed_count
        and record.get("expected") == f"primary.csv contains {expected_count} rows"
        and record.get("observed") == f"primary.csv contains {observed_count} rows"
        and record.get("plan", {}).get("evidence_ref", {}).get("path") == "PLAN.md"
        and record.get("observed_artifact", {}).get("evidence_ref", {}).get("path") == "primary.csv"
        and record.get("corroboration", {}).get("evidence_ref", {}).get("path") == "observation.log"
        for record in deviation_mismatch_records(receipt, case)
    )


def deviation_retro_property(receipt, case):
    return any(
        nonempty_string(record.get("retro_citation"))
        and record.get("retro_citation")
        == f"{receipt.get('case_id')}:{record.get('deviation_id')}"
        for record in deviation_mismatch_records(receipt, case)
    )


def explainer_claim_property(receipt, case, fixture_dir=None):
    report = read_json(fixture_dir / "build-report.json") if fixture_dir else None
    return any(
        nonempty_string(case.get("delivery_class"))
        and isinstance(case.get("substantial"), bool)
        and record.get("delivery_class") == case["delivery_class"]
        and record.get("substantial") is case.get("substantial")
        and (fixture_dir is None
             or report.get("run_id") == case.get("run_id")
             and report.get("build") == "pass"
             and type(report.get("tests", {}).get("passed")) is int
             and type(report.get("tests", {}).get("failed")) is int
             and report["tests"]["passed"] >= 0
             and report["tests"]["failed"] == 0
             and record.get("evidence_ref", {}).get("path") == "build-report.json")
        and nonempty_string(record.get("claim")) and has_record_evidence(record)
        for record in records_of(receipt, "claim")
    )


def explainer_gate_property(receipt, case, fixture_dir=None):
    records = [record for record in records_of(receipt, "comprehension_gate") if
        nonempty_string(case.get("delivery_class"))
        and isinstance(case.get("substantial"), bool)
        and case["substantial"] is True
        and record.get("delivery_class") == case["delivery_class"]
        and record.get("substantial") is case["substantial"]
        and record.get("outcome") in {"comprehension_recorded", "waived"}
        and all(nonempty_string(record.get(field)) for field in
                ("actor", "decision", "reason", "timestamp", "action_digest"))
        and has_record_evidence(record)
    ]
    if fixture_dir is None:
        return bool(records)
    source = read_json(fixture_dir / "comprehension.json")
    fields = ("outcome", "actor", "decision", "reason", "timestamp", "action_digest")
    return any(
        all(record.get(field) == source.get(field) for field in fields)
        and source.get("case_id") == case.get("case_id")
        and source.get("run_id") == case.get("run_id")
        and source.get("delivery_class") == case.get("delivery_class")
        and source.get("substantial") is case.get("substantial")
        and source.get("action_digest") == sha256(fixture_dir / "change-summary.md")
        and record["evidence_ref"].get("root") == "fixture"
        and record["evidence_ref"].get("path") == "comprehension.json"
        and isinstance(record.get("action"), dict)
        and isinstance(record["action"].get("evidence_ref"), dict)
        and record["action"]["evidence_ref"].get("root") == "fixture"
        and record["action"]["evidence_ref"].get("path") == "change-summary.md"
        for record in records
    )


def component_properties(component, receipt, case, fixture_dir=None, output_dir=None):
    if component == "PROFILE":
        return {
            "first": profile_fact_property(receipt, case, fixture_dir),
            "second": profile_inference_property(receipt, case),
            "third": profile_decision_property(receipt, case),
        }
    if component == "RULES":
        return {
            "first": rules_update_property(receipt, case, fixture_dir, output_dir),
            "second": rules_revalidation_property(receipt, case, fixture_dir),
        }
    if component == "DEVIATIONS":
        return {
            "first": deviation_mismatch_property(receipt, case, fixture_dir),
            "second": deviation_retro_property(receipt, case),
        }
    return {
        "first": explainer_claim_property(receipt, case, fixture_dir),
        "second": explainer_gate_property(receipt, case, fixture_dir),
    }


def exercise_component(component):
    fixture_dir = EVIDENCE_FIXTURES / component.lower()
    case = read_json(fixture_dir / "case.json")
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "output"
        output_dir.mkdir()
        environment = None
        if component == "PROFILE":
            environment = {**os.environ, "PYTHONIOENCODING": "ascii"}
        result = run_capture(
            sys.executable,
            EXERCISER,
            "--component",
            component,
            "--fixture-dir",
            fixture_dir,
            "--output-dir",
            output_dir,
            env=environment,
        )
        receipt = parse_receipt(result.stdout) if result.returncode == 0 else None
        valid = receipt_valid(receipt, component, case, fixture_dir, output_dir)
        properties = component_properties(component, receipt, case, fixture_dir, output_dir)
        return {name: valid and value for name, value in properties.items()}


def run_negative_self_tests():
    with tempfile.TemporaryDirectory() as temp_dir:
        fixture_dir = Path(temp_dir) / "fixture"
        output_dir = Path(temp_dir) / "output"
        fixture_dir.mkdir()
        output_dir.mkdir()
        source = fixture_dir / "source.log"
        source.write_text("observed evidence\n", encoding="utf-8")
        profile_case = {
            "case_id": "negative-case", "component": "PROFILE", "run_id": "negative-run",
            "requested_fact": "runtime", "requested_inference": "language", "decision_key": "target",
        }
        rules_case = {
            "case_id": "negative-case", "component": "RULES", "run_id": "negative-run",
            "failure_class": "same-failure", "affected_work": ["item-1", "item-2", "item-3"],
        }
        good_ref = {"root": "fixture", "path": "source.log", "sha256": sha256(source)}
        link = {"case_id": "negative-case", "run_id": "negative-run"}

        def receipt(component, records):
            return {"component": component, **link, "records": records}

        def reject(condition, message):
            if condition:
                raise RuntimeError(f"negative self-test failed: {message}")

        missing_ref = {"root": "fixture", "path": "missing.log", "sha256": "0" * 64}
        fabricated = receipt("PROFILE", [{**link, "record_type": "fact_lookup", "fact_key": "runtime", "observed_value": "3.12", "evidence_ref": missing_ref}])
        reject(receipt_valid(fabricated, "PROFILE", profile_case, fixture_dir, output_dir), "fabricated missing evidence_ref passed")

        reject(receipt_valid(receipt("PROFILE", []), "PROFILE", profile_case, fixture_dir, output_dir), "empty records passed")

        traversal_ref = {"root": "fixture", "path": "../source.log", "sha256": sha256(source)}
        traversal = receipt("PROFILE", [{**link, "record_type": "fact_lookup", "fact_key": "runtime", "observed_value": "3.12", "evidence_ref": traversal_ref}])
        reject(receipt_valid(traversal, "PROFILE", profile_case, fixture_dir, output_dir), "traversal evidence_ref passed")

        wrong_hash_ref = {**good_ref, "sha256": "f" * 64}
        wrong_hash = receipt("PROFILE", [{**link, "record_type": "fact_lookup", "fact_key": "runtime", "observed_value": "3.12", "evidence_ref": wrong_hash_ref}])
        reject(receipt_valid(wrong_hash, "PROFILE", profile_case, fixture_dir, output_dir), "wrong evidence hash passed")

        malformed_refs = [
            {"root": None, "path": "source.log", "sha256": sha256(source)},
            {"root": "fixture", "path": ["source.log"], "sha256": sha256(source)},
            {"root": "fixture", "path": "source.log", "sha256": 123},
        ]
        for malformed_ref in malformed_refs:
            malformed = receipt("PROFILE", [{**link, "record_type": "fact_lookup", "fact_key": "runtime", "observed_value": "3.12", "evidence_ref": malformed_ref}])
            reject(receipt_valid(malformed, "PROFILE", profile_case, fixture_dir, output_dir), "malformed evidence_ref passed")

        malformed_record = receipt("PROFILE", [42])
        reject(receipt_valid(malformed_record, "PROFILE", profile_case, fixture_dir, output_dir), "malformed record passed")
        reject(any(component_properties("PROFILE", malformed_record, profile_case).values()), "malformed record reached a property")

        mismatched = receipt("PROFILE", [{**link, "record_type": "fact_lookup", "fact_key": "wrong-fact", "observed_value": "3.12", "evidence_ref": good_ref}])
        if not receipt_valid(mismatched, "PROFILE", profile_case, fixture_dir, output_dir):
            raise RuntimeError("negative self-test setup failed: mismatched case receipt did not reach semantic validation")
        reject(profile_fact_property(mismatched, profile_case), "mismatched case content passed")

        corrupted_component_case = {**profile_case, "component": "RULES"}
        reject(
            receipt_valid(mismatched, "PROFILE", corrupted_component_case, fixture_dir, output_dir),
            "corrupted case.component passed",
        )

        valid_results = [{"item_id": item, "status": "pass"} for item in rules_case["affected_work"]]
        def revalidation(affected, results):
            return receipt("RULES", [{**link, "record_type": "revalidation", "affected_work": affected, "results": results, "evidence_ref": good_ref}])

        null_affected = revalidation(None, valid_results)
        if not receipt_valid(null_affected, "RULES", rules_case, fixture_dir, output_dir):
            raise RuntimeError("negative self-test setup failed: null affected_work receipt did not reach property validation")
        reject(rules_revalidation_property(null_affected, rules_case), "null affected_work passed")

        malformed_items = revalidation(["item-1", None, "item-3"], valid_results)
        reject(rules_revalidation_property(malformed_items, rules_case), "malformed affected item passed")
        failed = revalidation(rules_case["affected_work"], [{**result, "status": "fail"} if result["item_id"] == "item-2" else result for result in valid_results])
        missing = revalidation(rules_case["affected_work"], valid_results[:-1])
        extra = revalidation(rules_case["affected_work"], valid_results + [{"item_id": "item-4", "status": "pass"}])
        duplicate = revalidation(rules_case["affected_work"], [valid_results[0], valid_results[0], valid_results[2]])
        for bad_receipt, label in [(failed, "failed"), (missing, "missing"), (extra, "extra"), (duplicate, "duplicate")]:
            reject(rules_revalidation_property(bad_receipt, rules_case), f"{label} revalidation results passed")

        deviation_case = {
            "case_id": "negative-case", "component": "DEVIATIONS", "run_id": "negative-run",
            "plan_step": "read source", "expected": "three rows",
        }
        split_deviation = receipt("DEVIATIONS", [
            {**link, "record_type": "deviation", "deviation_id": "dev-1", "plan_step": "read source", "expected": "three rows", "observed": "two rows", "decision": "continue conservatively", "evidence_ref": good_ref},
            {**link, "record_type": "deviation", "deviation_id": "dev-2", "retro_citation": "negative-case:dev-2", "evidence_ref": good_ref},
        ])
        if not deviation_mismatch_property(split_deviation, deviation_case):
            raise RuntimeError("negative self-test setup failed: split deviation lacked a valid mismatch record")
        reject(deviation_retro_property(split_deviation, deviation_case), "split deviation records passed retro citation")

        future_profile = receipt("PROFILE", [{**link, "record_type": "intent", "message": "intends to look up facts later", "evidence_ref": good_ref}])
        explain_case = {"case_id": "negative-case", "component": "EXPLAIN", "run_id": "negative-run", "delivery_class": "merge_ship", "substantial": True}
        future_explain = receipt("EXPLAIN", [{**link, "record_type": "intent", "message": "plans to ensure every claim cites evidence later", "evidence_ref": good_ref}])
        if any(component_properties("PROFILE", future_profile, profile_case).values()) or any(
            component_properties("EXPLAIN", future_explain, explain_case).values()
        ):
            raise RuntimeError("negative self-test failed: future-tense prose passed")

    def run_variant(component, fixture_dir):
        output_dir = Path(tempfile.mkdtemp(
            prefix=f"{component.lower()}-output-", dir=fixture_dir.parent
        ))
        return run_capture(
            sys.executable, EXERCISER, "--component", component,
            "--fixture-dir", fixture_dir, "--output-dir", output_dir,
        )

    def copy_fixture(name, destination):
        shutil.copytree(EVIDENCE_FIXTURES / name, destination)
        destination.chmod(0o700)
        for path in destination.rglob("*"):
            path.chmod(0o700 if path.is_dir() else 0o600)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        profile_fixture = temp_root / "profile"
        copy_fixture("profile", profile_fixture)
        first = run_variant("PROFILE", profile_fixture)
        project_file = profile_fixture / "environment/project.toml"
        project_file.write_text(
            project_file.read_text(encoding="utf-8").replace("python3.12", "python3.13"),
            encoding="utf-8",
        )
        second = run_variant("PROFILE", profile_fixture)
        first_receipt = parse_receipt(first.stdout)
        second_receipt = parse_receipt(second.stdout)
        first_facts = records_of(first_receipt, "fact_lookup")
        second_facts = records_of(second_receipt, "fact_lookup")
        reject(
            first.returncode != 0 or second.returncode != 0
            or not first_facts or not second_facts
            or first_facts[0].get("observed_value") == second_facts[0].get("observed_value"),
            "PROFILE receipt did not change when project runtime changed",
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        rules_fixture = temp_root / "rules"
        copy_fixture("rules", rules_fixture)
        (rules_fixture / "revalidation.json").unlink(missing_ok=True)
        reject(run_variant("RULES", rules_fixture).returncode == 0,
               "RULES passed without revalidation check metadata")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        rules_fixture = temp_root / "rules"
        copy_fixture("rules", rules_fixture)
        (rules_fixture / "affected/item-001.txt").write_text(
            "Title:   Alpha   Report\n", encoding="utf-8"
        )
        reject(run_variant("RULES", rules_fixture).returncode == 0,
               "RULES trusted pass metadata over a malformed affected artifact")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        rules_fixture = temp_root / "rules"
        copy_fixture("rules", rules_fixture)
        (rules_fixture / "affected").rename(rules_fixture / "affected-missing")
        reject(run_variant("RULES", rules_fixture).returncode == 0,
               "RULES passed without the affected artifact directory")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        rules_fixture = temp_root / "rules"
        copy_fixture("rules", rules_fixture)
        (rules_fixture / "affected/item-001.txt").unlink()
        reject(run_variant("RULES", rules_fixture).returncode == 0,
               "RULES passed after deleting item-001's canonical artifact")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        rules_fixture = temp_root / "rules"
        copy_fixture("rules", rules_fixture)
        metadata_path = rules_fixture / "revalidation.json"
        metadata = read_json(metadata_path)
        metadata["checks"][0]["artifact_path"] = "affected/item-002.txt"
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
        (rules_fixture / "affected/item-001.txt").unlink()
        reject(run_variant("RULES", rules_fixture).returncode == 0,
               "RULES allowed item-001 to alias item-002's artifact")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        rules_fixture = temp_root / "rules"
        copy_fixture("rules", rules_fixture)
        metadata_path = rules_fixture / "revalidation.json"
        metadata = read_json(metadata_path)
        entries = metadata.get("checks", metadata.get("results", []))
        path_field = "artifact_path" if "checks" in metadata else "evidence_path"
        entries[0][path_field] = "affected/\u0000item.txt"
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
        invalid_path = run_variant("RULES", rules_fixture)
        reject(invalid_path.returncode != 2 or "Traceback" in invalid_path.stderr,
               "exercise did not convert an invalid evidence path to a concise exit-2 error")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        explain_fixture = temp_root / "explain"
        copy_fixture("explain", explain_fixture)
        (explain_fixture / "comprehension.json").unlink(missing_ok=True)
        reject(run_variant("EXPLAIN", explain_fixture).returncode == 0,
               "EXPLAIN passed without comprehension or waiver evidence")

    for outcome, decision in (("comprehension_recorded", "understood"), ("waived", "waive")):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            explain_fixture = temp_root / "explain"
            copy_fixture("explain", explain_fixture)
            fabricated = {
                "case_id": "explain-case-001",
                "run_id": "explain-run-001",
                "delivery_class": "merge_ship",
                "substantial": True,
                "outcome": outcome,
                "actor": "fixture-reviewer",
                "decision": decision,
                "reason": "reviewed the delivery",
                "timestamp": "2026-07-21T09:00:00Z",
                "action_digest": "0" * 64,
            }
            (explain_fixture / "comprehension.json").write_text(
                json.dumps(fabricated, ensure_ascii=False), encoding="utf-8"
            )
            reject(run_variant("EXPLAIN", explain_fixture).returncode == 0,
                   f"EXPLAIN passed fabricated {outcome} evidence")

    invalid_builds = [
        {"run_id": "wrong-run", "build": "pass", "tests": {"passed": 27, "failed": 0}},
        {"run_id": "explain-run-001", "build": "fail", "tests": {"passed": 27, "failed": 0}},
        {"run_id": "explain-run-001", "build": "pass", "tests": {"passed": -1, "failed": 0}},
        {"run_id": "explain-run-001", "build": "pass", "tests": {"passed": True, "failed": 0}},
        {"run_id": "explain-run-001", "build": "pass", "tests": {"passed": 27, "failed": 1}},
    ]
    for invalid_build in invalid_builds:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            explain_fixture = temp_root / "explain"
            copy_fixture("explain", explain_fixture)
            (explain_fixture / "build-report.json").write_text(
                json.dumps(invalid_build), encoding="utf-8"
            )
            reject(run_variant("EXPLAIN", explain_fixture).returncode == 0,
                   f"EXPLAIN passed invalid build report {invalid_build!r}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        deviation_fixture = temp_root / "deviations"
        copy_fixture("deviations", deviation_fixture)
        deviation_case_path = deviation_fixture / "case.json"
        deviation_case = read_json(deviation_case_path)
        deviation_case["expected"] = "primary.csv contains 2 rows"
        deviation_case_path.write_text(json.dumps(deviation_case), encoding="utf-8")
        reject(run_variant("DEVIATIONS", deviation_fixture).returncode == 0,
               "DEVIATIONS trusted case expected value over the plan")

    for relative, replacement in (
        ("primary.csv", "id,value\n1,alpha\n2,beta\n3,gamma\n"),
        ("observation.log", "deviations-run-001 observed primary.csv row_count=9 at plan_step=read-primary\n"),
        ("observation.log",
         "deviations-run-001 observed primary.csv row_count=2 at plan_step=read-primary\n"
         "deviations-run-001 observed primary.csv row_count=9 at plan_step=read-primary\n"),
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            deviation_fixture = temp_root / "deviations"
            copy_fixture("deviations", deviation_fixture)
            (deviation_fixture / relative).write_text(replacement, encoding="utf-8")
            reject(run_variant("DEVIATIONS", deviation_fixture).returncode == 0,
                   f"DEVIATIONS passed inconsistent corroboration after mutating {relative}")

    selector = SCRIPTS / "select_components.py"
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        absent = temp_root / "absent.json"
        absent.write_text("{}", encoding="utf-8")
        falseish = temp_root / "falseish.json"
        falseish.write_text(json.dumps({
            "autonomy": "L1",
            "stable_preferences_available": "false",
            "environment_facts_discoverable": 0,
            "repeated_failure_class": "false",
            "plan_uncertainty_material": [],
            "substantial_merge_or_ship": None,
        }), encoding="utf-8")
        for fixture in (absent, falseish):
            result = run_capture(sys.executable, selector, fixture)
            reject(result.returncode != 0 or parse_receipt(result.stdout) != {"components": ["CORE"]},
                   f"selector false-trigger near-miss passed: {fixture.name}")
        malformed = temp_root / "malformed.json"
        malformed.write_text("{not-json", encoding="utf-8")
        non_object = temp_root / "list.json"
        non_object.write_text("[]", encoding="utf-8")
        for args in ((), (malformed,), (non_object,)):
            result = run_capture(sys.executable, selector, *args)
            reject(result.returncode != 2 or "Traceback" in result.stderr,
                   f"selector did not reject invalid input concisely: {args!r}")

    expected_selections = {
        "profile": ["CORE", "PROFILE"],
        "repeated-failure": ["CORE", "VERIFY", "RULES", "CONTAIN"],
        "deviations": ["CORE", "STATE", "DEVIATIONS"],
        "explainer": ["CORE", "VERIFY", "EXPLAIN", "CONTAIN"],
        "simple": ["CORE"],
    }
    for name, expected in expected_selections.items():
        actual = select(name)
        if actual != expected:
            raise RuntimeError(f"selector order mismatch for {name}: {actual!r} != {expected!r}")


def finish():
    failed = [name for name, value in checks if not value]
    print(
        json.dumps(
            {"passed": len(checks) - len(failed), "total": len(checks), "failed": failed},
            ensure_ascii=False,
        )
    )
    raise SystemExit(bool(failed))


run_negative_self_tests()

core = (ROOT / "assets/harness-core.md").read_text(encoding="utf-8")
ok("core manifest", "- id: CORE" in core)
ok(
    "core omits optional sections",
    not any(
        section in core
        for section in ["# State & memory", "# Calibration", "# Shakedown", "# Optional specialist"]
    ),
)
ok(
    "core enforceable proxy",
    "iterations/tool calls/wall" in core and "observed metrics" in core,
)
ok("recovery selects STATE", "STATE" in select("recovery"))
with tempfile.TemporaryDirectory() as temp_dir:
    state = Path(temp_dir) / "state.json"
    shutil.copyfile(ROOT / "assets/state.example.json", state)
    claim = run_checked(
        sys.executable, SCRIPTS / "state_transition.py", state, "claim", "item-1", "--run-id", "fixture"
    )
    claimed = read_json(state)["items"][0]
    ok(
        "claim before effect with key",
        claim.returncode == 0 and claimed["status"] == "in_progress" and claimed["idempotency_key"],
    )
    first_reconcile = run_checked(
        sys.executable, SCRIPTS / "state_transition.py", state, "reconcile", "item-1"
    )
    run_checked(
        sys.executable,
        SCRIPTS / "state_transition.py",
        state,
        "effect",
        "item-1",
        "--output-ref",
        "sha256:output",
    )
    second_reconcile = run_checked(
        sys.executable, SCRIPTS / "state_transition.py", state, "reconcile", "item-1"
    )
    ok(
        "reconcile before retry",
        "SAME_IDEMPOTENCY_KEY" in first_reconcile.stdout
        and "VERIFY_EXISTING_EFFECT" in second_reconcile.stdout,
    )
    done = run_checked(
        sys.executable,
        SCRIPTS / "state_transition.py",
        state,
        "complete",
        "item-1",
        "--receipt",
        FIXTURES / "pass-receipt.json",
    )
    ok(
        "done requires receipt",
        done.returncode == 0 and read_json(state)["items"][0]["verification"]["evidence_ref"],
    )
    bad = Path(temp_dir) / "bad.json"
    shutil.copyfile(ROOT / "assets/state.example.json", bad)
    bad_data = read_json(bad)
    bad_data["items"][0]["status"] = "done"
    bad.write_text(json.dumps(bad_data), encoding="utf-8")
    rejection = run_capture(sys.executable, SCRIPTS / "validate_state.py", bad)
    ok("verifier no evidence rejected", rejection.returncode != 0)
    ok("no evidence cannot be done", "EVIDENCE" in rejection.stderr.upper())
ok("l3 selects CONTAIN", "CONTAIN" in select("l3"))
containment = (ROOT / "assets/components/environment-containment.md").read_text(encoding="utf-8")
ok("prompt-only rejected", "not the enforcement mechanism" in containment)
denial = run_capture(
    sys.executable, SCRIPTS / "containment_check.py", FIXTURES / "containment.json", "deploy", "prod/app"
)
cancellation = run_capture(
    sys.executable, SCRIPTS / "containment_check.py", FIXTURES / "canceled.json", "read", "safe/file"
)
ok("seeded denial and cancellation", denial.returncode == 2 and cancellation.returncode == 2)
fanout = select("fanout")
ok("fanout selects FLOW STATE", "FLOW" in fanout and "STATE" in fanout)
workflow = run_checked(
    sys.executable, SCRIPTS / "build_workflow.py", FIXTURES / "work-items.json", "--batch-size", "2"
)
graph = json.loads(workflow.stdout)
ok("executable workflow", graph["queue_size"] == 3)
ok(
    "bounded main context",
    graph["max_context_items"] == 2
    and all(len(node["items"]) <= 2 for node in graph["nodes"]),
)
skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
ok("no invented usage", "Never invent" in skill)
with tempfile.TemporaryDirectory() as temp_dir:
    quota = Path(temp_dir) / "quota.json"
    first_quota = run_checked(
        sys.executable, ROOT.parent / "loop-ops/scripts/quota_ledger.py", quota, "r1", "3", "--max", "5"
    )
    second_quota = run_capture(
        sys.executable, ROOT.parent / "loop-ops/scripts/quota_ledger.py", quota, "r2", "3", "--max", "5"
    )
    ok("enforceable quota", first_quota.returncode == 0 and second_quota.returncode == 2)
ok("token cost observed", "observed\nmetrics or placeholders" in skill)

if "--legacy" in sys.argv[1:]:
    finish()

traversal_denial = run_capture(
    sys.executable,
    SCRIPTS / "containment_check.py",
    FIXTURES / "containment.json",
    "read",
    "safe/../prod/app",
)
root_escape = run_capture(
    sys.executable,
    SCRIPTS / "containment_check.py",
    FIXTURES / "containment.json",
    "read",
    "../outside",
)
ok("containment normalizes traversal aliases", traversal_denial.returncode == 2)
ok("containment blocks root escape", root_escape.returncode == 2)
with tempfile.TemporaryDirectory() as temp_dir:
    temp = Path(temp_dir)
    root = temp / "root"
    outside = temp / "outside"
    root.mkdir()
    outside.mkdir()
    (root / "linked").symlink_to(outside, target_is_directory=True)
    policy = temp / "policy.json"
    policy.write_text(
        json.dumps(
            {
                "root": str(root),
                "allow_actions": ["read"],
                "deny_actions": [],
                "deny_paths": [],
                "cancel_requested": False,
            }
        ),
        encoding="utf-8",
    )
    symlink_escape = run_capture(
        sys.executable, SCRIPTS / "containment_check.py", policy, "read", "linked/file"
    )
    ok("containment rejects symlink paths", symlink_escape.returncode == 2)

with tempfile.TemporaryDirectory() as temp_dir:
    quota = Path(temp_dir) / "quota.json"
    quota_script = ROOT.parent / "loop-ops/scripts/quota_ledger.py"
    negative = run_capture(
        sys.executable, quota_script, quota, "negative", "-1", "--max", "5"
    )
    zero = run_capture(sys.executable, quota_script, quota, "zero", "0", "--max", "5")
    zero_max = run_capture(
        sys.executable, quota_script, quota, "bad-max", "1", "--max", "0"
    )
    ok(
        "quota rejects non-positive values",
        negative.returncode == 2 and zero.returncode == 2 and zero_max.returncode == 2,
    )
    first = run_capture(sys.executable, quota_script, quota, "same", "3", "--max", "3")
    retry = run_capture(sys.executable, quota_script, quota, "same", "3", "--max", "2")
    mismatch = run_capture(sys.executable, quota_script, quota, "same", "2", "--max", "3")
    overflow = run_capture(sys.executable, quota_script, quota, "other", "1", "--max", "3")
    ok("quota retry is idempotent before cap check", first.returncode == 0 and retry.returncode == 0)
    ok("quota rejects mismatched duplicate", mismatch.returncode == 2)
    ok("quota cap remains enforceable", overflow.returncode == 2)

profile = exercise_component("PROFILE")
ok("profile selects PROFILE", "PROFILE" in select("profile"))
ok("profile looks up facts", profile["first"])
ok("profile labels inferences", profile["second"])
ok("profile keeps decisions user-owned", profile["third"])

rules = exercise_component("RULES")
ok("repeated failure selects RULES", "RULES" in select("repeated-failure"))
ok("repeated failure updates tactical rule", rules["first"])
ok("rules revalidate affected work", rules["second"])

deviations = exercise_component("DEVIATIONS")
ok("deviations selects DEVIATIONS", "DEVIATIONS" in select("deviations"))
ok("deviation records mismatch", deviations["first"])
ok("retro cites deviation", deviations["second"])

explain = exercise_component("EXPLAIN")
ok("explainer selects EXPLAIN", "EXPLAIN" in select("explainer"))
ok("explainer claims cite evidence", explain["first"])
ok("merge ship comprehension gate", explain["second"])
finish()
