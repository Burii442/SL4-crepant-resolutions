"""Exact replay of the two-blowup crepant resolution of the standard A5 quotient.
No precomputed Cox ring is used. Invoked in a fresh directory by ../run.py.
"""
from pathlib import Path
import json,re,subprocess,hashlib,time,concurrent.futures
import sympy as S
P=Path(__file__).resolve().parent
CERT={}
def ss(f):return str(f).replace('**','^')
def parse_c(j):return re.findall(r'^C\[\d+\]=(.*)$',(P/f'a5_triple_chart{j}.log').read_text(),re.M)
def run_chart(j):
 t=time.time();f=P/f'a5_triple_chart{j}.sing'
 z=subprocess.run(['Singular','-q',str(f)],capture_output=True,text=True,timeout=None)
 assert z.returncode==0 and '?' not in z.stdout and 'DONE' in z.stdout,(j,z.stdout[-2000:])
 (P/f'a5_triple_chart{j}.log').write_text(z.stdout)
 dim=int(re.search(r'CHART_DIMENSION\n(-?\d+)',z.stdout)[1]);fd=int(re.search(r'FIBER_DIMENSION\n(-?\d+)',z.stdout)[1]);assert dim==4 and fd in[2,-1]
 return dict(chart=j,dimension=dim,central_fiber_dimension=fd,seconds=round(time.time()-t,3))
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:CERT['first_charts']=list(ex.map(run_chart,range(5)))
print('FIVE_REES_CHARTS_PASS',flush=True)
# The full charts are I:v^infty, not unsaturated graph equations.
# The matrix minors use five actual rows of those exact chart ideals.
minors=json.loads((P/'a5_first_boundary_minors.json').read_text());bm=[]
for row in minors:
 j=row['chart'];names=['p','q','r','h']+[f'y{i}' for i in range(5) if i!=j]+['v'];vv=S.symbols(' '.join(names));ns=dict(zip(names,vv));zero={ns[x]:0 for x in ['p','q','r','h','v','y3','y4']};raw=parse_c(j)
 fs=[S.sympify(raw[k-1],locals=ns) for k in row['rows']];cols=[ns[x] for x in row['columns']]
 det=S.factor(S.Matrix([[S.diff(f,x).subs(zero) for x in cols] for f in fs]).det());assert S.expand(det-S.sympify(row['determinant'],locals=ns))==0
 bm.append(dict(chart=j,rows=row['rows'],columns=row['columns'],determinant=str(det)))
CERT['boundary_minors']=bm;print('BOUNDARY_MINORS_PASS',flush=True)
# Reduce the independent dp-saturated g3 chart, using only invertible linear elimination.
vv=S.symbols('p q r h Z z1 t z4 v');p,q,r,h,Z,z1,t,z4,v=vv
ns=dict(zip(['p','q','r','h','y0','y1','y2','y4','v'],vv));fs=[S.sympify(x,locals=ns) for x in parse_c(3)];subs={};steps=[]
for x in [z4,r,h,v]:
 candidates=[(i,f,S.diff(f,x)) for i,f in enumerate(fs) if S.diff(f,x)!=0 and not S.diff(f,x).free_symbols];assert candidates
 i,f,c=min(candidates,key=lambda item:S.count_ops(item[1]));val=S.expand(x-f/c);steps.append(dict(variable=str(x),coefficient=str(c),equation=str(f),replacement=str(val)))
 fs=[S.expand(g.subs(x,val)) for j,g in enumerate(fs) if j!=i];fs=[g for g in fs if g!=0]
 subs={y:S.expand(z.subs(x,val)) for y,z in subs.items()};subs[x]=val
