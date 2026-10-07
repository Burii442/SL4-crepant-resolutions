"""Exact age-profile regressions on four small groups and corrupted inputs.

The full 106-case calculation is a separate CI step. These tests target
mathematical edge cases and failures that a stored catalogue might conceal.
"""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "tools/verify_age_profiles.py"
spec = importlib.util.spec_from_file_location("sl4_age_profile_tests", VERIFIER)
age = importlib.util.module_from_spec(spec)
spec.loader.exec_module(age)
CATALOGUE = json.loads(age.DEFAULT_CATALOGUE.read_text())


class AgeProfiles(unittest.TestCase):
    def row(self, case):
        return copy.deepcopy(CATALOGUE[case - 1])

    def test_trivial_group_has_only_identity_and_full_fixed_space(self):
        profile = age.compute_profile(self.row(1))
        self.assertEqual(profile["age_counts"], {"0": 1, "1": 0, "2": 0})
        self.assertEqual(profile["class_count"], 1)
        self.assertEqual(profile["class_sizes_by_age"], {"0": [1], "1": [], "2": []})
        self.assertEqual(profile["fixed_dimension"], 4)
        self.assertEqual(profile["junior_generated_order"], 1)
        self.assertTrue(profile["generated_by_juniors"])
        self.assertTrue(profile["abelian"])

    def test_scalar_minus_identity_has_age_two_and_no_juniors(self):
        profile = age.compute_profile(self.row(2))
        self.assertEqual(profile["group_order"], 2)
        self.assertEqual(profile["age_counts"], {"0": 1, "1": 0, "2": 1})
        self.assertEqual(profile["class_count"], 2)
        self.assertEqual(profile["fixed_dimension"], 0)
        self.assertEqual(profile["junior_generated_order"], 1)
        self.assertFalse(profile["generated_by_juniors"])
        self.assertTrue(profile["abelian"])

    def test_junior_generation_does_not_imply_a_positive_geometric_decision(self):
        row = self.row(45)
        self.assertEqual(row["decision"], "NO")
        profile = age.compute_profile(row)
        self.assertEqual(profile["age_counts"], {"0": 1, "1": 4, "2": 7})
        self.assertEqual(profile["class_count"], 12)
        self.assertEqual(profile["group_order"], 36)
        self.assertEqual(profile["junior_generated_order"], 36)
        self.assertTrue(profile["generated_by_juniors"])
        self.assertFalse(profile["abelian"])
        self.assertNotIn("decision", profile)

    def test_positive_nonabelian_case_35_has_correct_conjugacy_class_sizes(self):
        row = self.row(35)
        self.assertEqual(row["decision"], "YES")
        profile = age.compute_profile(row)
        self.assertEqual(profile["age_counts"], {"0": 1, "1": 2, "2": 4})
        self.assertEqual(profile["class_sizes_by_age"],
                         {"0": [1], "1": [4, 4], "2": [1, 2, 2, 2]})
        self.assertEqual(profile["class_count"], 7)
        self.assertEqual(profile["group_order"], 16)
        self.assertEqual(profile["junior_generated_order"], 16)
        self.assertTrue(profile["generated_by_juniors"])
        self.assertFalse(profile["abelian"])
        self.assertEqual(profile["fixed_dimension"], 0)

    def test_corrupted_stored_age_counts_are_rejected(self):
        for key in ("junior_classes", "age2_classes"):
            with self.subTest(field=key):
                row = self.row(2)
                row[key] += 1
                with self.assertRaisesRegex(ValueError, "computed .* recorded"):
                    age.compute_profile(row)

    def test_corrupted_spectral_polynomial_is_rejected(self):
        row = self.row(2)
        row["characteristic_polynomial_distribution"][1][0][1] = 3
        with self.assertRaisesRegex(ValueError, "spectral counts differ"):
            age.compute_profile(row)

    def test_determinant_minus_one_generator_is_rejected(self):
        row = self.row(2)
        row["actual_generators"][0][0][0] = 1
        with self.assertRaises(AssertionError):
            age.compute_profile(row)

    def test_both_underestimated_and_overestimated_orders_are_rejected(self):
        for order in (1, 3):
            with self.subTest(order=order):
                row = self.row(2)
                row["order"] = order
                with self.assertRaises(AssertionError):
                    age.compute_profile(row)

    def test_optimized_python_is_refused_before_checking(self):
        result = subprocess.run(
            [sys.executable, "-B", "-O", str(VERIFIER), "--case", "1"],
            cwd=ROOT, text=True, capture_output=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Run without -O", result.stderr)
        self.assertNotIn('"status": "PASS"', result.stdout)


if __name__ == "__main__":
    unittest.main()
