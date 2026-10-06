#!/usr/bin/env python3
"""Run the SL4 checks in an isolated copy, using manuscript case numbers."""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
COX_CASES = [114, 138, 140, 143, 151, 161, 167, 171, 173, 174, 177,
             178, 179, 194, 206, 221, 222, 227, 231, 233, 243]
COMMON_STEPS = ['criteria', 'criteria-geometry', 'catalogue', 'representatives',
                'compact', 'integral-lattices', 'named-hodge', 'seven-torsion',
                'extra-models', 'geometry', 'cox-models',
                'geometry-132', 'geometry-234', 'geometry-236']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_environment(gap=None):
    """Keep the selected standalone GAP visible to descendant launchers.

    Sieve E also receives --gap explicitly, since Sage can adjust PATH.
    Sieve F uses Sage's exact algebra and has no standalone GAP command.
    """
    env = os.environ.copy()
    env.pop('PYTHONOPTIMIZE', None)
    env['PYTHONUNBUFFERED'] = '1'
    if gap:
        env['SL4_GAP'] = str(gap)
        env['PATH'] = str(Path(gap).parent) + os.pathsep + env.get('PATH', '')
    return env


def preflight():
    if sys.flags.optimize:
        raise ValueError('Assertions must remain enabled; do not use python -O or PYTHONOPTIMIZE.')
    subprocess.run([sys.executable, str(ROOT/'tools/build_case_index.py'), '--check'],
                   check=True, stdout=subprocess.DEVNULL)
    spec = importlib.util.spec_from_file_location('legacy_runner', ROOT/'legacy245/run_verification.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    registry = module.registry()
    expected = set(COMMON_STEPS) | {f'{kind}-{n}' for n in COX_CASES
                                           for kind in ['binding', 'cox', 'endpoint']}
    if set(registry) != expected:
        raise ValueError(f'Legacy registry mismatch: missing={sorted(expected-set(registry))}, extra={sorted(set(registry)-expected)}')
    for n in COX_CASES:
        for name in ['model.json', 'invariants.json']:
            if not (ROOT/'legacy245'/str(n)/name).is_file():
                raise ValueError(f'Missing Cox input: {n}/{name}')
    for script, _, _ in registry.values():
        if not (ROOT/'legacy245'/script).is_file():
            raise ValueError(f'Missing legacy entry point: {script}')
    index = json.loads((ROOT/'cases/index.json').read_text())['cases']
    if sorted(c['case'] for c in index) != list(range(1, 107)):
        raise ValueError('The case index must contain each manuscript case 1–106 exactly once.')
    if sum(c['decision'] == 'YES' for c in index) != 61 or sum(c['decision'] == 'NO' for c in index) != 45:
        raise ValueError('Unexpected manuscript outcome labels.')
    for c in index:
        if set(c['legacy_steps']) - expected:
            raise ValueError(f'Unknown legacy step in case {c["case"]}.')
        for ext in c['extensions']:
            if ext.get('entrypoint') and not (ROOT/ext['entrypoint']).is_file():
                raise ValueError(f'Missing extension: {ext["entrypoint"]}')
    return index, registry


def plan(args, index):
    tasks = [
        {'id': 'catalogue106', 'runtime': 'python', 'script': 'manuscript106/catalogue/verify_catalogue.py', 'args': []},
        {'id': 'reduction245to106', 'runtime': 'python', 'script': 'manuscript106/catalogue/verify_reduction.py', 'args': []},
        {'id': 'sieve-cover', 'runtime': 'python', 'script': 'manuscript106/sieves/verify.py', 'args': []},
    ]
    extended = args.case is not None or args.profile != 'portable'
    if extended:
        tasks.append({'id': 'crystcat-enumeration', 'runtime': 'gap',
                      'script': 'classification/count_crystcat.g', 'args': [], 'cwd': 'classification'})
    tasks.append({'id': 'classical-comparison', 'runtime': 'python',
                  'script': 'classification/compare_catalogue.py',
                  'args': ['{snapshot}/manuscript106/catalogue/catalogue.json']})
    if args.case is not None:
        case = next(c for c in index if c['case'] == args.case)
        tasks.append({'id': 'legacy', 'runtime': 'python', 'script': 'legacy245/run_verification.py',
                      'args': ['--steps', ','.join(case['legacy_steps']), '--sage', '{sage}',
                               '--output-dir', '{out}/legacy']})
        for ext in case['extensions']:
            if ext.get('entrypoint'):
                extra = (['--gap', '{gap}'] if ext['id'] in ['abelian-lattice', 'sieve-e'] else
                         ['--sage', '{sage}'] if ext['id'] == 'dhz' else [])
                tasks.append({'id': ext['id'], 'runtime': ext.get('runtime', 'python'),
                              'script': ext['entrypoint'], 'args': ext.get('arguments', []) + extra +
                              ['--output-dir', '{out}/extensions/'+ext['id']]})
    elif args.profile in ['core', 'all']:
        tasks.append({'id': 'legacy', 'runtime': 'python', 'script': 'legacy245/run_verification.py',
                      'args': ['--profile', args.profile, '--sage', '{sage}', '--output-dir', '{out}/legacy']})
        tasks.append({'id': 'abelian-lattice', 'runtime': 'python', 'script': 'extensions/abelian/verify.py',
                      'args': ['--gap', '{gap}', '--output-dir', '{out}/extensions/abelian-lattice']})
        if args.profile == 'all':
            for name, script in [('sieve-e', 'extensions/geometry/verify_E.py'),
                                 ('sieve-f', 'extensions/geometry/verify_F.py'),
                                 ('dhz', 'extensions/dhz/verify.py')]:
                tasks.append({'id': name, 'runtime': 'sage', 'script': script,
                              'args': (['--sage', '{sage}'] if name == 'dhz' else
                                       ['--gap', '{gap}'] if name == 'sieve-e' else []) +
                              ['--output-dir', '{out}/extensions/'+name]})
    return tasks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--profile', choices=['portable', 'core', 'all'], default='portable')
    mode.add_argument('--case', type=int, choices=range(1, 107), metavar='1..106')
    parser.add_argument('--list', action='store_true', help='List manuscript cases and linked checks')
    parser.add_argument('--plan', action='store_true', help='Show the exact selected checks without running them')
    parser.add_argument('--output-dir', type=Path, help='New or empty output directory outside this repository')
    parser.add_argument('--sage', default=shutil.which('sage'))
    parser.add_argument('--gap', default=shutil.which('gap'))
    args = parser.parse_args()
    index, registry = preflight()
    if args.list:
        for c in index:
            print(f'{c["case"]:03d}  {c["decision"]:3s}  sieve {c["primary_sieve"]}  legacy {c["source_legacy_index"]}: '+', '.join(c['legacy_steps']))
        return
    tasks = plan(args, index)
    if args.plan:
        print(json.dumps({'case': args.case, 'profile': None if args.case else args.profile,
                          'legacy_registry_steps': len(registry), 'tasks': tasks}, indent=2))
        return
    if args.output_dir is None:
        parser.error('--output-dir is required unless --list or --plan is used')
    if any(t['runtime'] == 'sage' or t['id'] == 'legacy' for t in tasks) and not args.sage:
        parser.error('SageMath is required for these checks; pass --sage /path/to/sage')
    if any(t['runtime'] == 'gap' or t['id'] == 'abelian-lattice' for t in tasks) and not args.gap:
        parser.error('GAP with CrystCat is required; pass --gap /path/to/gap')
    if args.gap and any(t['runtime'] == 'gap' for t in tasks):
        gap = shutil.which(os.path.expanduser(args.gap))
        if not gap:
            parser.error('The selected GAP executable is missing or not executable: '+args.gap)
        # Child programs run in an isolated working directory, so relative
        # executable paths must be resolved before changing that directory.
        args.gap = str(Path(gap).resolve())
    out = args.output_dir.resolve()
    if out == ROOT or ROOT in out.parents or out in ROOT.parents:
        parser.error('The output directory must be outside the repository and cannot contain it')
    if out.exists() and any(out.iterdir()):
        parser.error('The output directory must be new or empty; existing calculations are not reused')
    out.mkdir(parents=True, exist_ok=True)
    snapshot = out/'inputs'
    report = {'status': 'PREPARING', 'case': args.case, 'profile': None if args.case else args.profile,
              'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'steps': [],
              'scope': 'Only the checks selected in this report; outcome labels and file hashes alone are not geometric proofs.'}

    def save():
        tmp = out/'verification.json.tmp'
        tmp.write_text(json.dumps(report, indent=2)+'\n')
        tmp.replace(out/'verification.json')

    save()
    try:
        shutil.copytree(ROOT, snapshot, ignore=shutil.ignore_patterns('.git', '__pycache__', '.DS_Store', 'evidence', '*.pyc', '*.tar.xz', '*.tar.gz'))
        manifest = {str(p.relative_to(snapshot)): sha(p) for p in sorted(snapshot.rglob('*')) if p.is_file()}
        (out/'input_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
        report['input_manifest_sha256'] = sha(out/'input_manifest.json')
        report['status'] = 'RUNNING'
        save()
        env = runtime_environment(args.gap if any(t['runtime'] == 'gap' for t in tasks) else None)
        (out/'sage-cache').mkdir()
        env['DOT_SAGE'] = str(out/'sage-cache')
        for task in tasks:
            generated = {
                'catalogue106': snapshot/'manuscript106/catalogue/verification_106.json',
                'reduction245to106': snapshot/'manuscript106/catalogue/verification_reduction.json',
                'sieve-cover': snapshot/'manuscript106/sieves/verification.json',
                'crystcat-enumeration': snapshot/'classification/all_qclasses.json',
                'classical-comparison': snapshot/'classification/comparison.json',
                'legacy': out/'legacy/verification.json',
                'abelian-lattice': out/'extensions/abelian-lattice/report.json',
                'sieve-e': out/'extensions/sieve-e/report.json',
                'sieve-f': out/'extensions/sieve-f/report.json',
                'dhz': out/'extensions/dhz/report.json',
            }[task['id']]
            if generated.exists():
                generated.unlink()  # Only generated outputs inside the isolated run.
            values = {'snapshot': str(snapshot), 'out': str(out), 'sage': args.sage or '', 'gap': args.gap or ''}
            argv = [a.format(**values) for a in task['args']]
            if task['runtime'] == 'sage': command = [args.sage, '-python', str(snapshot/task['script'])] + argv
            elif task['runtime'] == 'gap': command = [args.gap, '-q', '--quitonbreak', str(snapshot/task['script'])] + argv
            else: command = [sys.executable, str(snapshot/task['script'])] + argv
            log = out/(task['id']+'.log')
            item = {'id': task['id'], 'status': 'RUNNING', 'command': command, 'log': log.name}
            report['steps'].append(item)
            save()
            print('START '+task['id'], flush=True)
            start = time.monotonic()
            with log.open('w') as stream:
                proc = subprocess.Popen(command, cwd=snapshot/task.get('cwd', '.'), env=env,
                                        stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
                try:
                    code = proc.wait()
                except BaseException:
                    if proc.poll() is None:
                        os.killpg(proc.pid, signal.SIGINT)
                        try: proc.wait(timeout=30)
                        except subprocess.TimeoutExpired:
                            os.killpg(proc.pid, signal.SIGTERM)
                            proc.wait(timeout=10)
                    raise
            valid = code == 0 and generated.is_file()
            if valid:
                proof = json.loads(generated.read_text())
                if task['id'] == 'crystcat-enumeration':
                    valid = proof.get('counts') == {'all_qclasses': 227, 'all_zclasses': 710,
                                                   'det_one_qclasses': 106, 'det_one_zclasses': 245}
                    valid = valid and 'ALL_Q=227 ALL_Z=710 SL4_Q=106 SL4_Z=245' in log.read_text()
                elif task['id'] == 'dhz':
                    valid = proof.get('status') == 'ALL_REQUESTED_DHZ_INVARIANT_CHECKS_PASS' and proof.get('complete') is True
                else:
                    valid = proof.get('status') == 'PASS'
                item['result'] = str(generated.relative_to(out))
                item['result_sha256'] = sha(generated)
            item.update(status='PASS' if valid else 'FAILED', returncode=code,
                        seconds=round(time.monotonic()-start, 3), log_sha256=sha(log))
            save()
            print(item['status']+' '+task['id'], flush=True)
            if not valid:
                raise RuntimeError(f'{task["id"]} failed; see {log}')
        report['status'] = 'PASS'
    except BaseException as error:
        report['status'] = 'INTERRUPTED' if isinstance(error, KeyboardInterrupt) else 'FAILED'
        report['error'] = str(error)
        for item in report['steps']:
            if item['status'] == 'RUNNING': item['status'] = report['status']
        raise
    finally:
        report['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        save()
    print('PASS: '+str(out/'verification.json'))


if __name__ == '__main__':
    main()