F=min(fs,key=S.count_ops);F=S.Poly(F,p,q,Z,z1,t).monic().as_expr();BAS=S.groebner([F],p,q,Z,z1,t)
assert all(BAS.reduce(g)[1]==0 for g in fs)
# Every operation is an ideal equality: an equation with constant nonzero derivative
# eliminates one variable, and F itself is one of the remaining equations up to a unit.
A,B,Q=S.symbols('A B Q');qshift=t*(52*p-8*z1+15*t*t)/72
coord={p:-A/S.Integer(20)+B/S.Integer(40)-5*t*t/8,z1:-A/S.Integer(20)+11*B/S.Integer(40)+5*t*t/8}
transformed=S.factor(F.subs(q,Q+qshift).subs(coord,simultaneous=True));H=25920*Q*Q-B*(8100*Z*Z-A*A)+7200*A*Z*Z
assert S.expand(transformed+H/1936)==0
CERT['g3_reduction']=dict(eliminations=steps,original_eliminated={str(x):str(f) for x,f in subs.items()},hypersurface=str(F),normal_form=str(H),coordinate_change={str(x):str(f) for x,f in coord.items()},Q_shift=str(qshift))
print('G3_HYPERSURFACE_EQUALITY_PASS',flush=True)
# Bind the strict double-double center to the original prime stratum ideal.
data=json.loads((P/'a5_discriminant_input.json').read_text());ks=[S.sympify(x['polynomial']) for x in data['strata'][1]['ideal_generators']];ks=[S.expand(x.subs(subs,simultaneous=True)) for x in ks]
fmt=lambda x:re.sub(r'\^(\d+)',r'^(\1)',ss(x))
code='LIB "elim.lib";option(noredefine);option(redSB);ring R=0,(p,q,Z,z1,t),dp;\npoly F='+fmt(F)+';poly pivot='+fmt(subs[v])+';\nideal raw=F,Z*pivot,'+','.join(map(fmt,ks))+';\nideal strict=std(sat(raw,ideal(pivot)));\nideal expected=std(ideal(Z,-22*p+2*z1-15*t^2,q-t*(52*p-8*z1+15*t^2)/72));\nif(size(reduce(strict,expected))!=0 || size(reduce(expected,strict))!=0){ERROR("strict center mismatch");}\nprint("STRICT_CENTER_EQUALITY_PASS");quit;\n'
(P/'a5_g3_center_certificate.sing').write_text(code);z=subprocess.run(['Singular','-q',str(P/'a5_g3_center_certificate.sing')],capture_output=True,text=True,timeout=None);(P/'a5_g3_center_certificate.log').write_text(z.stdout);assert '?' not in z.stdout and 'STRICT_CENTER_EQUALITY_PASS' in z.stdout
CERT['strict_center']='(A,Z,Q), exact saturated ideal equality';print('STRICT_CENTER_PASS',flush=True)
# Three full affine charts of blow(A,Z,Q), including all their boundary points.
a,b,u,V=S.symbols('a b u V');charts=[('A',25920*V**2-B*(8100*u*u-1)+7200*A*u*u,[A,B,u,V]),('Z',25920*V**2-B*(8100-a*a)+7200*Z*a,[Z,B,a,V]),('Q',25920-B*(8100*b*b-a*a)+7200*Q*a*b*b,[Q,B,a,b])]
checks=[]
for name,f,vars in charts:
 G=S.groebner([f]+[S.diff(f,x) for x in vars],*vars);assert G.contains(S.Integer(1));checks.append(dict(chart=name,equation=str(f),jacobian_ideal_unit=True))
CERT['second_blowup_charts']=checks
# Exact roots-of-unity-free transfer of all four catalogue representations.
z=subprocess.run(['gap','-q',str(P/'transfer234_237.g')],capture_output=True,text=True,timeout=None);(P/'transfer234_237.log').write_text(z.stdout);assert z.returncode==0 and 'TRANSFER_234_237_PASS' in z.stdout
CERT['representation_transfer']='all character values on all elements, cases234..237 PASS'
# At the smooth g2 central origin, the involution has four negative tangent weights.
raw=parse_c(2);names=['p','q','r','h','y0','y1','y3','y4','v'];vs=S.symbols(' '.join(names));dic=dict(zip(names,vs));ff=[S.sympify(x,locals=dic) for x in raw[:10]];J=S.Matrix([[S.diff(f,x).subs({z:0 for z in vs}) for x in vs] for f in ff]);assert J.rank()==5
odd=[1,3,4,5,6,7,8];even=[0,2];assert J[:,odd].rank()==3 and J[:,even].rank()==2
CERT['C2_quotient_obstruction']=dict(point='g2 chart: all nine affine coordinates zero',ambient_odd_dimension=7,odd_relation_rank=3,tangent_negative_dimension=4,tangent_positive_dimension=0,scope='isolated 1/2(1,1,1,1) only on the quotient of this chosen resolution; no all-model NO claim')
CERT['status']='PASS_GEOMETRIC_YES_234_235'
(P/'certificate234_geometry.json').write_text(json.dumps(CERT,indent=2)+'\n')
files=[Path(__file__),P/'a5_discriminant_input.json',P/'a5_first_boundary_minors.json',P/'a5_g3_center_certificate.sing',P/'transfer234_237.g']+[P/f'a5_triple_chart{j}.sing' for j in range(5)]
(P/'SHA256_234_geometry.json').write_text(json.dumps({str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},indent=2)+'\n')
print(CERT['status'],flush=True)
