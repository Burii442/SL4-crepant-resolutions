"""Exercise resume integrity against one fresh, real portable computation.

The class runs only the two standard-library stages once. Subsequent commands
must reuse their checkpoints or refuse changed inputs/results; they never run
Sage, GAP, Singular, or the full Cox suite.
"""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ReproduceIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='sl4-reproduce-test-')
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.run_dir = (Path(cls.temporary.name)/'run').resolve()
        if ROOT == cls.run_dir or ROOT in cls.run_dir.parents or cls.run_dir in ROOT.parents:
            raise RuntimeError('The test needs a temporary directory outside the repository')
        cls.env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        cls.env.pop('PYTHONOPTIMIZE', None)
        result = cls.command('--profile', 'portable', '--run-dir', str(cls.run_dir))
        if result.returncode != 0:
            raise RuntimeError('Portable fixture failed:\n'+result.stdout+result.stderr)
        cls.initial_status = (cls.run_dir/'status.json').read_bytes()
        cls.initial_report = (cls.run_dir/'REPORT.txt').read_bytes()
        cls.baseline = json.loads(cls.initial_status)
        if cls.baseline['status'] != 'PASS' or [t['id'] for t in cls.baseline['tasks']] != [
                'portable-catalogue-and-sieves', 'ce03-ce07']:
            raise RuntimeError('The fixture must contain exactly the two completed portable stages')
        if any(t['status'] != 'PASS' or len(t['attempts']) != 1
               for t in cls.baseline['tasks']):
            raise RuntimeError('The fixture did not produce fresh completed checkpoints')

    @classmethod
    def command(cls, *arguments):
        return subprocess.run([sys.executable, '-B', str(ROOT/'reproduce.py'), *arguments],
                              cwd=ROOT, env=cls.env, text=True, capture_output=True,
                              timeout=60)

    def tearDown(self):
        # Each test starts from the same genuinely computed checkpoints.
        # Changed mathematical files are restored by edited_file's finally.
        (self.run_dir/'status.json').write_bytes(self.initial_status)
        (self.run_dir/'REPORT.txt').write_bytes(self.initial_report)

    @contextmanager
    def edited_file(self, path, content):
        original = path.read_bytes()
        try:
            path.write_bytes(content)
            yield
        finally:
            path.write_bytes(original)

    def assert_no_new_attempts(self):
        report = json.loads((self.run_dir/'status.json').read_text())
        self.assertEqual(len(report['tasks']), len(self.baseline['tasks']))
        for actual, original in zip(report['tasks'], self.baseline['tasks']):
            self.assertEqual(actual['attempts'], original['attempts'])
            self.assertEqual(actual['receipt'], original['receipt'])
            self.assertEqual(sorted(p.name for p in (self.run_dir/'steps'/actual['id']).iterdir()),
                             ['attempt-1'])

    def test_resume_reuses_completed_checkpoints_without_new_attempts(self):
        result = self.command('--resume', str(self.run_dir))
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        for task in self.baseline['tasks']:
            self.assertIn('REUSED PASS '+task['id'], result.stdout)
        self.assertNotIn('START ', result.stdout)
        self.assertEqual(json.loads((self.run_dir/'status.json').read_text())['status'], 'PASS')
        self.assert_no_new_attempts()

    def test_resume_refuses_changed_frozen_catalogue(self):
        relative = 'repository/manuscript106/catalogue/catalogue.json'
        path = self.run_dir/'inputs'/relative
        with self.edited_file(path, path.read_bytes()+b'\n'):
            result = self.command('--resume', str(self.run_dir))
        self.assertEqual(result.returncode, 1, result.stdout+result.stderr)
        self.assertIn('Frozen input changed: '+relative, result.stderr)
        self.assertNotIn('START ', result.stdout)
        self.assert_no_new_attempts()

    def test_resume_refuses_unlisted_frozen_file(self):
        extra = self.run_dir/'inputs/repository/unlisted-test-input.txt'
        try:
            extra.write_text('This file is absent from the frozen input manifest.\n')
            result = self.command('--resume', str(self.run_dir))
        finally:
            extra.unlink(missing_ok=True)
        self.assertEqual(result.returncode, 1, result.stdout+result.stderr)
        self.assertIn('Frozen input file list changed', result.stderr)
        self.assertNotIn('START ', result.stdout)
        self.assert_no_new_attempts()

    def refuse_changed_result(self, relative):
        task = self.baseline['tasks'][1]
        path = self.run_dir/task['attempts'][0]['directory']/relative
        self.assertIn(str(path.relative_to(self.run_dir)), task['receipt'])
        with self.edited_file(path, path.read_bytes()+b'\n'):
            result = self.command('--resume', str(self.run_dir))
        self.assertEqual(result.returncode, 1, result.stdout+result.stderr)
        self.assertIn('Completed result changed: ce03-ce07', result.stderr)
        self.assertNotIn('START ', result.stdout)
        self.assertEqual(json.loads((self.run_dir/'status.json').read_text())['status'], 'FAILED')
        self.assert_no_new_attempts()

    def test_resume_refuses_changed_completed_proof(self):
        self.refuse_changed_result('result/ce03_ce07.json')

    def test_resume_refuses_changed_completed_log(self):
        self.refuse_changed_result('stdout.log')


if __name__ == '__main__':
    unittest.main()
