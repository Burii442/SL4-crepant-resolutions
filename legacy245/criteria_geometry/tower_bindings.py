"""Complete exact group conjugacy checks for all eight Hilbert-square towers."""
from pathlib import Path
import ast
import json
import sympy as sp

HERE = Path(__file__).resolve().parent
catalogue_records = json.loads((HERE/'catalogue.json').read_text())
assert [r['index'] for r in catalogue_records] == list(range(1,246))
catalogue = [r['actual_generators'] for r in catalogue_records]
certificates = json.loads((HERE/'tower_matrices.json').read_text())
assert {r['index'] for r in certificates} == {165,166,214,215,216,217,218,228}
identity = tuple(int(i==j) for i in range(4) for j in range(4))

def flatten(a):
    return tuple(x for row in a for x in row)

def multiply(a,b):
    return tuple(sum(a[4*i+k]*b[4*k+j] for k in range(4)) for i in range(4) for j in range(4))

def closure(generators):
    seen={identity}; queue=[identity]
    for a in queue:
        for b in generators:
            c=multiply(a,b)
            if c not in seen:
                seen.add(c); queue.append(c)
        assert len(seen)<1000
    return seen

rows=[]
for record in certificates:
    i,m=record['index'],record['m']
    r=sp.Matrix({3:[[0,-1],[1,-1]],4:[[0,-1],[1,0]],6:[[0,-1],[1,1]]}[m])
    s=sp.diag(1,-1) if m==4 else sp.Matrix([[0,1],[1,0]])
    swap=sp.Matrix([[0,0,1,0],[0,0,0,1],[1,0,0,0],[0,1,0,0]])
    expected=[sp.diag(r,sp.eye(2)),sp.diag(sp.eye(2),r),sp.diag(s,s),swap]
    assert list(map(sp.Matrix,record['model_generators']))==expected
    assert r**m==sp.eye(2) and s*r*s==r.inv()
    assert r.det()==1 and s.det()==-1
    original=closure(list(map(flatten,catalogue[i-1])))
    images=closure(list(map(flatten,record['images'])))
    model=closure(list(map(flatten,record['model_generators'])))
    assert original==images and len(original)==len(model)==4*m*m
    p=sp.Matrix(record['intertwiner'])
    assert p.det()!=0
    assert all(sp.Matrix(a)*p==p*g for a,g in zip(record['images'],expected))
    row={'index':i,'m':m,'order':len(original),'det_intertwiner':str(p.det()),'pass':True}
    rows.append(row)
    print('TOWER_EXACT_PASS',i,'m',m,'order',len(original),'detP',p.det())

(HERE/'Z_exact_binding_recheck.json').write_text(json.dumps(rows,indent=2)+'\n')
print('ALL_8_TOWERS_RECHECKED')
