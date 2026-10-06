"""Fresh binding of the stated discriminant and both complete stratum ideals."""
from pathlib import Path
import json
import sympy as S

P=Path(__file__).resolve().parent
d=json.loads((P/'a5_discriminant_input.json').read_text())
T,a,b,p,q,r,h,s,v=S.symbols('T a b p q r h s v')
D=S.discriminant(T**5+p*T**3+q*T**2+r*T+h,T)
assert S.expand(D-S.sympify(d['discriminant']))==0
for row,polynomial in zip(d['strata'],[(T-a)**3*(T*T+3*a*T+b),(T*T-a*T+b)**2*(T+2*a)]):
    actual=S.Poly(polynomial,T).all_coeffs()[2:]
    stated=[S.sympify(row['parametrization'][str(x)]) for x in [p,q,r,h]]
    assert all(S.expand(x-y)==0 for x,y in zip(actual,stated))
    graph=S.groebner([x-y for x,y in zip([p,q,r,h],actual)],a,b,h,r,q,p,order='lex')
    kernel=[x.as_expr() for x in graph.polys if not x.as_expr().has(a,b)]
    given=[S.sympify(x['polynomial']) for x in row['ideal_generators']]
    A=S.groebner(kernel,h,r,q,p,order='lex');B=S.groebner(given,h,r,q,p,order='lex')
    assert all(A.contains(x) for x in given) and all(B.contains(x) for x in kernel)
    assert S.expand(D.subs(dict(zip([p,q,r,h],actual)),simultaneous=True))==0
    print('FULL_STRATUM_KERNEL',row['name'],'PASS',len(A.polys),flush=True)
for chart in [0,1]:
    result=0
    for (iq,ih),coef in S.Poly(D,q,h).terms():
        assert (iq+ih)%2==0
        result+=coef*s**((iq+ih)//2)*v**(ih if chart==0 else iq)
    assert S.expand(result-S.sympify(d['central_extension_C2xA5']['two_charts'][chart]['D']))==0
print('DISCRIMINANT_AND_CONTRACTED_CHART_INPUTS_PASS',flush=True)
