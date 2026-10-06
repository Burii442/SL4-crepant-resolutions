#!/usr/bin/env python3
"""Verify that the ten criteria cover the catalogue with consistent decisions.

This checks the recorded applicability relation, not the geometric proofs
that establish its entries. Requires only the Python standard library.
"""
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
cases = {d['index']: d for d in json.loads((HERE/'catalogue.json').read_text())}
assert set(cases) == set(range(1, 246))
cover = {}
with (HERE/'criteria_incidence.csv').open(newline='') as stream:
    for row in csv.DictReader(stream):
        i = int(row['index'])
        assert row['outcome'] == cases[i]['decision']
        cover.setdefault(row['test'], set()).add(i)
assert set(cover) == set('ABCDEGHIUZ')
assert set().union(*cover.values()) == set(cases)
for i, record in cases.items():
    assert i in cover[record['family']]
result = {'cases':245, 'decisions':dict(Counter(d['decision'] for d in cases.values())),
          'criteria':sorted(cover), 'all_cases_covered':True,
          'scope':'Coverage and consistency of the ten recorded applicability sets.'}
(HERE/'criteria_verification.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
