#!/usr/bin/env python3
"""Resumable exact verification of the SL4 catalogue. No network or AI calls.

Default: the 72 legacy checks used by the paper plus its
additional exact checks. A completed Cox bundle retains binding, full Cox
generation, exact Hilbert=Molien comparison and geometric endpoint together.
"""
import argparse
from collections import Counter
import datetime as dt
import fcntl
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

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
REPO = ROOT
SUPPORT = REPO/'verification'
OUTPUT = REPO.parent/'SL4-results'
SCHEMA = 1
RUNTIME_NAMES = ('sage', 'gap', 'singular', 'magma', 'cxx')


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write_json(path, value):
    path = Path(path)
    tmp = path.with_name(path.name+'.tmp')
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')
    tmp.replace(path)


def read_json(path):
    return json.loads(Path(path).read_text())


def probe_runtimes(runtime, profile, overrides, output_dir=None):
    discovered = runtime.discover(**overrides)
    required = () if profile == 'portable' else ('sage', 'gap', 'singular', 'cxx')
    selected = set(required)
    if profile != 'portable' and overrides.get('magma') is not None:
        selected.add('magma')  # Optional diagnostics; never a prerequisite.
    result = runtime.probe({name: value for name, value in discovered.items()
                            if name in selected}, output_dir=output_dir)
    for name, value in discovered.items():
        if name not in selected:
            result[name] = dict(value, status='not_required', tested=False)
    result['python'] = dict(path=sys.executable, status='pass', version=sys.version,
                          found=True, tested=True)
    return result


def make_plan(profile, with_paper=False):
    coverage = read_json(SUPPORT/'coverage.json')
    tasks = ([dict(id='paper-matrix-binding', kind='paper')] if with_paper else []) + [
        dict(id='portable-catalogue-and-sieves', kind='portable'),
        dict(id='ce03-ce07', kind='ce03'),
    ]
    if profile == 'portable':
        return tasks
    tasks += [dict(id='fresh-crystcat', kind='classical'),
              dict(id='paper-claims', kind='claims'),
              dict(id='gachet-ages', kind='gachet')]
    for item in coverage['common_tasks']:
        tasks.append(dict(id='legacy-'+item['id'], kind='legacy',
                          steps=[item['id']], scope=item['scope']))
    tasks += [dict(id='abelian-lattice', kind='abelian'),
              dict(id='sieve-e', kind='sieve-e',
                   requires=['legacy-geometry-'+str(c) for c in (132, 234, 236)]),
              dict(id='sieve-f', kind='sieve-f')]
    for case in (45, 65, 66, 105):
        tasks.append(dict(id='dhz-'+str(case), kind='dhz', case=case))
    for item in coverage['cox_bundles']:
        tasks.append(dict(id='cox-bundle-'+str(item['old_case']), kind='legacy',
                          steps=item['steps'], old_case=item['old_case'],
                          current_cases=item['current_cases']))
    selected = [s for t in tasks for s in t.get('steps', [])]
    legacy = load_module(REPO/'legacy245/run_verification.py', 'legacy_plan')
    if len(selected) != 72 or set(selected) != set(legacy.registry()):
        raise ValueError('The 72-step registry and the local coverage plan differ')
    return tasks


def save(run, report):
    report['updated_utc'] = now()
    counts = Counter(t['status'] for t in report['tasks'])
    report['counts'] = dict(counts)
    write_json(run/'status.json', report)
    lines = ['SL4 REPRODUCTION REPORT', '', 'Status: '+report['status'],
             f"Completed: {counts['PASS']}/{len(report['tasks'])}",
             'This report concerns the frozen repository and optional external paper.',
             'PASS certifies the selected computations; cited mathematical theorems are not reproved.',
             'Completed stages can be resumed without AI or network access.', '']
    for t in report['tasks']:
        lines.append(f"{t['status']:12} {t['id']}")
        if t.get('error'):
            lines.append('  '+t['error'])
    lines += ['', 'Resume:', f'python3 "{ROOT / "reproduce.py"}" --resume "{run}"',
              '', 'Details and logs: '+str(run/'steps')]
    (run/'REPORT.txt').write_text('\n'.join(lines)+'\n')


