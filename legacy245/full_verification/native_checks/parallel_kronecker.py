"""Exact parallel orchestration of the unchanged serial QQ[T] helper.

The work is only partitioned, never approximated. Workers load a byte-for-byte
copy of the serial helper. A PASS requires every worker to exit successfully,
the entire serial protocol for every assigned input, and exact index coverage.
Only then are the original IMAGE_ZERO events replayed in input order.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time

HERE = Path(__file__).resolve().parent
PUBLIC = HERE.parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    temporary.replace(path)


def prepare(polynomials, images):
    """Repeat every serial precondition before starting any process."""
    from sage.all import QQ
    polynomials, images = list(polynomials), list(images)
    assert polynomials and images, 'Nonempty typed inputs are required'
    U, X = polynomials[0].parent(), images[0].parent()
    assert U.ngens() == len(images) and X.ngens() >= 2
    assert all(f.parent() is U for f in polynomials)
    assert all(f.parent() is X for f in images)
    for ring in (U, X):
        K = ring.base_ring()
        assert K.is_field() and K.is_exact() and K.characteristic() == 0
    assert all(c in QQ for f in polynomials + images for c in f.coefficients()), 'Rational coefficients are required'
    assert all(f and f.is_homogeneous() for f in images), 'Every image must be nonzero and homogeneous'
    def encode(f):
        def exponent(e):
            return tuple(int(v) for v in e) if hasattr(e, '__iter__') else (int(e),)
        return [[list(exponent(e)), str(QQ(c))] for e, c in sorted(f.dict().items())]
    inputs, forms = [encode(f) for f in polynomials], [encode(f) for f in images]
    degrees = [int(f.total_degree()) for f in images]
    weighted = []
    for rows in inputs:
        ds = {sum(e[j] * degrees[j] for j in range(len(images))) for e, c in rows}
        assert len(ds) <= 1, 'Kronecker dehomogenization requires a homogeneous image degree'
        weighted.append(next(iter(ds), 0))
    return dict(input_variables=U.ngens(), physical_variables=X.ngens(),
                polynomials=inputs, images=forms), weighted


def partition(data, weighted, workers):
    """Deterministic longest-estimated-job-first assignment, original tie order."""
    costs = [(max(1, d + 1) ** (data['physical_variables'] - 1)) * max(1, len(rows))
             for d, rows in zip(weighted, data['polynomials'])]
    groups, loads = [[] for _ in range(workers)], [0] * workers
    for index in sorted(range(len(costs)), key=lambda i: (-costs[i], i)):
        worker = min(range(workers), key=lambda j: (loads[j], j))
        groups[worker].append(index)
        loads[worker] += costs[index]
    return [sorted(group) for group in groups], loads


def verify_worker(record, helper_sha, weighted, data):
    """Strict complete serial protocol; never treat partial output as evidence."""
    result = json.loads(record['output'].read_text())
    indices = record['indices']
    assert result['status'] == 'PASS', result
    assert result['request_sha256'] == record['request_sha256'] == digest(record['request'])
    assert result['helper_sha256'] == helper_sha
    assert result['worker_id'] == record['id'] and result['indices'] == indices
    assert result['pid'] == record['process'].pid
    proof = result['result']
    assert proof == dict(all_zero=True, checked=len(indices), characteristic=0,
                         coefficient_field='QQ', method='injective homogeneous Kronecker encoding in QQ[T]')
    events = [json.loads(line) for line in record['events'].read_text().splitlines()]
    assert len(events) == len(indices) + 3
    assert events[0] == dict(event='PARALLEL_KRONECKER_WORKER_READY', worker_id=record['id'], pid=result['pid'])
    assert events[1] == dict(event='EXACT_KRONECKER_IMAGES_START', count=len(indices), characteristic=0,
                            physical_variables=data['physical_variables'], maximum_homogeneous_degree=max(weighted[i-1] for i in indices))
    assert events[-1] == dict(event='EXACT_KRONECKER_IMAGES_COMPLETE', count=len(indices), characteristic=0)
    mapped = {}
    for local, index in enumerate(indices, 1):
        event = events[local + 1]
        d = weighted[index - 1]
        expected = dict(event='EXACT_KRONECKER_IMAGE_ZERO', index=local, homogeneous_degree=d)
        if not data['polynomials'][index - 1]:
            expected['zero_input'] = True
        else:
            expected.update(radix=d + 1, univariate_degree_bound=d * (d + 1) ** (data['physical_variables'] - 2))
        assert event == expected, (index, event, expected)
        mapped[index] = dict(event, index=index)
    return mapped


def verify_zero_images(polynomials, images, emit=lambda *a, **k: None, *,
                       workers=2, work_directory=None, timeout_seconds=None,
                       serial_helper=None, runtime_helper=None):
    """Typed inputs; 2--4 workers using this Sage Python, with retained evidence.

    Errors and interruption propagate after bounded cleanup of every owned
    process group. The optional timeout is a failure to obtain a certificate.
    No output directory or cache is deleted while a known group might survive.
    """
    assert type(workers) is int and 2 <= workers <= 4
    assert threading.current_thread() is threading.main_thread(), 'Signal-safe orchestration requires the main thread'
    if timeout_seconds is not None:
        assert float(timeout_seconds) > 0
    data, weighted = prepare(polynomials, images)
    worker_count = min(workers, len(weighted))
    groups, loads = partition(data, weighted, worker_count)
    directory = Path(work_directory) if work_directory else Path(tempfile.mkdtemp(prefix='parallel-kronecker-'))
    directory = directory.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    assert not list(directory.iterdir()), 'Use a fresh empty evidence directory'
    source = Path(serial_helper) if serial_helper else PUBLIC / 'full_verification/native_checks/kronecker_images.py'
    runtime = Path(runtime_helper) if runtime_helper else PUBLIC / 'runtime_cache.py'
    frozen = directory / 'sources'
    frozen.mkdir()
    for path, name in [(source, 'kronecker_images.py'), (runtime, 'runtime_cache.py'), (HERE / 'kronecker_worker.py', 'worker.py'), (Path(__file__), 'parallel_kronecker.py')]:
        shutil.copy2(path, frozen / name)
    helper_sha = digest(frozen / 'kronecker_images.py')
    original_source_sha = digest(source)
    assert original_source_sha == helper_sha
    manifest = {p.name: digest(p) for p in frozen.iterdir()}
    write_json(directory / 'source_manifest.json', manifest)
    spec = importlib.util.spec_from_file_location('parallel_runtime_cache', frozen / 'runtime_cache.py')
    cache_tools = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cache_tools)
    records, registered = [], []
    started = time.monotonic()
    outcome = dict(status='RUNNING', characteristic=0, checked=0, count=len(weighted),
                   source_manifest=manifest, assignments=[[i+1 for i in g] for g in groups],
                   estimated_loads=loads, worker_count=worker_count)
    write_json(directory / 'result.json', outcome)
    old_handlers = {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM)}
    in_spawn = False
    pending_signal = None
    def interrupted(signum, frame):
        nonlocal pending_signal
        if in_spawn:
            pending_signal = signum
            return
        raise KeyboardInterrupt('Parallel Kronecker interrupted by ' + signal.Signals(signum).name)
    for sig in old_handlers:
        signal.signal(sig, interrupted)
    try:
        emit('EXACT_KRONECKER_IMAGES_START', count=len(weighted), characteristic=0,
             physical_variables=data['physical_variables'], maximum_homogeneous_degree=max(weighted))
        emit('PARALLEL_KRONECKER_START', workers=worker_count, assignments=outcome['assignments'], evidence_directory=str(directory))
        for worker_id, group in enumerate(groups, 1):
            folder = directory / ('worker_' + str(worker_id))
            folder.mkdir()
            request = dict(data, worker_id=worker_id, indices=[i+1 for i in group], polynomials=[data['polynomials'][i] for i in group])
            input_path, output_path, event_path = folder / 'request.json', folder / 'result.json', folder / 'events.jsonl'
            write_json(input_path, request)
            cache = cache_tools.allocate_sage_cache(folder / 'sage_cache')
            env = dict(os.environ, DOT_SAGE=str(cache.path), PYTHONUNBUFFERED='1')
            log = (folder / 'worker.log').open('xb')
            record = dict(id=worker_id, request=input_path, output=output_path, events=event_path,
                          indices=request['indices'], request_sha256=digest(input_path), cache=cache, log=log, process=None, lines_seen=0)
            records.append(record)
            # Defer signals only across spawn + ownership registration, so a
            # just-created child cannot be lost between these two operations.
            in_spawn = True
            try:
                process = subprocess.Popen([sys.executable, str(frozen / 'worker.py'), '--request', str(input_path),
                    '--helper', str(frozen / 'kronecker_images.py'), '--helper-sha256', helper_sha,
                    '--output', str(output_path), '--events', str(event_path)],
                    env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                record['process'] = process
                registered.append(process.pid)
            finally:
                in_spawn = False
            if pending_signal is not None:
                interrupted(pending_signal, None)
            emit('PARALLEL_KRONECKER_WORKER_STARTED', worker_id=worker_id, pid=process.pid, count=len(group))
        complete = set()
        mapped = {}
        while len(complete) < worker_count:
            if timeout_seconds is not None and time.monotonic() - started > float(timeout_seconds):
                raise TimeoutError('Parallel Kronecker certificate timed out')
            for record in records:
                if record['id'] in complete:
                    continue
                # Only newline-terminated records count as progress. They are
                # not mathematical evidence until verify_worker succeeds.
                if record['events'].exists():
                    lines = record['events'].read_text().splitlines(keepends=True)
                    lines = [line for line in lines if line.endswith('\n')]
                    if len(lines) > record['lines_seen']:
                        record['lines_seen'] = len(lines)
                        emit('PARALLEL_KRONECKER_PROGRESS', worker_id=record['id'], flushed_records=len(lines))
                code = record['process'].poll()
                if code is None:
                    continue
                if code != 0:
                    raise RuntimeError(f'Kronecker worker {record["id"]} exited with {code}; see {record["log"].name}')
                result = verify_worker(record, helper_sha, weighted, data)
                assert not set(mapped).intersection(result)
                mapped.update(result)
                complete.add(record['id'])
                emit('PARALLEL_KRONECKER_WORKER_COMPLETE', worker_id=record['id'], checked=len(result))
            if len(complete) < worker_count:
                time.sleep(0.05)
        assert sorted(mapped) == list(range(1, len(weighted) + 1))
        assert digest(source) == original_source_sha
        assert all(digest(frozen / name) == sha for name, sha in manifest.items())
        assert all(digest(r['request']) == r['request_sha256'] for r in records)
        outcome['literal_request_sha256'] = {str(r['id']): r['request_sha256'] for r in records}
        outcome['all_worker_inputs_and_sources_unchanged'] = True
        outcome.update(status='PASS', checked=len(mapped), all_zero=True, coefficient_field='QQ',
                       method='injective homogeneous Kronecker encoding in QQ[T]')
    except BaseException as error:
        outcome.update(status='INTERRUPTED' if isinstance(error, KeyboardInterrupt) else 'ERROR', error=repr(error))
        raise
    finally:
        # A second signal cannot skip cleanup of later owned groups.
        for sig in old_handlers:
            signal.signal(sig, signal.SIG_IGN)
        cleanup = []
        try:
            for record in records:
                process = record['process']
                termination = cache_tools.terminate_owned_process_group(process, registered, grace_seconds=1.0) if process else None
                # On macOS the group query can transiently return EPERM while
                # a terminated process is disappearing. Preserve that report;
                # perform only a bounded read-only recheck, never a second kill.
                group_exited = process is None or termination['whole_process_group_exited']
                if process is not None and not group_exited:
                    deadline = time.monotonic() + 1.0
                    while time.monotonic() < deadline:
                        process.poll()
                        try:
                            os.killpg(process.pid, 0)
                        except ProcessLookupError:
                            group_exited = True
                            break
                        except OSError:
                            pass
                        time.sleep(0.02)
                record['log'].close()
                cleanup.append(dict(worker_id=record['id'], termination=termination,
                    whole_process_group_exited=group_exited,
                    cache=record['cache'].metadata(), cache_cleanup=record['cache'].cleanup([process.pid] if process else [])))
            outcome['cleanup'] = cleanup
            if outcome['status'] == 'PASS' and not all(r['whole_process_group_exited'] for r in cleanup):
                outcome.update(status='ERROR', error='Worker process group termination was not verified')
            outcome['parallel_elapsed_seconds'] = time.monotonic() - started
            write_json(directory / 'result.json', outcome)
        finally:
            for sig, handler in old_handlers.items():
                signal.signal(sig, handler)
    assert outcome['status'] == 'PASS', outcome
    for index in range(1, len(weighted) + 1):
        event = dict(mapped[index])
        name = event.pop('event')
        emit(name, **event)
    emit('EXACT_KRONECKER_IMAGES_COMPLETE', count=len(weighted), characteristic=0)
    return {key: outcome[key] for key in ('all_zero', 'checked', 'characteristic', 'coefficient_field', 'method')}
