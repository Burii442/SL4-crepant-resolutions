#!/usr/bin/env sage -python
"""Reconstruct all 245 matrix groups and their exact elementary invariants.

Run: sage -python verify_catalogue.py --output verification/catalogue.json
Only catalogue.json and criteria_incidence.csv are inputs. This verifies group
and criterion-incidence data; it does not prove the geometric criteria.
"""
import argparse
from collections import Counter
import csv
import hashlib
import json
from itertools import combinations
from pathlib import Path
import time
from sage.all import QQ, ZZ, identity_matrix, matrix

HERE = Path(__file__).resolve().parent
PAIRS = list(combinations(range(4), 2))

def immutable(m):
    m.set_immutable()
    return m

IDENTITY = immutable(identity_matrix(QQ, 4))

def require(condition, message):
    if not condition:
        raise ValueError(message)

def closure(generators, maximum):
    found = {IDENTITY}
    todo = [IDENTITY]
    for a in todo:
        for g in generators:
            b = immutable(g*a)
            if b not in found:
                found.add(b)
                require(len(found) <= maximum, 'Closure exceeds the asserted finite group order')
                todo.append(b)
    return found

def generated_subgroup(elements, maximum):
    found, generators = {IDENTITY}, []
    for g in sorted(elements):
        if g not in found:
            generators.append(g)
            found = closure(generators, maximum)
    return found

def conjugacy_classes(group, generators):
    inverses = [g.inverse() for g in generators]
    unseen, classes = set(group), []
    while unseen:
        x = min(unseen)
        seen, todo = {x}, [x]
        for y in todo:
            for g, inv in zip(generators, inverses):
                z = immutable(g*y*inv)
                if z not in seen:
                    seen.add(z)
                    todo.append(z)
        require(seen <= unseen, 'Conjugacy orbits overlap or leave the group')
        unseen.difference_update(seen)
        classes.append(seen)
    require(sum(map(len, classes)) == len(group), 'Conjugacy classes do not partition the group')
    return classes

def alternating_forms(generators):
    equations = []
    for g in generators:
        for i, j in PAIRS:
            equations.append([g[a,i]*g[b,j]-g[b,i]*g[a,j]-int((a,b)==(i,j)) for a,b in PAIRS])
    equations = matrix(QQ, equations) if equations else matrix(QQ, 0, 6)
    basis = list(equations.right_kernel().basis())
    def pfaffian(v):
        return v[0]*v[5]-v[1]*v[4]+v[2]*v[3]
    witnesses = basis + [a+b for a,b in combinations(basis, 2)]
    # A quadratic polynomial vanishes identically iff it vanishes on the
    # basis vectors and on their pairwise sums; hence this test is exhaustive.
    nondegenerate = any(pfaffian(v) != 0 for v in witnesses)
    return len(basis), bool(nondegenerate)

def verify_record(record):
    index = record['index']
    gens = [immutable(matrix(QQ, g)) for g in record['actual_generators']]
    require(all(g.nrows()==g.ncols()==4 and all(x in ZZ for x in g.list()) and g.det()==1 for g in gens), f'{index}: nonintegral or non-SL4 generator')
    group = closure(gens, record['order'])
    require(len(group)==record['order'], f'{index}: incorrect group order')
    require(all(g.det()==1 for g in group), f'{index}: determinant')
    ranks = {g:int((g-IDENTITY).rank()) for g in group}
    require(set(ranks.values()) <= {0,2,4}, f'{index}: impossible real determinant-one rank')
    classes = conjugacy_classes(group, gens)
    ages = Counter(ranks[next(iter(c))]//2 for c in classes)
    require(ages[0]==1 and ages[1]==record['junior_classes'] and ages[2]==record['age2_classes'], f'{index}: age-class counts')
    require(all(len({ranks[g] for g in c})==1 for c in classes), f'{index}: class rank')
    juniors = generated_subgroup((g for g in group if ranks[g]==2), len(group))
    equations = matrix(QQ, [list(row) for g in gens for row in g-IDENTITY]) if gens else matrix(QQ,0,4)
    fixed = 4-equations.rank()
    require(QQ(sum(g.trace() for g in group))/len(group)==fixed, f'{index}: fixed-space character formula')
    dim, nondeg = alternating_forms(gens)
    char_dim = QQ(sum((g.trace()**2-(g*g).trace())/2 for g in group))/len(group)
    require(dim==char_dim, f'{index}: invariant two-form character formula')
    abelian = all(g*h==h*g for g in gens for h in gens)
    return {'index':index,'order':len(group),'conjugacy_classes':len(classes),'junior_classes':ages[1],
        'age2_classes':ages[2],'junior_elements':sum(r==2 for r in ranks.values()),
        'junior_subgroup_order':len(juniors),'fixed_dimension':int(fixed),'abelian':abelian,
        'invariant_two_form_dimension':dim,'nondegenerate_invariant_form':nondeg,
        'character_norm':int(sum(g.trace()**2 for g in group)/len(group)),
        'decision_label':record['decision'],'family_label':record['family']}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=HERE/'verification/catalogue.json')
    args=parser.parse_args();start=time.time()
    path=HERE/'catalogue.json';records=json.loads(path.read_text())
    require([r['index'] for r in records]==list(range(1,246)), 'Catalogue indices must be exactly 1..245')
    out=[]
    for record in records:
        out.append(verify_record(record))
        if record['index']%25==0:
            print(f"Verified {record['index']}/245 groups",flush=True)
    with (HERE/'criteria_incidence.csv').open() as stream:
        incidence=list(csv.DictReader(stream))
    require(len({(int(r['index']),r['test']) for r in incidence})==len(incidence),'Duplicate incidence rows')
    coverage={}
    for row in incidence:
        i=int(row['index']);require(1<=i<=245,'Unknown incidence index')
        require(row['outcome']==records[i-1]['decision'], f'{i}: conflicting criterion outcome')
        coverage.setdefault(row['test'],set()).add(i)
    require(set(coverage)==set('ABCDEGHIUZ'),'Criterion names')
    require(set.union(*coverage.values())==set(range(1,246)),'Incomplete incidence coverage')
    require(all(r['index'] in coverage[r['family']] for r in records),'Main-family membership')
    require(coverage['A']=={r['index'] for r in out if r['junior_subgroup_order']<r['order']},'Criterion A applicability')
    require(coverage['B']=={r['index'] for r in out if r['fixed_dimension']>0},'Criterion B applicability')
    require(coverage['C']=={r['index'] for r in out if r['abelian']},'Criterion C applicability')
    summary={'status':'PASS','groups_reconstructed':245,'group_elements':sum(r['order'] for r in out),
      'ordered_generators':sum(len(r['actual_generators']) for r in records),
      'decision_labels':dict(Counter(r['decision'] for r in records)),
      'catalogue_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
      'criteria_sha256':hashlib.sha256((HERE/'criteria_incidence.csv').read_bytes()).hexdigest(),
      'seconds':round(time.time()-start,3),
      'scope':'All closures, determinants, conjugacy classes, ages, junior subgroups, fixed spaces, invariant alternating forms and A/B/C applicability. Other criterion geometry is checked by separate proof programs.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps({'summary':summary,'cases':out},indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