def prepare(args):
    paper = args.paper.resolve() if args.paper is not None else None
    plan = make_plan(args.profile, paper is not None)
    if paper is not None and not paper.is_file():
        raise ValueError('Missing manuscript: '+str(paper))
    run = (args.run_dir or OUTPUT/dt.datetime.now().strftime('run-%Y%m%d-%H%M%S')).resolve()
    if run == REPO or REPO in run.parents or run in REPO.parents:
        raise ValueError('Place the run outside the code repository and its ancestors')
    if paper is not None and (run == paper or run in paper.parents):
        raise ValueError('The run directory cannot contain the supplied paper')
    if run.exists() and (not run.is_dir() or any(run.iterdir())):
        raise ValueError('Output exists; use --resume or a new --run-dir')
    if shutil.disk_usage(ROOT).free < 4*1024**3 and args.profile == 'all':
        raise ValueError('At least 4 GiB free disk space is required for the isolated calculation copies')
    run.mkdir(parents=True, exist_ok=True)
    inputs = run/'inputs'
    inputs.mkdir()
    ignore = shutil.ignore_patterns('.git', '__pycache__', '.DS_Store', '*.pyc',
                                   'evidence', '*.tar.xz', '*.tar.gz')
    shutil.copytree(REPO, inputs/'repository', ignore=ignore)
    if paper is not None:
        shutil.copy2(paper, inputs/'paper.tex')
    write_json(inputs/'plan.json', dict(profile=args.profile,
               paper_supplied=paper is not None, tasks=plan))
    manifest = {str(p.relative_to(inputs)): sha(p)
                for p in sorted(inputs.rglob('*')) if p.is_file()}
    write_json(run/'input_manifest.json', manifest)
    report = dict(schema=SCHEMA, status='PREPARED', created_utc=now(),
                  profile=args.profile, paper_supplied=paper is not None,
                  original_paper=str(paper) if paper is not None else None,
                  original_repository=str(REPO),
                  input_manifest_sha256=sha(run/'input_manifest.json'),
                  tasks=[dict(t, status='PENDING', attempts=[]) for t in plan],
                  runtime_overrides={n: getattr(args, n) for n in
                                     ('sage', 'gap', 'singular', 'magma', 'cxx')},
                  scope=('Catalogue/reduction/sieve checks and CE03/CE07 arithmetic. '
                         if args.profile == 'portable' else
                         'Fresh manuscript claims and the 72 legacy checks used by the paper. ')+
                        'An external paper is checked only when supplied. '
                        'No AI/network calls.',
                  resume_policy='Only completed stages with matching frozen inputs, proof files and logs are reused. '
                                'Interrupted stages restart in a new attempt directory. '
                                'Cox stages are resumed as binding+generation+endpoint bundles.')
    save(run, report)
    return run


def check_frozen(run, report):
    if report['schema'] != SCHEMA:
        raise ValueError('Unsupported run format')
    if sha(run/'input_manifest.json') != report['input_manifest_sha256']:
        raise ValueError('Input manifest changed')
    inputs = (run/'inputs').resolve()
    manifest = read_json(run/'input_manifest.json')
    if not isinstance(manifest, dict) or not manifest:
        raise ValueError('Missing frozen input manifest')
    for name, digest in manifest.items():
        path = (inputs/name).resolve()
        if inputs not in path.parents:
            raise ValueError('Unsafe frozen input path: '+name)
        if not path.is_file() or sha(path) != digest:
            raise ValueError('Frozen input changed: '+name)
    actual = {str(path.relative_to(inputs)) for path in inputs.rglob('*') if path.is_file()}
    if actual != set(manifest):
        raise ValueError('Frozen input file list changed')
    plan = read_json(inputs/'plan.json')
    if (report.get('profile') != plan['profile'] or
            report.get('paper_supplied') != plan['paper_supplied'] or
            len(report.get('tasks', [])) != len(plan['tasks'])):
        raise ValueError('Saved execution plan changed')
    for task, expected in zip(report['tasks'], plan['tasks']):
        if any(task.get(key) != value for key, value in expected.items()):
            raise ValueError('Saved task changed: '+expected['id'])


def receipt_valid(run, task):
    if task['status'] != 'PASS' or not task.get('receipt'):
        return False
    return all(run in (run/name).resolve().parents and
               (run/name).is_file() and sha(run/name) == value
               for name, value in task['receipt'].items())


