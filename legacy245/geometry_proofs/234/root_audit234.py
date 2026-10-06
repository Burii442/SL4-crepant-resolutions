"""Independent input-to-Rees-chart binding and local slice audit for234--235."""
from pathlib import Path
import re,json,hashlib
import sympy as s
P=Path(__file__).resolve().parent
original=json.loads((P/'a5_discriminant_input.json').read_text())
fresh=original
assert original==fresh
p,q,r,h,w,v=s.symbols('p q r h w v'); yy=s.symbols('y0:5')
D=s.sympify(fresh['discriminant']); gg=[s.sympify(row['polynomial']) for row in fresh['strata'][0]['ideal_generators']]
checks=[]
for j in range(5):
 source=(P/f'a5_triple_chart{j}.sing').read_text()
 raw=source.split('ideal raw=',1)[1].split(';',1)[0]
 actual=[s.sympify(f,locals={str(x):x for x in [p,q,r,h,v,*yy]}) for f in raw.split(',')]
 expected=[gg[i-1]-v*(1 if j==i else yy[i]) for i in range(1,5)]+[(v if j==0 else v*yy[0])**2-D]
 assert len(actual)==len(expected)==5
 assert all(s.expand(a-b)==0 for a,b in zip(actual,expected))
 assert 'list L=sat(raw,ideal(v));' in source and 'ideal C=std(L[1]);' in source
 log=(P/f'a5_triple_chart{j}.log').read_text()
 fstrings=re.findall(r'^CF\[\d+\]=(.*)$',log,re.M)
 fs=[s.sympify(f,locals={str(x):x for x in yy}) for f in fstrings]
 target=[s.Integer(1)] if j==4 else [yy[4],yy[1]**2-1125] if j==0 else [yy[4],1125*yy[0]**2-1] if j==1 else [yy[4],1125*yy[0]**2-yy[1]**2]
 variables=[yy[i] for i in range(5) if i!=j]
 A=s.groebner(fs,*variables);B=s.groebner(target,*variables)
 assert all(A.contains(f) for f in target) and all(B.contains(f) for f in fs)
 checks.append(dict(chart=j,raw_Rees_equations_bound=True,fresh_central_fiber_ideal_equality=True))
# Independent elementary local computations over every nonzero stabilizer stratum.
a,x,y,e,X,Y,t,u,V=s.symbols('a x y e X Y t u V')
cL=a**3+x**3*y**2+y-3*a*x*y;cM=a**3+x*y*(x+y-3*a);cR=a**3+x+x**2*y**3-3*a*x*y
assert s.cancel(cM.subs({x:x*x*y,y:1/x},simultaneous=True)-cL)==0
assert s.cancel(cM.subs({x:1/y,y:x*y*y},simultaneous=True)-cR)==0
assert s.expand(cM.subs({x:X+a,y:Y+a},simultaneous=True)-(a*(X*X+X*Y+Y*Y)+X*Y*(X+Y)))==0
F=t*t-a*(1+V+V*V)-X*V*(1+V)
assert s.expand(s.diff(F,a)-s.diff(F,X))==-1
F=1-a*(u*u+u*V+V*V)-e*u*V*(u+V)
assert s.groebner([F]+[s.diff(F,z) for z in [a,e,u,V]],a,e,u,V).contains(s.Integer(1))
# S3 std2+sign, p-chart: c=v^2+p is a polynomial coordinate; z^2=s*c.
ss,z,c=s.symbols('s z c')
original_S3=w*w-ss*(q*q+p**3)
assert s.expand(original_S3.subs({q:p*V,w:p*z},simultaneous=True)/p**2-(z*z-ss*(V*V+p)))==0
# The smooth q-chart complement and w-chart have no singular points.
F=z*z-ss*(1+q*V**3)
assert s.groebner([F,V]+[s.diff(F,z0) for z0 in [q,V,z,ss]],q,V,z,ss).contains(s.Integer(1))
F=1-ss*(z*z+w*V**3)
assert s.groebner([F]+[s.diff(F,z0) for z0 in [w,V,z,ss]],w,V,z,ss).contains(s.Integer(1))
# Three charts of blow(s,z,c) in A1: two eliminate, central chart s1*c1=1.
assert s.groebner([1-u*V,-V,-u],u,V).contains(s.Integer(1))
cert=dict(result='PASS_INDEPENDENT_INPUT_BINDING_AND_LOCAL_GEOMETRY',first_chart_checks=checks,local_models=['A2','A1','S3 standard2 plus sign','A4 standard3'],fresh_final_validator='certificate234_geometry.json')
(P/'root_audit234_certificate.json').write_text(json.dumps(cert,indent=2)+'\n')
print(cert['result'])
