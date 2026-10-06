"""Isolated outputs and explicit provenance for the E/F geometry checks."""
import argparse
import contextlib
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import traceback

# Imported legacy helpers are read-only proof inputs, not cache locations.
sys.dont_write_bytecode = True

BASE = Path(__file__).resolve().parent
REPOSITORY = BASE.parent.parent
GEOMETRY_STEPS = {
    132: [('verify_132_resolution.py', '"result": "PASS"')],
    234: [('validate_inputs.py', 'DISCRIMINANT_AND_CONTRACTED_CHART_INPUTS_PASS'),
          ('validate234_geometry.py', 'PASS_GEOMETRIC_YES_234_235'),
          ('root_audit234.py', 'PASS_INDEPENDENT_INPUT_BINDING_AND_LOCAL_GEOMETRY')],
    236: [('validate_inputs.py', 'DISCRIMINANT_AND_CONTRACTED_CHART_INPUTS_PASS'),
          ('validate236_geometry.py', 'PASS_GEOMETRIC_YES_236_237'),
          ('root_audit236.py', 'PASS_INDEPENDENT_236_INPUT_CENTERS_REES_AND_COVER')],
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


class Tee:
    def __init__(self, console, log):
        self.console, self.log = console, log

    def write(self, text):
        self.console.write(text)
        self.log.write(text)
        self.log.flush()
        return len(text)

    def flush(self):
        self.console.flush()
        self.log.flush()


class Context:
    def __init__(self, args):
        self.args = args
        self.legacy = args.legacy_root.resolve()
        self.paper = args.paper.resolve() if args.paper is not None else None
        self.output = args.output_dir.resolve()
        self.inputs = {}
        self.geometry_runs = []

    def label(self, path):
        path = Path(path).resolve()
        for root, prefix in [(self.output, 'output'), (self.legacy, 'legacy245'),
                             (REPOSITORY, 'repository')]:
            try:
                return prefix + '/' + path.relative_to(root).as_posix()
            except ValueError:
                pass
        return 'external:' + str(path)

    def bind(self, path):
        path = Path(path).resolve()
        self.inputs[self.label(path)] = sha(path)
        return path

    def read(self, path):
        return json.loads(self.bind(path).read_text())

    def section(self, sieve):
        require(self.paper is not None, 'No external paper was supplied')
        text = self.bind(self.paper).read_text()
        marker = '\\label{sec:sieve-' + sieve + '}'
        require(text.count(marker) == 1, 'Expected one paper section label: ' + marker)
        label = text.index(marker)
        start = text.rfind('\\section{', 0, label)
        end = text.find('\\section{', label)
        require(start >= 0, 'Section heading missing before ' + marker)
        return text[start:end if end >= 0 else len(text)]

    def example_matrices(self, sieve, current_case, legacy_case, expected):
        """Always bind the catalogue; optionally audit an external paper display."""
        catalogue = self.read(REPOSITORY / 'manuscript106/catalogue/catalogue.json')
        rows = [row for row in catalogue if row['index'] == current_case]
        require(len(rows) == 1, 'Expected one current catalogue example')
        require(rows[0]['actual_generators'] == expected,
                'Current and legacy example matrices differ')
        result = {'current_case': current_case, 'legacy_case': legacy_case,
                  'catalogue_matrices_match': True,
                  'paper_display': {'status': 'not_requested'}}
        if self.paper is None:
            return result
        section = self.section(sieve)
        printed = [[[int(value.strip()) for value in row.split('&')]
                    for row in raw.split(r'\\')]
                   for raw in re.findall(r'\\begin\{pmatrix\}(.*?)\\end\{pmatrix\}',
                                         section, re.S)]
        if sieve == 'E':
            require(r'g_1=-I_4' in section, 'Expected the displayed negative identity')
            printed.insert(0, [[-int(i == j) for j in range(4)] for i in range(4)])
        require(printed == expected, 'External paper and catalogue example matrices differ')
        result['paper_display'] = {'status': 'PASS', 'printed_matrices_match': True,
                                   'input': self.label(self.paper)}
        return result

    def run_geometry(self):
        """Run now by default; supplied reports are always marked as prior outputs."""
        supplied = self.args.geometry_runs
        root = supplied.resolve() if supplied else self.output
        runner = self.bind(self.legacy / 'geometry_proofs/run.py')
        for case, steps in GEOMETRY_STEPS.items():
            folder = root / ('geometry_' + str(case))
            command = None
            if supplied is None:
                command = [sys.executable, str(runner), '--case', str(case),
                           '--output-dir', str(folder)]
                for option in ['singular', 'gap']:
                    value = getattr(self.args, option)
                    if value:
                        command += ['--' + option, value]
                print('Starting fresh geometry', case, flush=True)
                proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, text=True,
                                        bufsize=1)
                try:
                    for line in proc.stdout:
                        print(line, end='', flush=True)
                    require(proc.wait() == 0, 'Fresh geometry failed: ' + str(case))
                except BaseException:
                    # The top-level wrapper owns the worker's process group,
                    # including this stage and all its Singular/GAP children.
                    if proc.poll() is None:
                        proc.terminate()
                    raise
            report = self.read(folder / 'run.json')
            require(report['status'] == 'PASS' and report['case'] == case,
                    'Geometry report is not PASS for the requested case')
            source = self.legacy / 'geometry_proofs' / str(case)
            required = {str(p.relative_to(self.legacy)) for p in source.iterdir() if p.is_file()}
            required.update(['geometry_proofs/run.py', 'catalogue.json', 'runtime_cache.py'])
            if case != 132:
                required.add('geometry_proofs/validate_inputs.py')
            require(set(report['inputs']) == required, 'Incomplete geometry input manifest')
            for name, digest in report['inputs'].items():
                require(sha(self.bind(self.legacy / name)) == digest,
                        'Geometry input hash mismatch: ' + name)
            require([step['script'] for step in report['steps']] == [s[0] for s in steps],
                    'Geometry report omitted or reordered required steps')
            for step, (_, marker) in zip(report['steps'], steps):
                require(step['status'] == 'PASS' and step['returncode'] == 0,
                        'Geometry step is not PASS')
                log = (folder / step['log']).resolve()
                require(log.is_relative_to(folder.resolve()), 'Geometry log must be inside its run')
                require(sha(self.bind(log)) == step['log_sha256'], 'Geometry log hash mismatch')
                require(marker in log.read_text(), 'Geometry completion assertion missing')
            self.geometry_runs.append({
                'case': case, 'status': 'PASS', 'steps': len(steps),
                'mode': 'provided_prior_outputs' if supplied else 'fresh_in_this_invocation',
                'report': self.label(folder / 'run.json'),
                'report_sha256': sha(folder / 'run.json'),
                'original_started_utc': report.get('started_utc'),
                'command': command,
            })
        return self.geometry_runs