def command_for(task, run, attempt, paths, report):
    repo = run/'inputs/repository'
    support = repo/'verification'
    paper = run/'inputs/paper.tex'
    paper_args = ['--paper', str(paper)] if report.get('paper_supplied') else []
    out = attempt/'result'
    py = [sys.executable]
    sage = [paths.get('sage', ''), '-python']
    kind = task['kind']
    if kind == 'paper':
        return py+[str(repo/'tools/build_case_index.py'), '--check', '--paper', str(paper)], None
    if kind == 'portable':
        return py+[str(repo/'verify.py'), '--profile', 'portable', '--output-dir', str(out)], out/'verification.json'
    if kind == 'classical':
        return py+[str(support/'run_classical.py'), '--repo', str(repo), '--gap', paths['gap'], '--output-dir', str(out)], out/'report.json'
    if kind == 'ce03':
        return py+[str(repo/'verification/check_ce03_ce07.py'), '--output-dir', str(out)], out/'ce03_ce07.json'
    if kind == 'claims':
        return sage+[str(support/'verify_paper_claims.py'), '--repo', str(repo), '--output-dir', str(out)]+paper_args, out/'report.json'
    if kind == 'gachet':
        return [paths['gap'], '-q', '--quitonbreak', str(support/'gachet_cohomology.g')], None
    if kind == 'legacy':
        return py+[str(repo/'legacy245/run_verification.py'), '--steps', ','.join(task['steps']),
                   '--sage', paths['sage'], '--keep-going', '--output-dir', str(out)], out/'verification.json'
    if kind == 'abelian':
        return py+[str(repo/'extensions/abelian/verify.py'), '--gap', paths['gap'], '--output-dir', str(out)], out/'report.json'
    if kind in ('sieve-e', 'sieve-f'):
        argv = sage+[str(repo/('extensions/geometry/verify_'+kind[-1].upper()+'.py')),
                     '--output-dir', str(out)]+paper_args
        if kind == 'sieve-e':
            prior = attempt/'geometry_from_this_run'
            prior.mkdir()
            for case in (132, 234, 236):
                key = 'legacy-geometry-'+str(case)
                dep = next(t for t in report['tasks'] if t['id'] == key)
                origin = run/dep['attempts'][-1]['directory']/'result/steps'/('geometry-'+str(case))/'result'
                (prior/('geometry_'+str(case))).symlink_to(origin, target_is_directory=True)
            argv += ['--geometry-runs', str(prior), '--gap', paths['gap'], '--singular', paths['singular']]
        return argv, out/'report.json'
    if kind == 'dhz':
        return py+[str(repo/'extensions/dhz/verify.py'), '--case', str(task['case']),
                   '--sage', paths['sage'], '--output-dir', str(out)], out/'report.json'
    raise ValueError('Unknown task '+kind)


def validate(task, attempt, proof, validation):
    log = (attempt/'stdout.log').read_text(errors='replace')
    if task['kind'] == 'paper':
        data = json.loads(log)
        if data.get('status') != 'PASS' or data.get('cases') != 106 or data.get('manuscript_comparison') != 'checked':
            raise ValueError('Manuscript matrix comparison incomplete')
    elif task['kind'] == 'gachet':
        marker = 'PASS: two dual representations; age polynomial 1+t+2*t^2+2*t^3+t^4; b2=1, b4=2.'
        # GAP inserts backslash-newline continuations at its terminal width.
        if marker not in log.replace('\\\n', ''):
            raise ValueError('Gachet computation omitted its completion assertion')
    elif task['kind'] == 'legacy':
        validation.validate_legacy(attempt/'result', task['steps'])
    else:
        data = read_json(proof)
        expected = 'ALL_REQUESTED_DHZ_INVARIANT_CHECKS_PASS' if task['kind'] == 'dhz' else 'PASS'
        if data.get('status') != expected:
            raise ValueError('Required mathematical completion status absent: '+str(proof))
        if task['kind'] in ('dhz', 'claims') and data.get('complete') is not True:
            raise ValueError('Incomplete check: '+str(proof))
        if task['kind'] == 'claims':
            expected_checks = {'CE02', 'CE05', 'CE06', 'CE10', 'CE12', 'CE03_table_selection'}
            checks = data.get('checks')
            if (not isinstance(checks, dict) or set(checks) != expected_checks or
                    any(not isinstance(value, dict) or value.get('status') != 'PASS'
                        for value in checks.values())):
                raise ValueError('Paper claims omitted or failed a required exact check')


def terminate(proc, owned_groups):
    group = proc.pid
    if group not in owned_groups or group <= 1 or group == os.getpgrp():
        raise ValueError('Refusing to terminate an unregistered process group')

    def alive():
        proc.poll()  # Reap the leader, but also check for surviving descendants.
        try:
            os.killpg(group, 0)
        except ProcessLookupError:
            return False
        return True

    signals = []
    previous = signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        for signum, grace in ((signal.SIGINT, 45), (signal.SIGTERM, 5), (signal.SIGKILL, 5)):
            if not alive():
                break
            try:
                os.killpg(group, signum)
            except ProcessLookupError:
                break
            signals.append(signal.Signals(signum).name)
            deadline = time.monotonic()+grace
            while alive() and time.monotonic() < deadline:
                time.sleep(0.05)
        return dict(process_group=group, signals=signals,
                    whole_process_group_exited=not alive(), leader_returncode=proc.poll())
    except OSError as error:
        return dict(process_group=group, signals=signals,
                    whole_process_group_exited=False, termination_error=str(error))
    finally:
        signal.signal(signal.SIGINT, previous)


