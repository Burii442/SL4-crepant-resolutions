"""Exact checks of the twelve invariant rings and 46 coherent toric fans.

Run: sage -python verify_geometry.py
Requires SageMath; all inputs are relative to this file.
"""
from pathlib import Path
import itertools
import json
import csv
from sage.all import QQ, PolynomialRing, matrix, vector, Polyhedron

HERE=Path(__file__).resolve().parent
reports=[]
for folder in sorted(HERE.glob('*/invariant_ring'),key=lambda p:int(p.parent.name)):
    d=json.loads((folder/'ring_certificate.json').read_text())
    matrices=[matrix(QQ,g) for g in json.loads((folder/'input_matrices.json').read_text())]
    # Source polynomials use x1,...,x4 rather than Sage's default x0,...,x3.
    R=PolynomialRing(QQ,names=['x1','x2','x3','x4']);xs=R.gens()
    fs=[R(f) for f in d['generators']]
    for g in matrices:
        image=list(g*vector(xs))
        assert all(f(*image)==f for f in fs)
    m=len(fs)
    T=PolynomialRing(QQ,names=['x1','x2','x3','x4']+[f'u{i}' for i in range(1,m+1)],order='lex')
    x=T.gens()[:4];u=T.gens()[4:]
    graph=T.ideal([u[j]-T(str(fs[j])) for j in range(m)])
    eliminated=[f for f in graph.groebner_basis() if not any(f.degree(z) for z in x)]
    kernel=T.ideal(eliminated)
    relations=T.ideal([T(f) for f in d['minimal_relations']])
    assert kernel==relations
    assert all(f(*([0]*4+fs))==0 for f in relations.gens())
    assert relations.dimension()==8
    if len(relations.gens())==2:
        assert relations.gens()[0].gcd(relations.gens()[1])==1
    identity=matrix(QQ,4,4,1);identity.set_immutable()
    seen={identity};todo=list(seen)
    while todo:
        a=todo.pop()
        for g in matrices:
            b=a*g;b.set_immutable()
            if b not in seen:seen.add(b);todo.append(b)
    assert len(seen)==d['actual_group_order']
    A=PolynomialRing(QQ,'t');t=A.gen();K=A.fraction_field()
    molien=sum(K(1)/((matrix(A,4,4,1)-t*matrix(A,g)).det()) for g in seen)/len(seen)
    hilbert=K(1)
    for n in d['relation_degrees']:hilbert*=1-t**n
    for n in d['weights']:hilbert/=1-t**n
    assert molien==hilbert
    reports.append({'index':d['index'],'invariant_ring':True,'full_kernel':True,'molien_hilbert':True})
    print('INVARIANT_RING',d['index'],'verified',flush=True)

chars={int(r['index']):r for r in csv.DictReader((HERE/'abelian_characters.csv').open())}
tetrahedra=0;pairs=0
for path in sorted(HERE.glob('*/triangulation.json'),key=lambda p:int(p.parent.name)):
    d=json.loads(path.read_text());n=d['order']
    P=[vector(QQ,p) for p in d['points']];h=list(map(QQ,d['heights']))
    fractional=[tuple(QQ(v) for v in p.split(',')) for p in chars[d['index']]['fractional_points'].split(';')]
    permutation=d['actual_character_coordinate_permutation']
    fractional={tuple(p[j] for j in permutation) for p in fractional}
    assert len(fractional)==n
    expected={tuple(int(j==k) for j in range(4)) for k in range(4)}|{p for p in fractional if sum(p)==1}
    assert {tuple(p) for p in P}==expected
    cells=[];indices=[]
    for cell in d['simplices']:
        S=cell['simplex'];M=matrix(QQ,[P[j] for j in S])
        assert n*abs(M.det())==1
        plane=M.solve_right(vector(QQ,[h[j] for j in S]))
        assert all(h[j]-P[j]*plane==0 if j in S else h[j]-P[j]*plane>0 for j in range(len(P)))
        cells.append(Polyhedron(vertices=[P[j] for j in S],base_ring=QQ,backend='ppl'));indices.append(set(S))
        tetrahedra+=1
    assert len(cells)==n
    for j in range(len(cells)):
        for k in range(j):
            common=indices[j]&indices[k]
            meet=cells[j].intersection(cells[k]);pairs+=1
            assert meet==Polyhedron(vertices=[P[z] for z in common],base_ring=QQ,backend='ppl') if common else meet.is_empty()
    print('TORIC_FAN',d['index'],'verified',flush=True)
assert len(reports)==12 and len(list(HERE.glob('*/triangulation.json')))==46 and tetrahedra==337
result={'invariant_rings':reports,'toric_fans':46,'tetrahedra':tetrahedra,'pair_intersections':pairs,
        'scope':'Exact invariance, full elimination kernels, Molien/Hilbert equality; full toric coherence, volume and intersections against the saved character lattices.'}
(HERE/'geometry_verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
