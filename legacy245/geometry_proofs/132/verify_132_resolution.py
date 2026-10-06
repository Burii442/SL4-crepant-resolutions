"""Exact group and chart certificate for a crepant resolution of ASL4[132:137].

Run from any directory using Python with sympy. Only writes beside this file.
The mathematical projectivity/crepancy proof is in resolution_132_proof.md.
"""
import ast
import itertools
import json
from pathlib import Path
import sympy as S

HERE = Path(__file__).resolve().parent
catalogue = [row['actual_generators'] for row in json.loads((HERE / 'catalogue.json').read_text())]
I = S.eye(4)

def key(m):
    return tuple(m)

def closure(gens):
    known = {key(I): I}
    todo = [I]
    for g in todo:
        for h in gens:
            p = g*h
            if key(p) not in known:
                known[key(p)] = p
                todo.append(p)
    return list(known.values())

Pcycle = S.Matrix([[1,0,0,0],[0,0,0,1],[0,1,0,0],[0,0,1,0]])
diagonals = [S.diag(*sgn) for sgn in itertools.product([-1,1],repeat=4) if S.prod(sgn)==1]
canonical = {key(d * Pcycle**i) for d in diagonals for i in range(3)}
records=[]
for index in range(132,138):
    generators = [S.Matrix(g) for g in catalogue[index-1]]
    group = closure(generators)
    assert len(group)==24
    N = [g for g in group if g*g==I]
    assert len(N)==8 and all(g*h==h*g for g in N for h in N)
    # Simultaneous rational eigenspaces of all involutions.
    spaces=[I]
    for n in N:
        refined=[]
        for B in spaces:
            for sign in [-1,1]:
                kernel=((n-sign*I)*B).nullspace()
                if kernel:
                    refined.append(B*S.Matrix.hstack(*kernel))
        spaces=refined
    assert len(spaces)==4 and all(B.cols==1 for B in spaces)
    c=next(g for g in group if g!=I and g**3==I)
    fixed=next(B for B in spaces if c*B==B)
    b=next(B for B in spaces if c*B!=B)
    P=S.Matrix.hstack(fixed,b,c*b,c*c*b)
    assert P.det()!=0
    conjugates=[P.inv()*g*P for g in group]
    assert {key(g) for g in conjugates}==canonical
    records.append(dict(index=index,order=len(group),normal_even_sign_subgroup_order=len(N),
        conjugating_matrix=[[str(z) for z in row] for row in P.tolist()],
        determinant=str(P.det()),
        conjugated_generators=[[[str(z) for z in row] for row in (P.inv()*g*P).tolist()] for g in generators],
        exact_canonical_group_equality=True))

a,x,y,d,e,t,X,Y,u,v=S.symbols('a x y d e t X Y u v')
charts=[(x**3*y**2,y,x*y),(x**2*y,x*y**2,x*y),(x,x**2*y**3,x*y)]
ccharts=[]
for U,V,W in charts:
    assert S.expand(U*V-W**3)==0
    ccharts.append(S.expand(a**3+U+V-3*a*W))
cL,cM,cR=ccharts
# All critical points of c in the outer charts lie in the middle-chart overlap.
assert S.diff(cL,y).subs(x,0)==1
assert S.diff(cR,x).subs(y,0)==1
# Exact overlap formulas: middle (p,q)=(x^2 y,1/x) on L and (1/y,x y^2) on R.
p,q=S.symbols('p q')
mid=a**3+p*q*(p+q-3*a)
assert S.simplify(mid.subs({p:x*x*y,q:1/x})-cL)==0
assert S.simplify(mid.subs({p:1/y,q:x*y*y})-cR)==0
shifted=S.expand(cM.subs({x:a+X,y:a+Y}))
expected=a*(X*X+X*Y+Y*Y)+X*Y*(X+Y)
assert S.expand(shifted-expected)==0
F=t*t*d-expected
Ft=S.cancel(F.subs({X:t*u,Y:t*v})/t**2)
Fx=S.cancel(F.subs({t:X*u,Y:X*v})/X**2)
Fy=S.cancel(F.subs({t:Y*u,X:Y*v})/Y**2)
assert S.diff(Ft,d)==1
assert S.diff(Fx,a)-S.diff(Fx,X)==-1
assert S.diff(Fy,a)-S.diff(Fy,Y)==-1
# The original double-cover blow-up charts after saturation.
c=S.symbols('c')
assert S.expand((e*e-d*c).subs(e,d*t)-d*(d*t*t-c))==0
s=S.symbols('s')
assert S.expand((e*e-d*c).subs(d,e*s)-e*(e-s*c))==0

out=dict(result='PASS',indices=list(range(132,138)),group_certificates=records,
    quotient_presentation=['U*V=W^3','e^2=d*(a^3+U+V-3*a*W)'],
    A2_resolution_charts=[dict(U=str(U),V=str(V),W=str(W),c=str(cc)) for (U,V,W),cc in zip(charts,ccharts)],
    middle_critical_locus_reduced='x=y=a',
    outer_critical_loci_in_middle_overlap=True,
    translated_c=str(expected),final_blowup_charts=[str(Ft),str(Fx),str(Fy)],
    smoothness_certificates=['d(Ft)/dd=1','d(Fx)/da-d(Fx)/dX=-1','d(Fy)/da-d(Fy)/dY=-1'],
    discrepancy_checks=['A2 resolution: crepant; base changed hypersurface has no exceptional factor',
                        'ambient blowup (d,e): codimension 2, multiplicity 1, discrepancy 0',
                        'ambient blowup (t,X,Y): codimension 3, multiplicity 2, discrepancy 0'])
(HERE/'certificate_132.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(result='PASS',indices=out['indices'],groups_verified=len(records),
                     smooth_final_charts=3),indent=2))
