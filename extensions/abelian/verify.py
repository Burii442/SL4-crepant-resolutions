#!/usr/bin/env python3
"""Bind the saved abelian lattices to the actual integral matrix generators.

Only Python's standard library and GAP are needed. This complements the Sage
fan verification; it does not replace coherence, smoothness or coverage tests.
"""
import argparse
import csv
from fractions import Fraction
import hashlib
from itertools import permutations
import json
from pathlib import Path
import shutil
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def points(text):
    return {tuple(Fraction(x) for x in row.split(',')) for row in text.split(';') if row}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output-dir', type=Path, required=True)
    ap.add_argument('--gap', default=shutil.which('gap'))
    ap.add_argument('--legacy-case', type=int, help='One old 245-catalogue index; default: all abelian entries')
    args = ap.parse_args()
    if not args.gap:
        ap.error('GAP is unavailable; pass --gap /path/to/gap')
    out = args.output_dir.resolve()
    if out == ROOT or ROOT in out.parents:
        ap.error('Use a fresh output directory outside the repository')
    if out.exists() and any(out.iterdir()):
        ap.error('Output directory must be new or empty')
    out.mkdir(parents=True, exist_ok=True)
    catalogue = ROOT / 'legacy245/catalogue.json'
    saved = ROOT / 'legacy245/abelian_characters.csv'
    data = json.loads(catalogue.read_text())
    with saved.open() as stream:
        expected = {int(r['index']): r for r in csv.DictReader(stream)}
    if args.legacy_case is not None and args.legacy_case not in expected:
        ap.error('The selected old index is not an abelian catalogue entry')
    selection = sorted(expected) if args.legacy_case is None else [args.legacy_case]
    # GAP and JSON share the literal syntax of these integer matrix lists.
    (out / 'matrices.g').write_text('ASL4 := ' + json.dumps([r['actual_generators'] for r in data]) + ';;\n')
    driver = '\n'.join([
        'SLDataFile := ' + json.dumps(str(out / 'matrices.g')) + ';;',
        'SLVariableName := "ASL4";;',
        'SLDimension := 4;;',
        'SLSelectedIndices := ' + json.dumps(selection) + ';;',
        'SLOutputFile := ' + json.dumps(str(out / 'actual_characters.csv')) + ';;',
        'Read(' + json.dumps(str(HERE / 'export_characters.g')) + ');',
    ])
    (out / 'run.g').write_text(driver + '\n')
    report = {'status': 'RUNNING', 'legacy_indices': selection, 'scope': 'Exact character lattices from the actual catalogue matrices, up to coordinate permutation; fan geometry is a separate check.',
              'input_sha256': {str(p.relative_to(ROOT)): sha(p) for p in [catalogue, saved, HERE / 'export_characters.g', Path(__file__)]}}
    reportpath = out / 'report.json'
    reportpath.write_text(json.dumps(report, indent=2) + '\n')
    start = time.monotonic()
    try:
        with (out / 'stdout.log').open('w') as log:
            proc = subprocess.run([args.gap, '-q', str(out / 'run.g')], stdout=log, stderr=subprocess.STDOUT)
        if proc.returncode:
            raise ValueError('GAP failed; inspect stdout.log')
        with (out / 'actual_characters.csv').open() as stream:
            actual = {int(r['index']): r for r in csv.DictReader(stream)}
        if sorted(actual) != selection:
            raise ValueError('The character export did not complete the requested scope')
        matches = []
        for i in selection:
            old, new = points(expected[i]['fractional_points']), points(actual[i]['fractional_points'])
            order = data[i - 1]['order']
            if not (len(old) == len(new) == order == int(actual[i]['order'])):
                raise ValueError(f'{i}: incorrect number of distinct character vectors')
            perms = [p for p in permutations(range(4)) if {tuple(v[k] for k in p) for v in new} == old]
            if not perms:
                raise ValueError(f'{i}: actual and saved quotient lattices differ')
            matches.append({'legacy_case': i, 'order': order, 'actual_to_saved_coordinate_permutation': list(perms[0]),
                            'fractional_vectors': len(new), 'junior_vectors': sum(sum(v) == 1 for v in new)})
        report.update(status='PASS', cases=matches, checked=len(matches), actual_character_csv_sha256=sha(out / 'actual_characters.csv'))
    except BaseException as error:
        report.update(status='FAILED', error=str(error))
        raise
    finally:
        report.update(seconds=round(time.monotonic() - start, 3))
        reportpath.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'checked': report['checked'], 'report': str(reportpath)}))


if __name__ == '__main__':
    main()
