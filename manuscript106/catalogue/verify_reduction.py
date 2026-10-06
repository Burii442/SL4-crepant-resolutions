#!/usr/bin/env python3
"""Reconstruct the 245 groups and verify the 106-class reduction over Q.

Uses Python's standard library only. No old PASS result or GAP group closure
is used. All 139 witnesses are checked by equality of complete matrix sets.
"""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import time

HERE = Path(__file__).resolve().parent
INPUT = HERE / 'catalogue_245.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
one = tuple(tuple(int(i == j) for j in range(4)) for i in range(4))

def mat(a):
    return tuple(tuple(row) for row in a)

def mul(a, b):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(4))
                       for j in range(4)) for i in range(4))

def det(a):
    a = [list(map(Fraction, row)) for row in a]
    d = Fraction(1)
    for j in range(4):
        pivot = next((k for k in range(j, 4) if a[k][j]), None)
        if pivot is None:
            return 0
        if pivot != j:
            a[j], a[pivot] = a[pivot], a[j]
            d = -d
        d *= a[j][j]
        for k in range(j+1, 4):
            q = a[k][j]/a[j][j]
            for l in range(j+1, 4):
                a[k][l] -= q*a[j][l]
    return d

def closure(gens, expected):
    gens = [mat(g) for g in gens]
    assert all(det(g) == 1 for g in gens)
    seen = {one}
    elements = [one]
    for x in elements:
        for g in gens:
            y = mul(x, g)
            if y not in seen:
                seen.add(y)
                elements.append(y)
                assert len(elements) <= expected, 'Expected finite order exceeded'
    assert len(elements) == expected
    return seen

def charpoly(g):
    # det(tI-g), ascending coefficients. det(g)=1 follows from the generators.
    p1 = sum(g[i][i] for i in range(4))
    g2 = mul(g, g)
    p2 = sum(g2[i][i] for i in range(4))
    p3 = sum(g2[i][j]*g[j][i] for i in range(4) for j in range(4))
    assert (p1*p1-p2) % 2 == 0
    assert (p1**3-3*p1*p2+2*p3) % 6 == 0
    return (1, -(p1**3-3*p1*p2+2*p3)//6, (p1*p1-p2)//2, -p1, 1)

def main():
    start = time.monotonic()
    original = json.loads(INPUT.read_text())
    cert = json.loads((HERE/'conjugacy_certificates.json').read_text())
    assert sha(INPUT) == cert['original_catalogue_sha256']
    assert [r['index'] for r in original] == list(range(1, 246))
    groups = {r['index']: closure(r['actual_generators'], r['order']) for r in original}
    signatures = {i: tuple(sorted(Counter(charpoly(g) for g in gs).items()))
                  for i, gs in groups.items()}
    classes = cert['classes']
    assert [r['new_index'] for r in classes] == list(range(1, 107))
    assert sorted(i for r in classes for i in r['old_indices']) == list(range(1, 246))
    assert len({signatures[r['representative']] for r in classes}) == 106
    witnesses = {w['original_index']: w for w in cert['witnesses']}
    expected_witnesses = {i for c in classes for i in c['old_indices'] if i != c['representative']}
    assert len(witnesses) == len(cert['witnesses']) == 139
    assert set(witnesses) == expected_witnesses
    comparisons = 0
    reduced = []
    mapping = {}
    labels = dict(zip('ABCDEGHIUZ', 'ABCDEFGHIJ'))
    for c in classes:
        r = c['representative']
        assert r in c['old_indices']
        source = original[r-1]
        for i in c['old_indices']:
            assert signatures[i] == signatures[r]
            assert original[i-1]['decision'] == source['decision']
            assert original[i-1]['order'] == source['order']
            mapping[i] = c['new_index']
            if i == r:
                continue
            w = witnesses[i]
            assert w['original_representative'] == r
            P = mat(w['P'])
            assert det(P) == w['determinant'] != 0
            # P R = H P is equivalent to P R P^-1 = H when P is invertible.
            assert {mul(P, g) for g in groups[r]} == {mul(h, P) for h in groups[i]}
            comparisons += len(groups[r])
        reduced.append({**source, 'index': c['new_index'],
                        'representative': c['new_index'], 'source_index': r,
                        'original_indices': c['old_indices'],
                        'sieve': labels[source['family']],
                        'characteristic_polynomial_distribution': signatures[r]})
    counts = Counter(r['decision'] for r in reduced)
    assert counts == {'YES': 61, 'NO': 45}
    assert [(x['index'],x['actual_generators'],x['order'],x['sieve']) for x in reduced] == [(x['index'],x['actual_generators'],x['order'],x['sieve']) for x in json.loads((HERE/'catalogue.json').read_text())]
    (HERE/'catalogue_reduced.json').write_text(json.dumps(reduced, indent=2)+'\n')
    report = {'status': 'PASS', 'method': 'Fresh exact Python matrix closure, Newton characteristic polynomials, and complete intertwining-set equalities',
              'original_groups': 245, 'original_group_elements': sum(map(len, groups.values())),
              'distinct_spectral_distributions': 106, 'classes': 106,
              'rational_conjugacies': 139, 'element_comparisons': comparisons,
              'decisions': dict(counts), 'all_decisions_constant_on_classes': True,
              'old_to_new': mapping, 'classes_data': classes,
              'input_sha256': {'catalogue_245.json': sha(INPUT),
                               'conjugacy_certificates.json': sha(HERE/'conjugacy_certificates.json')},
              'output_sha256': sha(HERE/'catalogue_reduced.json'),
              'verifier_sha256': sha(Path(__file__)),
              'seconds': round(time.monotonic()-start, 3),
              'scope': 'Conjugacy of this finite catalogue in GL4(Q), equivalently here GL4(C) and SL4(C); no claim of exhaustive classification of all finite subgroups.'}
    (HERE/'verification_reduction.json').write_text(json.dumps(report, indent=2)+'\n')
    print('REDUCTION_PASS:', report['classes'], 'classes;', report['rational_conjugacies'],
          'full-group conjugacies;', dict(counts), ';', report['seconds'], 'seconds', flush=True)

if __name__ == '__main__':
    main()