def main(sieve, verify, script):
    parser = argparse.ArgumentParser(description='Exact portable geometry checks for Sieve ' + sieve)
    parser.add_argument('--output-dir', type=Path, required=True, help='New or empty result directory')
    parser.add_argument('--legacy-root', type=Path, default=REPOSITORY / 'legacy245')
    parser.add_argument('--paper', type=Path,
                        help='Optional external LaTeX paper: also audit its example matrices')
    parser.add_argument('--_worker', action='store_true', help=argparse.SUPPRESS)
    if sieve == 'E':
        parser.add_argument('--geometry-runs', type=Path,
                            help='Use prior ROOT/geometry_132,234,236/run.json; do not rerun these stages')
        parser.add_argument('--singular', help='Singular executable for fresh geometric stages')
        parser.add_argument('--gap', help='GAP executable for fresh geometric stages')
    args = parser.parse_args()
    if not __debug__:
        parser.error('Do not use Python optimization: the exact checks require assertions')
    context = Context(args)
    if args._worker:
        if os.environ.get('SL4_GEOMETRY_WORKER_OUTPUT') != str(context.output):
            parser.error('Internal worker requires the parent runner')
        result = verify(context)
        result['input_sha256'] = context.inputs
        if sieve == 'E':
            result['geometry_runs'] = context.geometry_runs
        (context.output / 'worker_result.json').write_text(json.dumps(result, indent=2) + '\n')
        return 0
    if not context.legacy.is_dir():
        parser.error('The supplied legacy root must exist')
    if context.paper is not None:
        if not context.paper.is_file():
            parser.error('The supplied external paper must exist')
        try:
            context.section(sieve)
        except (AssertionError, OSError, UnicodeError) as error:
            parser.error('Invalid external paper: ' + str(error))
    if context.output.is_relative_to(context.legacy):
        parser.error('Place outputs outside the read-only legacy inputs')
    if context.output.exists() and (not context.output.is_dir() or any(context.output.iterdir())):
        parser.error('Output directory must be new or empty')
    context.output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    report = {'status': 'RUNNING', 'sieve': sieve,
              'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'python': sys.version, 'command': [sys.executable] + sys.argv,
              'input_sha256': context.inputs}

    def save():
        target = context.output / 'report.json'
        temporary = target.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(report, indent=2) + '\n')
        temporary.replace(target)

    save()
    cache = None
    exit_code = 0
    with (context.output / 'verification.log').open('w') as log:
        with contextlib.redirect_stdout(Tee(sys.stdout, log)), contextlib.redirect_stderr(Tee(sys.stderr, log)):
            try:
                context.bind(script)
                context.bind(Path(__file__))
                context.bind(context.legacy / 'runtime_cache.py')
                sys.path.insert(0, str(context.legacy))
                from runtime_cache import allocate_sage_cache, terminate_owned_process_group
                # Some Sage launchers set DOT_SAGE to the user's default
                # directory. Always own a private cache for this top-level run.
                cache = allocate_sage_cache(context.output / 'sage-cache')
                report['sage_cache'] = cache.metadata()
                # Sage may preload sage.env before this file is executed.
                # A new interpreter must receive DOT_SAGE before startup.
                env = dict(os.environ, DOT_SAGE=str(cache.path),
                           SL4_GEOMETRY_WORKER_OUTPUT=str(context.output),
                           PYTHONUNBUFFERED='1', PYTHONDONTWRITEBYTECODE='1')
                command = [sys.executable, str(Path(script).resolve())] + sys.argv[1:] + ['--_worker']
                report['worker_command'] = command
                save()
                proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, text=True,
                                        bufsize=1, env=env, start_new_session=True)
                try:
                    for line in proc.stdout:
                        print(line, end='', flush=True)
                    require(proc.wait() == 0, 'Geometry worker failed; see verification.log')
                except BaseException:
                    report['worker_termination'] = terminate_owned_process_group(proc, {proc.pid})
                    raise
                result = json.loads((context.output / 'worker_result.json').read_text())
                context.inputs.update(result.pop('input_sha256'))
                report.update(result)
                require(report['status'] == 'PASS', 'Verifier did not complete successfully')
            except BaseException as error:
                report['status'] = 'INTERRUPTED' if isinstance(error, KeyboardInterrupt) else 'FAILED'
                report['error'] = type(error).__name__ + ': ' + str(error)
                traceback.print_exc()
                exit_code = 130 if isinstance(error, KeyboardInterrupt) else 1
            finally:
                if cache is not None:
                    report['sage_cache_cleanup'] = cache.cleanup([proc.pid] if 'proc' in locals() else [])
                report['elapsed_seconds'] = round(time.monotonic() - started, 3)
                report['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                print('SIEVE_' + sieve + '_' + report['status'], flush=True)
    report['log_sha256'] = sha(context.output / 'verification.log')
    save()
    return exit_code
