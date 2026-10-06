#!/usr/bin/env python3
"""Check the standalone catalogue and pairwise nonconjugacy by exact arithmetic."""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import time
HERE = Path(__file__).resolve().parent
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
    path = HERE/'catalogue.json'
    rows = json.loads(path.read_text())
    assert [r['index'] for r in rows] == list(range(1,107))
    signatures = []
    elements = 0
    for row in rows:
        group = closure(row['actual_generators'], row['order'])
        signature = tuple(sorted(Counter(charpoly(g) for g in group).items()))
        stored = tuple((tuple(poly),count) for poly,count in row['characteristic_polynomial_distribution'])
        assert signature == stored, row['index']
        assert signature not in signatures, row['index']
        signatures.append(signature)
        elements += len(group)
    assert Counter(r['decision'] for r in rows) == {'YES':61,'NO':45}
    report = {'status':'PASS','classes':len(rows),'distinct_spectral_distributions':len(set(signatures)),
              'group_elements':elements,'ordered_generators':sum(len(r['actual_generators']) for r in rows),
              'decisions':dict(Counter(r['decision'] for r in rows)),
              'method':'Exact matrix closure and Newton identities; pairwise distinct characteristic-polynomial distributions',
              'scope':'Checks the 106 listed matrix groups and pairwise nonconjugacy. The YES/NO totals are labels, not independently proved geometric decisions; exhaustiveness among all finite subgroups is not tested.',
              'catalogue_sha256':sha(path),'verifier_sha256':sha(Path(__file__)),
              'seconds':round(time.monotonic()-start,3)}
    (HERE/'verification_106.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__ == '__main__': main()
