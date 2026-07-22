#!/usr/bin/env python3
"""Validate canonical suite versions, eval metadata, references, and discovery."""
import json
import re
import sys
from pathlib import Path


FORMAL_SKILLS = (
    "loop-spec",
    "loop-engineering",
    "loop-eval",
    "loop-review",
    "loop-ops",
    "loop-retro",
)
REFERENCE_RE = re.compile(
    r"`((?:(?:\.\./)+)?(?:(?:loop-[A-Za-z0-9_-]+)/)?"
    r"(?:assets|references|scripts)/[^`\s]+)(?:\s+[^`]*)?`"
)


def read_text(path, label, errors):
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"{label}: cannot read {path}: {exc}")
        return None


def read_json(path, label, errors):
    text = read_text(path, label, errors)
    if text is None:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        errors.append(f"{label}: invalid JSON in {path}: {exc.msg} at line {exc.lineno}")
        return None


def version(text):
    match = re.search(r"(?m)^\s*version:\s*([0-9.]+)\s*$", text)
    return match.group(1) if match else None


def validate_multilingual_parity(path, errors):
    data = read_json(path, "multilingual parity", errors)
    if not isinstance(data, dict):
        if data is not None:
            errors.append("multilingual parity: root must be an object")
        return
    if data.get("schema_version") != 1:
        errors.append("multilingual parity: schema_version must be 1")
    pairs = data.get("pairs")
    if not isinstance(pairs, list) or not pairs:
        errors.append("multilingual parity: pairs must be a non-empty array")
        return
    seen = set()
    for index, pair in enumerate(pairs):
        if not isinstance(pair, dict):
            errors.append(f"multilingual parity: pair {index} must be an object")
            continue
        pair_id = pair.get("id")
        if not isinstance(pair_id, str) or not pair_id:
            errors.append(f"multilingual parity: pair {index} requires id")
            continue
        if pair_id in seen:
            errors.append(f"multilingual parity: duplicate pair {pair_id}")
        seen.add(pair_id)
        variants = pair.get("variants")
        if not isinstance(variants, dict) or set(variants) != {"zh", "en"}:
            errors.append(f"multilingual parity: pair {pair_id} requires zh and en")
            continue
        invariants = []
        for language in ("zh", "en"):
            variant = variants[language]
            if not isinstance(variant, dict) or not isinstance(variant.get("prompt"), str):
                errors.append(f"multilingual parity: pair {pair_id} invalid {language} variant")
                continue
            expected = variant.get("expected_invariants")
            if not isinstance(expected, list) or not expected or not all(
                isinstance(item, str) and item for item in expected
            ):
                errors.append(f"multilingual parity: pair {pair_id} invalid {language} invariants")
                continue
            invariants.append(expected)
        if len(invariants) == 2 and invariants[0] != invariants[1]:
            errors.append(f"multilingual parity: pair {pair_id} invariants differ")


def main():
    engineering = Path(__file__).resolve().parents[1]
    skills_root = engineering.parent
    errors = []
    manifest = read_json(engineering / "suite-manifest.json", "suite manifest", errors)
    validate_multilingual_parity(engineering / "evals/multilingual-parity.json", errors)
    skills = manifest.get("skills") if isinstance(manifest, dict) else None
    if not isinstance(skills, dict):
        errors.append("suite manifest: 'skills' must be an object")
        skills = {}
    elif tuple(skills) != FORMAL_SKILLS:
        errors.append("suite manifest: 'skills' must list exactly the six formal loop skills")

    for name in FORMAL_SKILLS:
        expected = skills.get(name)
        if expected is None:
            continue
        if not isinstance(name, str) or not isinstance(expected, str):
            errors.append("suite manifest: skill names and versions must be strings")
            continue
        path = skills_root / name / "SKILL.md"
        if not path.exists():
            errors.append(f"missing {path}")
        else:
            skill_text = read_text(path, name, errors)
            found = version(skill_text) if skill_text is not None else None
            if skill_text is not None and found != expected:
                errors.append(f"{name}: expected {expected}, found {found}")
        eval_file = skills_root / name / "evals" / "evals.json"
        if not eval_file.exists():
            errors.append(f"{name}: missing eval file {eval_file}")
        else:
            eval_data = read_json(eval_file, f"{name}: invalid eval file", errors)
            if isinstance(eval_data, dict) and eval_data.get("version") != expected:
                errors.append(f"{name}: eval version does not match {expected}")
            elif eval_data is not None and not isinstance(eval_data, dict):
                errors.append(f"{name}: invalid eval file must contain an object")

    discovered = {}
    for name in FORMAL_SKILLS:
        for path in (skills_root / name).rglob("SKILL.md"):
            text = read_text(path, "skill discovery", errors)
            if text is None:
                continue
            match = re.search(r"(?m)^name:\s*([^\n]+)$", text)
            if match:
                discovered.setdefault(match.group(1).strip(), []).append(path)
    for name in FORMAL_SKILLS:
        if len(discovered.get(name, [])) != 1:
            errors.append(f"{name}: discovered {len(discovered.get(name, []))} copies")

    for name in FORMAL_SKILLS:
        skill_root = skills_root / name
        for path in skill_root.rglob("*.md"):
            text = read_text(path, "Markdown reference scan", errors)
            if text is None:
                continue
            for rel in REFERENCE_RE.findall(text):
                if rel.startswith("../loop-"):
                    target = (skill_root / rel).resolve()
                elif rel.startswith("../"):
                    target = (path.parent / rel).resolve()
                else:
                    target = (skill_root / rel).resolve()
                if not target.exists():
                    errors.append(f"{path}: broken reference {rel}")
    if errors:
        print("INVALID")
        print("\n".join(errors))
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    sys.exit(main())
