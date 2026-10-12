"""Check paper-only execution coverage without running mathematical stages."""

from collections import Counter
import copy
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


reproducer = load("sl4_paper_scope_reproducer", "reproduce.py")
runner = load("sl4_paper_scope_runner", "verify.py")
legacy = load("sl4_paper_scope_legacy", "legacy245/run_verification.py")
EXCLUDED_COMPACT_STAGES = {
    "compact", "integral-lattices", "named-hodge", "seven-torsion", "extra-models"
}


class PaperScope(unittest.TestCase):
    def test_full_plan_covers_each_retained_legacy_check_exactly_once(self):
        registry = legacy.registry()
        tasks = reproducer.make_plan("all")
        selected = Counter(step for task in tasks for step in task.get("steps", []))
        self.assertEqual(selected, Counter({name: 1 for name in registry}))
        self.assertFalse(EXCLUDED_COMPACT_STAGES.intersection(selected))
        self.assertFalse(any(task.get("legacy_extra") for task in tasks))
        for script, _, _ in registry.values():
            with self.subTest(script=script):
                self.assertTrue((ROOT / "legacy245" / script).is_file())
                self.assertNotIn("ihs_verification", Path(script).parts)

    def test_missing_coverage_is_rejected_before_execution(self):
        coverage = json.loads((ROOT / "verification/coverage.json").read_text())
        incomplete = copy.deepcopy(coverage)
        incomplete["common_tasks"].pop()
        with patch.object(reproducer, "read_json", return_value=incomplete):
            with self.assertRaisesRegex(ValueError, "registry.*coverage plan"):
                reproducer.make_plan("all")

    def test_duplicate_coverage_is_rejected_before_execution(self):
        coverage = json.loads((ROOT / "verification/coverage.json").read_text())
        duplicate = copy.deepcopy(coverage)
        duplicate["common_tasks"].append(copy.deepcopy(duplicate["common_tasks"][0]))
        with patch.object(reproducer, "read_json", return_value=duplicate):
            with self.assertRaisesRegex(ValueError, "registry.*coverage plan"):
                reproducer.make_plan("all")

    def test_all_case_plans_use_supported_programs_and_preserve_cox_order(self):
        cases = json.loads((ROOT / "cases/index.json").read_text())["cases"]
        registry = legacy.registry()
        self.assertEqual([case["case"] for case in cases], list(range(1, 107)))
        for case in cases:
            with self.subTest(case=case["case"]):
                steps = case["legacy_steps"]
                self.assertEqual(len(steps), len(set(steps)))
                self.assertLessEqual(set(steps), set(registry))
                self.assertFalse(EXCLUDED_COMPACT_STAGES.intersection(steps))
                tasks = runner.plan(SimpleNamespace(case=case["case"], profile="portable"), cases)
                legacy_task = next(task for task in tasks if task["id"] == "legacy")
                selector = legacy_task["args"].index("--steps")
                self.assertEqual(legacy_task["args"][selector + 1].split(","), steps)
                for step in steps:
                    if step.startswith("endpoint-"):
                        number = step.removeprefix("endpoint-")
                        self.assertLess(steps.index("binding-" + number), steps.index("cox-" + number))
                        self.assertLess(steps.index("cox-" + number), steps.index(step))
                for task in tasks:
                    self.assertTrue((ROOT / task["script"]).is_file(), task["script"])
                for extension in case["extensions"]:
                    if extension.get("entrypoint"):
                        task = next(task for task in tasks if task["id"] == extension["id"])
                        self.assertEqual(task["script"], extension["entrypoint"])

    def test_optional_paper_binding_only_prepends_one_stage(self):
        without = reproducer.make_plan("all")
        with_paper = reproducer.make_plan("all", with_paper=True)
        self.assertEqual(with_paper[0], {"id": "paper-matrix-binding", "kind": "paper"})
        self.assertEqual(with_paper[1:], without)


if __name__ == "__main__":
    unittest.main()
