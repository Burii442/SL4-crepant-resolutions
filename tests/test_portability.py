"""Small executable-selection regressions; no Sage or algebra run is needed."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT/relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runner = load('sl4_portability_runner', 'verify.py')
executables = load('sl4_endpoint_executables', 'legacy245/endpoint_verification/executables.py')


class GapForwarding(unittest.TestCase):
    def test_all_passes_selected_gap_to_e_without_invalid_f_argument(self):
        tasks = {t['id']: t for t in runner.plan(SimpleNamespace(case=None, profile='all'), [])}
        self.assertEqual(tasks['sieve-e']['args'][:2], ['--gap', '{gap}'])
        # F contains no standalone GAP computation and accepts no --gap flag.
        self.assertNotIn('--gap', tasks['sieve-f']['args'])

    def test_individual_e_case_passes_gap_too(self):
        cases = json.loads((ROOT/'cases/index.json').read_text())['cases']
        tasks = runner.plan(SimpleNamespace(case=100, profile='portable'), cases)
        e = next(t for t in tasks if t['id'] == 'sieve-e')
        self.assertEqual(e['args'][:2], ['--gap', '{gap}'])
        value = '/a directory/custom-gap-name'
        self.assertEqual(e['args'][1].format(gap=value), value)

    def test_descendants_inherit_gap_selection_and_safe_assertion_mode(self):
        with patch.dict(os.environ, {'PATH': '/original/bin', 'PYTHONOPTIMIZE': '2'}, clear=True):
            env = runner.runtime_environment('/selected tools/gap')
        self.assertEqual(env['SL4_GAP'], '/selected tools/gap')
        self.assertEqual(env['PATH'], '/selected tools'+os.pathsep+'/original/bin')
        self.assertNotIn('PYTHONOPTIMIZE', env)


class SingularSelection(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sl4-tools-')
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def executable(self, relative, body='print("ENDPOINT_UNIT_PASS")'):
        path = self.root/relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('#!'+sys.executable+'\n'+body+'\n')
        path.chmod(0o755)
        return path.resolve()

    def test_override_wins_over_path_and_runs_with_spaces(self):
        selected = self.executable('selected tools/custom-singular')
        other = self.executable('on-path/Singular', 'raise SystemExit(99)')
        with patch.dict(os.environ, {'SL4_SINGULAR': str(selected), 'PATH': str(other.parent)}, clear=True):
            binary = executables.singular_executable()
            result = subprocess.run([str(binary), '-q', 'input with spaces.sing'],
                                    text=True, capture_output=True, check=True)
        self.assertEqual(binary, selected)
        self.assertEqual(result.stdout.strip(), 'ENDPOINT_UNIT_PASS')

    def test_invalid_override_does_not_silently_fall_back(self):
        other = self.executable('on-path/Singular')
        with patch.dict(os.environ, {'SL4_SINGULAR': str(self.root/'missing'), 'PATH': str(other.parent)}, clear=True):
            with self.assertRaisesRegex(FileNotFoundError, 'SL4_SINGULAR'):
                executables.singular_executable()

    def test_nonexecutable_and_empty_overrides_fail(self):
        path = self.root/'not-executable'
        path.write_text('not a program')
        for value in [str(path), '']:
            with self.subTest(value=value), patch.dict(os.environ, {'SL4_SINGULAR': value}, clear=True):
                with self.assertRaises(FileNotFoundError):
                    executables.singular_executable()

    def test_path_does_not_require_sage(self):
        selected = self.executable('on-path/Singular')
        with patch.dict(os.environ, {'PATH': str(selected.parent)}, clear=True), patch.dict(sys.modules, {'sage.env': None}):
            self.assertEqual(executables.singular_executable(), selected)

    def test_sage_local_is_last_fallback(self):
        selected = self.executable('sage-local/bin/Singular')
        env = ModuleType('sage.env')
        env.SAGE_LOCAL = str(selected.parent.parent)
        with patch.dict(os.environ, {'PATH': ''}, clear=True), patch.dict(sys.modules, {'sage.env': env}):
            self.assertEqual(executables.singular_executable(), selected)

    def test_absent_sage_local_reports_actionable_failure(self):
        env = ModuleType('sage.env')
        env.SAGE_LOCAL = None
        with patch.dict(os.environ, {'PATH': ''}, clear=True), patch.dict(sys.modules, {'sage.env': env}):
            with self.assertRaisesRegex(FileNotFoundError, 'set SL4_SINGULAR'):
                executables.singular_executable()

    def test_actual_chart_launcher_uses_override_and_checks_marker(self):
        common = ModuleType('common')
        common.__dict__.update(Path=Path, subprocess=subprocess, shutil=shutil)
        strata = ModuleType('laurent_strata')
        strata.check_support = None
        with patch.dict(sys.modules, {'common': common, 'laurent_strata': strata, 'executables': executables}):
            chart = load('sl4_chart_portability', 'legacy245/endpoint_verification/chart_endpoints.py')
        selected = self.executable('selected tools/custom-singular')
        ring = SimpleNamespace(variable_names=lambda: ['x'])
        with patch.dict(os.environ, {'SL4_SINGULAR': str(selected)}, clear=True):
            chart.singular_unit(ring, ['x'], self.root, 'positive')
        self.assertTrue((self.root/'positive.sing').is_file())
        self.assertEqual((self.root/'positive.log').read_text().strip(), 'ENDPOINT_UNIT_PASS')
        missing_marker = self.executable('selected tools/empty-success', 'pass')
        with patch.dict(os.environ, {'SL4_SINGULAR': str(missing_marker)}, clear=True):
            with self.assertRaises(AssertionError):
                chart.singular_unit(ring, ['x'], self.root, 'negative')


if __name__ == '__main__':
    unittest.main()
