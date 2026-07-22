#!/usr/bin/env python3
"""Regression tests for the suite validator's release-critical failure modes."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SUITE_ROOT = Path(__file__).resolve().parents[2]


class ValidateSuiteTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "canonical"
        shutil.copytree(SUITE_ROOT, self.root)
        self.validator = self.root / "loop-engineering/scripts/validate_suite.py"

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_validator(self):
        return subprocess.run(
            [sys.executable, self.validator], capture_output=True, text=True,
            encoding="utf-8",
        )

    def assert_controlled_failure(self, result, message):
        self.assertEqual(result.returncode, 1)
        self.assertIn("INVALID", result.stdout)
        self.assertIn(message, result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_current_suite_is_valid(self):
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), "VALID")

    def test_missing_eval_file_is_invalid(self):
        (self.root / "loop-retro/evals/evals.json").unlink()
        result = self.run_validator()
        self.assert_controlled_failure(result, "loop-retro: missing eval file")

    def test_cross_skill_markdown_reference_is_validated(self):
        skill = self.root / "loop-spec/SKILL.md"
        skill.write_text(
            skill.read_text(encoding="utf-8")
            + "\n`../loop-engineering/assets/components/not-real.md`\n",
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assert_controlled_failure(result, "broken reference")

    def test_unrelated_sibling_skill_with_broken_reference_is_ignored(self):
        unrelated = self.root / "unrelated-existing-skill/SKILL.md"
        unrelated.parent.mkdir(parents=True)
        unrelated.write_text(
            "---\nname: unrelated-existing-skill\n"
            "description: unrelated installed sibling\n---\n\n"
            "Example only: `assets/does-not-exist.md`\n",
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), "VALID")

    def test_malformed_eval_json_is_controlled(self):
        (self.root / "loop-review/evals/evals.json").write_text(
            "{not-json\n", encoding="utf-8"
        )
        result = self.run_validator()
        self.assert_controlled_failure(result, "loop-review: invalid eval file")

    def test_multilingual_pair_requires_both_languages(self):
        path = self.root / "loop-engineering/evals/multilingual-parity.json"
        data = __import__("json").loads(path.read_text(encoding="utf-8"))
        del data["pairs"][0]["variants"]["en"]
        path.write_text(__import__("json").dumps(data), encoding="utf-8")
        result = self.run_validator()
        self.assert_controlled_failure(result, "multilingual parity: pair l1-default requires zh and en")

    def test_multilingual_pair_requires_identical_invariants(self):
        path = self.root / "loop-engineering/evals/multilingual-parity.json"
        data = __import__("json").loads(path.read_text(encoding="utf-8"))
        data["pairs"][0]["variants"]["en"]["expected_invariants"] = ["different"]
        path.write_text(__import__("json").dumps(data), encoding="utf-8")
        result = self.run_validator()
        self.assert_controlled_failure(result, "multilingual parity: pair l1-default invariants differ")


if __name__ == "__main__":
    unittest.main()
