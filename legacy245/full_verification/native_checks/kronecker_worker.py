#!/usr/bin/env python3
"""Isolated Sage worker for exact rational Kronecker images. Never import the verifier's __main__."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import traceback


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--request', required=True)
    parser.add_argument('--helper', required=True)
    parser.add_argument('--helper-sha256', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--events', required=True)
    args = parser.parse_args()
    request = json.loads(Path(args.request).read_text())
    identity = dict(request_sha256=digest(args.request),
                    helper_sha256=digest(args.helper), worker_id=request['worker_id'],
                    indices=request['indices'], pid=os.getpid())
    assert identity['helper_sha256'] == args.helper_sha256
    with Path(args.events).open('x') as stream:
        def emit(event, **payload):
            stream.write(json.dumps(dict(event=event, **payload), sort_keys=True) + '\n')
            stream.flush()
        try:
            from sage.all import QQ, PolynomialRing
            U = PolynomialRing(QQ, names=tuple('u' + str(j) for j in range(request['input_variables'])))
            X = PolynomialRing(QQ, names=tuple('x' + str(j) for j in range(request['physical_variables'])))
            def decode(ring, rows):
                data = {}
                for exponent, coefficient in rows:
                    e = tuple(exponent)
                    assert len(e) == ring.ngens() and all(type(v) is int and v >= 0 for v in e)
                    assert e not in data and QQ(coefficient) != 0
                    data[e] = QQ(coefficient)
                if ring.ngens() == 1:
                    return ring({e[0]: c for e, c in data.items()})
                return ring(data)
            polynomials = [decode(U, rows) for rows in request['polynomials']]
            images = [decode(X, rows) for rows in request['images']]
            assert len(polynomials) == len(request['indices']) > 0
            spec = importlib.util.spec_from_file_location('verified_serial_kronecker', args.helper)
            helper = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(helper)
            emit('PARALLEL_KRONECKER_WORKER_READY', worker_id=request['worker_id'], pid=os.getpid())
            result = helper.verify_zero_images(polynomials, images, emit)
            assert digest(args.helper) == identity['helper_sha256']
            assert digest(args.request) == identity['request_sha256']
            write_json(args.output, dict(status='PASS', result=result, **identity))
        except BaseException as error:
            write_json(args.output, dict(status='ERROR', error=repr(error), **identity))
            traceback.print_exc()
            return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
