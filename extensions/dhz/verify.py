#!/usr/bin/env python3
"""Run fresh DHZ invariant-ring checks with a private Sage cache.

Case numbers are 45,65,66,105 in the manuscript. Omit --case for all four.
This launcher runs with ordinary Python3 or sage -python.
"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',type=int,choices=[45,65,66,105],action='append')
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--sage',default=shutil.which('sage'))
    args = parser.parse_args()
    if sys.flags.optimize:parser.error('Do not use -O or PYTHONOPTIMIZE')
    if not args.sage:parser.error('SageMath executable unavailable; supply --sage')
    if args.case and len(set(args.case))!=len(args.case):parser.error('Duplicate case selection')
    command = [args.sage,'-python',str(HERE/'worker.py'),'--output-dir',str(args.output_dir.resolve())]
    for case in args.case or []:command.extend(['--case',str(case)])
    with tempfile.TemporaryDirectory(prefix='sl4-dhz-sage-') as cache:
        env = os.environ.copy()
        env['DOT_SAGE'] = cache
        env.pop('PYTHONOPTIMIZE',None)
        result = subprocess.run(command,env=env,check=False)
    return result.returncode


if __name__=='__main__':raise SystemExit(main())
