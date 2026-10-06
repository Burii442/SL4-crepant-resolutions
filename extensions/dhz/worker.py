#!/usr/bin/env python3
"""Fresh full invariant-ring and minimal-CI proofs for four manuscript DHZ cases.

Run with sage -python. This command does not assert Cox nonexistence.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CASES = {45:140,65:178,66:179,105:243}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',type=int,choices=sorted(CASES),action='append',
                        help='Manuscript case; may be repeated. Default: all four.')
    parser.add_argument('--output-dir',type=Path,required=True,
                        help='New or empty directory outside this repository')
    args = parser.parse_args()
    if sys.flags.optimize:
        parser.error('Python optimization disables mathematical assertions; do not use -O or PYTHONOPTIMIZE')
    cases = args.case or sorted(CASES)
    if len(set(cases)) != len(cases):parser.error('Duplicate case selection')
    out = args.output_dir.resolve()
    if out==REPO or REPO in out.parents:parser.error('Output must be outside the repository')
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        parser.error('Output directory must be new or empty')
    out.mkdir(parents=True,exist_ok=True)
    os.environ.pop('PYTHONOPTIMIZE',None)
    os.environ.setdefault('DOT_SAGE',str(out/'sage-cache'))
    start = time.monotonic()
    catalogue = REPO/'legacy245/catalogue.json'
    reduced = REPO/'manuscript106/catalogue/catalogue_reduced.json'
    proof_files = ['verify.py','worker.py','common.py','small_ci.py','rotation_ci.py',
                   'rotation_bindings.json','singular/invariants_140.sing',
                   'singular/invariants_243.sing','singular/vendor/finvar.lib']
    inputs = [catalogue,reduced]+[HERE/name for name in proof_files]
    hashes = {str(p.relative_to(REPO)):digest(p) for p in inputs}
    report = {'status':'RUNNING','complete':False,'requested_cases':cases,'results':[],
              'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'scope':'Fresh full-group invariant rings, exact minimal CI presentations and actual matrix bindings. Cox nonexistence is a separate calculation.',
              'cox_nonexistence_recomputed':False,'input_sha256':hashes}
    path = out/'report.json'
    def save():path.write_text(json.dumps(report,indent=2)+'\n')
    save()
    try:
        from common import require
        from sage.version import version as sage_version
        report['sage_version'] = sage_version
        old = {r['index']:r for r in json.loads(catalogue.read_text())}
        current = {r['index']:r for r in json.loads(reduced.read_text())}
        require(len(old)==245 and len(current)==106,'Incomplete catalogues')
        for case in cases:
            source = CASES[case]
            require(current[case]['source_index']==source,'Manuscript/source number mismatch')
            require(current[case]['actual_generators']==old[source]['actual_generators'],
                    'Manuscript and original matrix input disagree')
            target = out/str(case)
            target.mkdir()
            print('DHZ_INVARIANTS_START',case,'source',source,flush=True)
            if source in [140,243]:
                from small_ci import run
            else:
                from rotation_ci import run
            result = run(source,old[source],HERE,target)
            require(all(result.get(key) is True for key in
                    ['actual_catalogue_binding','full_invariant_ring','complete_relation_kernel',
                     'complete_intersection','minimal_embedding']), 'Incomplete invariant-ring proof')
            result.update(paper_case=case,source_case=source,status='PASS',complete=True)
            (target/'certificate.json').write_text(json.dumps(result,indent=2)+'\n')
            report['results'].append(result)
            save()
            print('DHZ_INVARIANTS_PASS',case,flush=True)
        require(hashes=={name:digest(REPO/name) for name in hashes},'Proof input changed during run')
        require([x['paper_case'] for x in report['results']]==cases,'Incomplete selected-case coverage')
        report.update(status='ALL_REQUESTED_DHZ_INVARIANT_CHECKS_PASS',complete=True)
    except BaseException as error:
        report.update(status='FAILED',complete=False,error=type(error).__name__+': '+str(error))
        raise
    finally:
        report['seconds'] = round(time.monotonic()-start,3)
        save()
    print(report['status'],cases,flush=True)


if __name__=='__main__':main()