def execute(run, overrides=None):
    lock = (run/'run.lock').open('a+')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise ValueError('This run is already active')
    report = read_json(run/'status.json')
    check_frozen(run, report)
    if overrides:
        report.setdefault('runtime_override_history', []).append(dict(
            at_utc=now(), previous=dict(report['runtime_overrides']), requested=overrides))
        report['runtime_overrides'].update(overrides)
    report['pid'] = os.getpid()
    report['status'] = 'PREFLIGHT'
    save(run, report)
    owned_groups = set()
    try:
        frozen = run/'inputs/repository/verification'
        runtime = load_module(frozen/'runtime_probe.py', 'sl4_runtime')
        validation = load_module(frozen/'validation.py', 'sl4_validation')
        tools = probe_runtimes(runtime, report['profile'], report['runtime_overrides'],
                               output_dir=run/('runtime-'+str(time.time_ns())))
        report['runtimes'] = tools
        paths = {k: v.get('path') for k, v in tools.items() if isinstance(v, dict)}
        needed = ['python'] if report['profile'] == 'portable' else ['python', 'sage', 'gap', 'singular', 'cxx']
        missing = [n for n in needed if tools.get(n, {}).get('status') != 'pass']
        if missing:
            report.update(status='BLOCKED_RUNTIME', error='Required runtime check failed: '+', '.join(missing))
            save(run, report)
            raise ValueError(report['error'])
        env = os.environ.copy()
        env.pop('PYTHONOPTIMIZE', None)
        env.update(PYTHONUNBUFFERED='1', PYTHONDONTWRITEBYTECODE='1', OMP_NUM_THREADS='1')
        bindir = run/'bin'
        bindir.mkdir(exist_ok=True)
        for name, key in [('sage', 'sage'), ('gap', 'gap'), ('Singular', 'singular'),
                          ('singular', 'singular'), ('g++', 'cxx')]:
            if paths.get(key):
                link = bindir/name
                if link.is_symlink():
                    link.unlink()
                link.symlink_to(paths[key])
        env['PATH'] = str(bindir)+os.pathsep+env.get('PATH', '')
        env['SL4_TOOL_BIN'] = str(bindir)
        if paths.get('singular') and tools['singular']['status'] == 'pass':
            env['SL4_SINGULAR'] = paths['singular']
        report['status'] = 'RUNNING'
        report.pop('error', None)
        save(run, report)
        for task in report['tasks']:
            if receipt_valid(run, task):
                print('REUSED PASS '+task['id'], flush=True)
                continue
            if task['status'] == 'PASS':
                raise ValueError('Completed result changed: '+task['id'])
            bad = [key for key in task.get('requires', [])
                   if not receipt_valid(run, next(t for t in report['tasks'] if t['id'] == key))]
            if bad:
                task.update(status='BLOCKED_DEPENDENCY', error='Required stages failed: '+', '.join(bad))
                save(run, report)
                continue
            attempt = run/'steps'/task['id']/('attempt-'+str(len(task['attempts'])+1))
            attempt.mkdir(parents=True)
            entry = dict(directory=str(attempt.relative_to(run)), started_utc=now())
            task['attempts'].append(entry)
            task.update(status='RUNNING')
            task.pop('error', None)
            command, proof = command_for(task, run, attempt, paths, report)
            entry['command'] = command
            save(run, report)
            print('START '+task['id'], flush=True)
            start = time.monotonic()
            cache = attempt/'sage-cache'
            cache.mkdir()
            with (attempt/'stdout.log').open('w') as log:
                proc = None
                try:
                    proc = subprocess.Popen(command, cwd=attempt, env=dict(env, DOT_SAGE=str(cache)),
                                            stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                    owned_groups.add(proc.pid)
                    entry['process_id'] = proc.pid
                    save(run, report)
                    code = proc.wait()
                except BaseException as error:
                    if proc is not None:
                        owned_groups.add(proc.pid)
                        entry['process_group_termination'] = terminate(proc, owned_groups)
                    task['status'] = 'INTERRUPTED' if isinstance(error, KeyboardInterrupt) else 'FAILED'
                    raise
            entry.update(returncode=code, seconds=round(time.monotonic()-start, 2), finished_utc=now())
            try:
                if code:
                    raise ValueError('Exit code '+str(code)+'; see '+str(attempt/'stdout.log'))
                validate(task, attempt, proof, validation)
                evidence = [p for p in attempt.rglob('*')
                            if p.is_file() and p.suffix in ('.json', '.log', '.csv')
                            and 'sage-cache' not in p.parts]
                task['receipt'] = {str(p.relative_to(run)): sha(p) for p in sorted(evidence)}
                task['status'] = 'PASS'
            except (ValueError, OSError, KeyError, TypeError) as error:
                task.update(status='FAILED', error=str(error))
            save(run, report)
            print(task['status']+' '+task['id'], flush=True)
        report['status'] = 'PASS' if all(t['status'] == 'PASS' for t in report['tasks']) else 'FAILED'
    except BaseException as error:
        if report['status'] != 'BLOCKED_RUNTIME':
            report['status'] = 'INTERRUPTED' if isinstance(error, KeyboardInterrupt) else 'FAILED'
        report['error'] = str(error) or type(error).__name__
        raise
    finally:
        report['finished_utc'] = now()
        save(run, report)
    print(report['status']+': '+str(run/'REPORT.txt'), flush=True)
    return 0 if report['status'] == 'PASS' else 1


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profile', choices=['all', 'portable'], default='all')
    p.add_argument('--paper', type=Path, help='Optional external LaTeX manuscript: also check all 106 printed matrix blocks')
    p.add_argument('--run-dir', type=Path)
    p.add_argument('--resume', type=Path)
    p.add_argument('--status', type=Path)
    p.add_argument('--stop', type=Path)
    p.add_argument('--plan', action='store_true')
    p.add_argument('--check-tools', action='store_true')
    p.add_argument('--background', action='store_true')
    for name in RUNTIME_NAMES:
        p.add_argument('--'+name)
    a = p.parse_args()
    if sys.flags.optimize or os.environ.get('PYTHONOPTIMIZE'):
        p.error('Run without -O or PYTHONOPTIMIZE; assertions are mathematical checks')
    for name in RUNTIME_NAMES:
        value = getattr(a, name)
        if value is not None and (os.sep in value or value.startswith('~')):
            setattr(a, name, str(Path(value).expanduser().resolve()))
    overrides = {name: getattr(a, name) for name in RUNTIME_NAMES
                 if getattr(a, name) is not None}
    if a.status:
        print((a.status.resolve()/'REPORT.txt').read_text())
        return 0
    if a.stop:
        run = a.stop.resolve()
        with (run/'run.lock').open('a+') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                print('No active worker holds this run lock')
                return 0
            except BlockingIOError:
                pass
            pid = read_json(run/'status.json')['pid']
            os.kill(pid, signal.SIGINT)
            print('Requested an orderly stop of run '+str(run))
        return 0
    if a.plan:
        print(json.dumps(make_plan(a.profile, a.paper is not None), indent=2))
        return 0
    if a.check_tools:
        runtime = load_module(SUPPORT/'runtime_probe.py', 'runtime_probe')
        result = probe_runtimes(runtime, a.profile,
                               {name: getattr(a, name) for name in RUNTIME_NAMES})
        print(json.dumps(result, indent=2))
        required = () if a.profile == 'portable' else ('sage', 'gap', 'singular', 'cxx')
        return 0 if all(result.get(name, {}).get('status') == 'pass' for name in required) else 1
    run = a.resume.resolve() if a.resume else prepare(a)
    controller = (run/'inputs/repository/reproduce.py').resolve()
    # Check the frozen code before executing it, including when the live
    # launcher has been edited since this calculation was prepared.
    if Path(__file__).resolve() != controller:
        check_frozen(run, read_json(run/'status.json'))
    command = [sys.executable, str(controller), '--resume', str(run)]
    for name, value in overrides.items():
        command += ['--'+name, value]
    if a.background:
        with (run/'controller.log').open('a') as log:
            cmd = command
            if Path('/usr/bin/caffeinate').exists():
                cmd = ['/usr/bin/caffeinate', '-i']+cmd
            child = subprocess.Popen(cmd, cwd=run, stdout=log, stderr=subprocess.STDOUT,
                                     stdin=subprocess.DEVNULL, start_new_session=True)
        print('Started local worker. Process '+str(child.pid))
        print('Report: '+str(run/'REPORT.txt'))
        print('Log: '+str(run/'controller.log'))
        return 0
    if Path(__file__).resolve() != controller:
        os.execv(sys.executable, command)
    return execute(run, overrides)


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print('Interrupted. Use --resume to retain completed stages.', file=sys.stderr)
        raise SystemExit(130)
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
