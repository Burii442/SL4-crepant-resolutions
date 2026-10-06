#!/usr/bin/env python3
"""Reconstruct official CrystCat groups; compare exact spectral distributions.

Usage: python3 compare_catalogue.py /path/to/praca/skrocona/catalogue.json
No project code or project classification list is used to generate the
classical determinant-one classes.
"""
import json
import hashlib
import sys
from pathlib import Path
from collections import Counter
from fractions import Fraction
from itertools import permutations

HERE=Path(__file__).resolve().parent
I=tuple(tuple(int(i==j) for j in range(4)) for i in range(4))

def mul(a,b):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)) for i in range(4))

def det(a):
    return sum((-1)**sum(p[i]>p[j] for i in range(4) for j in range(i+1,4))*
               a[0][p[0]]*a[1][p[1]]*a[2][p[2]]*a[3][p[3]] for p in permutations(range(4)))

def closure(gens,order):
    gens=[tuple(map(tuple,g)) for g in gens]
    elements=[I]; known={I}
    for x in elements:
        for g in gens:
            y=mul(x,g)
            if y not in known:
                known.add(y); elements.append(y)
                assert len(elements)<=order
    assert len(elements)==order
    return elements

def poly(a):
    a2=mul(a,a);a3=mul(a2,a)
    p1=sum(a[i][i] for i in range(4));p2=sum(a2[i][i] for i in range(4));p3=sum(a3[i][i] for i in range(4))
    assert (p1*p1-p2)%2==0 and (p1**3-3*p1*p2+2*p3)%6==0
    return (det(a),-(p1**3-3*p1*p2+2*p3)//6,(p1*p1-p2)//2,-p1,1)

def signature(elements):
    return tuple(sorted(Counter(map(poly,elements)).items()))

classic=json.loads((HERE/'all_qclasses.json').read_text())
rows=classic['classes'];assert len(rows)==227
assert sum(r['zclasses'] for r in rows)==710
selected=[]
for r in rows:
    ds=[det(g) for g in r['generators']]
    assert ds==r['generator_determinants']
    assert all(d in (-1,1) for d in ds)
    assert all(d==1 for d in ds)==r['determinant_one']
    if r['determinant_one']:selected.append(r)
assert len(selected)==106 and sum(r['zclasses'] for r in selected)==245
classical_sigs={}; total=0
for r in selected:
    elements=closure(r['generators'],r['order']);total+=len(elements)
    key=signature(elements);assert key not in classical_sigs
    classical_sigs[key]=r
catalogue=Path(sys.argv[1]).resolve(); manuscript=json.loads(catalogue.read_text())
our_sigs={}; mapping=[]
for r in manuscript:
    assert all(det(g)==1 for g in r['actual_generators'])
    key=signature(closure(r['actual_generators'],r['order']))
    assert key not in our_sigs
    assert key==tuple((tuple(poly),n) for poly,n in r['characteristic_polynomial_distribution'])
    our_sigs[key]=r['index']
    c=classical_sigs[key]
    mapping.append({'manuscript_case':r['index'],'crystcat_system':c['system'],
                    'crystcat_qclass':c['qclass'],'crystcat_global_qclass':c['global_qclass'],
                    'crystcat_zclasses':c['zclasses'],'order':r['order']})
assert len(our_sigs)==106 and set(our_sigs)==set(classical_sigs)
expected_mapping=json.loads((HERE/'case_map.json').read_text())['correspondence']
if mapping != expected_mapping:
    raise ValueError('Fresh CrystCat correspondence differs from case_map.json')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'status':'PASS','gap_version':classic['gap_version'],
'crystcat_version':classic['crystcat_version'],'counts':classic['counts'],
'freshly_reconstructed_classical_elements':total,'classical_distinct_spectral_distributions':106,
'manuscript_distinct_spectral_distributions':106,'spectral_distributions_coincide':True,
'correspondence':mapping,'input_sha256':{'all_qclasses.json':sha(HERE/'all_qclasses.json'),'case_map.json':sha(HERE/'case_map.json'),str(catalogue):sha(catalogue)},
'program_sha256':{n:sha(HERE/n) for n in ['count_crystcat.g','compare_catalogue.py']},
'scope':'Complete independent CrystCat enumeration, determinant filter and exact matrix closure/spectral comparison. Conjugacy completeness relies on the classical catalogue; spectral equality by itself is not a general conjugacy criterion. Distinct spectra and the complete count give the bijection.'}
(HERE/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='correspondence'},indent=2))
