"""Exact standard-library audit of CE03/CE07; geometry is reused, not reproved.

Run with Python 3.9+: --output-dir NEW_EMPTY_DIRECTORY_OUTSIDE_REPOSITORY.
All 106 invariant alternating-form spaces and age/order collision keys are checked.
The eight target groups are freshly closed and their age classes, junior generation,
character norms and first ten Molien coefficients are independently calculated.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from itertools import combinations, product
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'manuscript106/catalogue/catalogue.json'
TARGETS = (35, 38, 55, 64, 86, 97, 98, 105)
COORDS = tuple(combinations(range(4), 2))
IDENTITY = tuple(tuple(int(i == j) for j in range(4)) for i in range(4))


def transpose(a):
    return tuple(zip(*a))


def multiply(a, b):
    return tuple(tuple(sum(x*y for x, y in zip(r, c))
                       for c in transpose(b)) for r in a)


def subtract(a, b):
    return tuple(tuple(x-y for x, y in zip(r, s)) for r, s in zip(a, b))


def kernel(equations, columns):
    a = [[Q(x) for x in row] for row in equations]
    pivots = []
    row = 0
    for col in range(columns):
        pivot = next((k for k in range(row, len(a)) if a[k][col]), None)
        if pivot is None:
            continue
        a[row], a[pivot] = a[pivot], a[row]
        scale = a[row][col]
        a[row] = [x / scale for x in a[row]]
        for k in range(len(a)):
            if k != row and a[k][col]:
                scale = a[k][col]
                a[k] = [x-scale*y for x, y in zip(a[k], a[row])]
        pivots.append(col)
        row += 1
    answer = []
    for col in sorted(set(range(columns))-set(pivots)):
        v = [Q(0)] * columns
        v[col] = Q(1)
        for k, p in enumerate(pivots):
            v[p] = -a[k][col]
        answer.append(v)
    return answer


def alternating(generators):
    basis = []
    for i, j in COORDS:
        b = [[0]*4 for _ in range(4)]
        b[i][j], b[j][i] = 1, -1
        basis.append(tuple(map(tuple, b)))
    equations = []
    for g in generators:
        differences = [subtract(multiply(multiply(transpose(g), b), g), b)
                       for b in basis]
        equations.extend([[d[i][j] for d in differences] for i, j in COORDS])
    k = kernel(equations, 6)
    witness = None
    # The Pfaffian has degree at most two in each parameter. Vanishing on the
    # entire three-point Cartesian grid is therefore equivalent to being zero.
    for coefficients in product((-1, 0, 1), repeat=len(k)):
        v = [sum(c*b[i] for c, b in zip(coefficients, k)) for i in range(6)]
        if v[0]*v[5]-v[1]*v[4]+v[2]*v[3]:
            witness = list(map(str, v))
            break
    return {'invariant_alternating_form_dimension': len(k),
            'symplectic': witness is not None,
            'kernel_basis_in_12_13_14_23_24_34': [list(map(str, v)) for v in k],
            'nondegenerate_form_coordinates': witness}


def closure(generators, bound):
    found, queue = {IDENTITY}, [IDENTITY]
    for a in queue:
        for g in generators:
            b = multiply(a, g)
            if b not in found:
                found.add(b)
                queue.append(b)
                assert len(queue) <= bound
    return found


def age(g):
    codimension = 4-len(kernel(subtract(IDENTITY, g), 4))
    assert codimension % 2 == 0
    # Finite rational SL4 matrices have reciprocal eigenvalue pairs.
    return codimension // 2


def inverse(g, bound):
    result = IDENTITY
    for _ in range(bound):
        if multiply(result, g) == IDENTITY:
            return result
        result = multiply(result, g)
    raise AssertionError('Generator order exceeds group order')


def verify_group(row, generators):
    group = closure(generators, row['order'])
    assert len(group) == row['order']
    juniors = [g for g in group if age(g) == 1]
    junior_group = closure(juniors, row['order'])
    pairs = [(g, inverse(g, row['order'])) for g in generators]
    remaining = set(group)
    counts = Counter()
    while remaining:
        first = min(remaining)
        orbit, queue = {first}, [first]
        for a in queue:
            for g, inv in pairs:
                b = multiply(multiply(g, a), inv)
                if b not in orbit:
                    orbit.add(b)
                    queue.append(b)
        assert orbit <= remaining
        remaining -= orbit
        counts[age(first)] += 1
    assert counts == {0: 1, 1: row['junior_classes'], 2: row['age2_classes']}
    molien = [Q(0)]*10
    for polynomial, multiplicity in row['characteristic_polynomial_distribution']:
        reciprocal = [Q(1)]
        for degree in range(1, 10):
            reciprocal.append(-sum(Q(polynomial[j])*reciprocal[degree-j]
                                   for j in range(1, min(degree, 4)+1)))
        molien = [a+Q(multiplicity, len(group))*b
                  for a, b in zip(molien, reciprocal)]
    # An independent trace calculation verifies the degree-two Molien value.
    trace = lambda a: sum(a[i][i] for i in range(4))
    degree_two = sum(Q(trace(g)**2+trace(multiply(g, g)), 2)
                     for g in group) / len(group)
    assert degree_two == molien[2]
    return {'closed_group_order': len(group),
            'junior_elements': len(juniors),
            'junior_generated_order': len(junior_group),
            'generated_by_juniors': junior_group == group,
            'fresh_age_class_counts': dict(sorted(counts.items())),
            'complex_character_norm': str(sum(trace(g)**2 for g in group)/Q(len(group))),
            'molien_coefficients_degrees_0_through_9': list(map(str, molien)),
            'fresh_trace_formula_degree_two_molien': str(degree_two)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error('Assertions must remain enabled')
    output = args.output_dir.resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error('Use an output directory outside the repository')
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        parser.error('Output directory must be new or empty')
    output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    rows = json.loads(SOURCE.read_text())
    assert [r['index'] for r in rows] == list(range(1, 107))
    blocks = defaultdict(list)
    forms, targets = [], []
    for row in rows:
        generators = [tuple(map(tuple, g)) for g in row['actual_generators']]
        assert all(isinstance(x, int) for g in generators for r in g for x in r)
        form = alternating(generators)
        forms.append({'case': row['index'], **form})
        blocks[(row['order'], row['junior_classes'], row['age2_classes'])].append(row)
        if row['index'] in TARGETS:
            result = {'case': row['index'], 'decision': row['decision'],
                      **form, **verify_group(row, generators)}
            targets.append(result)
    collisions = [{'order': key[0], 'age_class_counts': [1, key[1], key[2]],
                   'cases': [{'case': r['index'], 'decision': r['decision']} for r in block]}
                  for key, block in sorted(blocks.items())
                  if len({r['decision'] for r in block}) > 1]
    assert not collisions
    assert [r['case'] for r in targets if r['symplectic']] == [38]
    assert all(r['invariant_alternating_form_dimension'] == 0
               for r in targets if r['case'] != 38)
    assert all(r['generated_by_juniors'] for r in targets)
    result = {'status': 'PASS', 'python_version': sys.version,
              'scope': 'Exact rational linear algebra and finite-group calculations. '
                       'Geometric YES/NO decisions are reused, not reproved. '
                       'All106 age/order scan uses accepted catalogue class counts; '
                       'the eight target age class counts are freshly recomputed.',
              'catalogue_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              'program_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'catalogue_entries_checked': len(rows),
              'distinct_order_age_keys': len(blocks),
              'opposite_decision_equal_order_and_age_pairs': collisions,
              'all106_alternating_form_checks': forms, 'target_checks': targets,
              'seconds': round(time.monotonic()-started, 3)}
    (output/'ce03_ce07.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items()
                      if k != 'all106_alternating_form_checks'}, indent=2))


if __name__ == '__main__':
    main()
