"""Exact geometry replay; the last h germ uses the proved finite-jet criterion.
Requires Python3+SymPy, Singular and GAP. Invoked in a fresh directory by ../run.py.
"""
from pathlib import Path
import subprocess,re,json,sympy as S,hashlib,sys,time
P=Path(__file__).resolve().parent;RESULT={'scope':'direct projective three-blowup construction for236..237','phases':[]}
def runpy(name,timeout=None):
 z=subprocess.run([sys.executable,str(P/name)],capture_output=True,text=True,timeout=timeout);(P/(name.replace('.py','')+'_master.log')).write_text(z.stdout+z.stderr);assert z.returncode==0,(name,z.stdout[-2000:],z.stderr[-2000:]);RESULT['phases'].append(name);print('PASS',name,flush=True)
def runsing(name,timeout=None):
 z=subprocess.run(['Singular','-q',str(P/name)],capture_output=True,text=True,timeout=timeout);(P/(name.replace('.sing','')+'.log')).write_text(z.stdout);assert z.returncode==0 and'?'not in z.stdout and'DONE'in z.stdout,(name,z.stdout[-2000:]);RESULT['phases'].append(name);return z.stdout
p,q,r,h,s,t,w,L,a,b=S.symbols('p q r h s t w L a b');d=json.loads((P/'a5_discriminant_input.json').read_text());T=S.Symbol('T');Disc=S.discriminant(T**5+p*T**3+q*T**2+r*T+h,T);assert S.expand(Disc-S.sympify(d['discriminant']))==0
# Reproduce both exact contracted centers after the first extraction.
runpy('c2a5_direct_first.py')
# Rebuild the complete q-chart input by exact substitution and coefficient division.
Dq=S.sympify(d['central_extension_C2xA5']['two_charts'][0]['D']).subs(S.Symbol('v'),t)
assert S.expand(Dq.subs(s,q*q)-Disc.subs(h,q*t))==0
s0=-5*p*p*t+S.Rational(32,9)*p*r+S.Rational(100,9)*r*t;K=9*p**3*t-p*p*r-225*p*p*t*t+140*p*r*t-12*r*r+500*r*t*t;coef=S.Poly(S.expand(Dq.subs(s,s0+L)),L)
model={'s0':str(s0),'K':str(K),'D_in_L':str(coef.as_expr()),'coefficients':{str(e[0]):str(S.factor(c))for e,c in coef.terms()},'center':['w','L',str(K)]};(P/'c2a5_q_first_model.json').write_text(json.dumps(model,indent=2)+'\n')
# Verify the first q strict center is precisely(w,s-s0,K), not just a set inclusion.
raw=S.symbols('p r s t w');fs=[S.sympify(x)for x in re.findall(r'^C\[\d+\]=(.*)$',(P/'c2a5_first_triple0.log').read_text(),re.M)];G=S.groebner(fs,*raw,domain=S.QQ);E=S.groebner([w,s-s0,K],*raw,domain=S.QQ);assert all(G.contains(f)for f in E.exprs)and all(E.contains(f)for f in G.exprs)
runpy('c2a5_q_triple_charts.py')
# Constant-coefficient elimination binds the complete q-L strict DD ideal.
vs=[p,r,t,L,a,b];fs=[S.sympify(x)for x in re.findall(r'^center\[\d+\]=(.*)$',(P/'c2a5_q_L_dd.log').read_text(),re.M)];sub={}
for x in[a,r,L]:
 candidates=[(i,f,S.diff(f,x))for i,f in enumerate(fs)if S.diff(f,x)!=0 and not S.diff(f,x).free_symbols];i,f,c=min(candidates,key=lambda z:S.count_ops(z[1]));v=S.expand(x-f/c);fs=[S.expand(g.subs(x,v))for j,g in enumerate(fs)if j!=i];fs=[f for f in fs if f!=0];sub={y:S.expand(g.subs(x,v))for y,g in sub.items()};sub[x]=v
GB=S.groebner(fs,p,t,b);assert len(GB.polys)==1
J=b*b/27+25*b*t/9+p*t+50*t*t;assert S.expand(GB.polys[0].as_expr()-J)==0
(P/'c2a5_q_L_dd_reduced.json').write_text(json.dumps({'J':str(J),'substitutions':{str(x):str(f)for x,f in sub.items()}},indent=2)+'\n')
runpy('c2a5_q_dd_charts.py')
# Recompute every used Jacobian determinant directly from freshly replayed full ideals.
def minor(chart,rows,columns,special=None,kind='q'):
 if kind=='q':names=['p','t','b','u','V','a']+[f'y{i}'for i in range(4)if i!=chart]+['v'];base=['p','t','b','u','V','a','v'];file=P/f'c2a5_q_dd_chart{chart}.log'
 else:names=['p','r','s','t','w']+[f'y{i}'for i in range(3)if i!=chart]+['v'];base=['p','r','s','t','w','v'];file=P/f'c2a5_h_triple_chart{chart}.log'
 ns={x:S.Symbol(x)for x in names};zero={ns[x]:0 for x in base};zero.update({ns[x]:S.sympify(v)for x,v in(special or{}).items()});raw=re.findall(r'^C\[\d+\]=(.*)$',file.read_text(),re.M);f=[S.sympify(raw[i-1],locals=ns)for i in rows];M=S.Matrix([[S.diff(g,ns[x]).subs(zero)for x in columns]for g in f]);return S.factor(M.det())
qm=json.loads((P/'c2a5_q_dd_jacobian.json').read_text());actual={}
for row in qm:
 val=minor(row['chart'],row['rows'],row['columns']);assert S.expand(val-S.sympify(row['determinant']))==0;actual[row['chart']]=val
assert actual[3]!=0 and not actual[3].free_symbols
z0,z1,z2,z3=S.symbols('y0 y1 y2 y3');assert S.expand(actual[2]+34992*(9*z1-16))==0
assert S.expand(actual[0].subs({z2:0,z3:0})-5832*(27*z1*z1+1)**3)==0
assert actual[1].subs({z0:0,z2:0,z3:0})!=0
special=json.loads((P/'c2a5_q_dd_jacobian_special.json').read_text())[1];val=minor(2,special['rows'],special['columns'],{'y1':'16/9','y3':0});assert S.expand(val-11664*(3*z0*z0-2048))==0
for row in json.loads((P/'c2a5_q_dd_cover.json').read_text()):
 sp={'y2':0,'y3':0}if row['chart']==0 else{'y1':'16/9','y3':0};val=minor(row['chart'],row['rows'],row['columns'],sp);assert S.expand(val-S.sympify(row['determinant']))==0
 relation=27*z1*z1+1 if row['chart']==0 else 3*z0*z0-2048;x=z1 if row['chart']==0 else z0;rem=S.rem(val,relation,x);assert rem!=0 and not rem.free_symbols;assert rem==S.sympify(row['remainder'])
RESULT['q_full_fiber_minor_cover']='PASS';print('PASS q full fiber minor cover',flush=True)
# Full ORIGINAL central fibers: t remains free. Regenerate source from fresh r0,L0.
norm=json.loads((P/'c2a5_q_dd_normal_input.json').read_text());fmt=lambda x:re.sub(r'\^(\d+)',r'^(\1)',x.replace('**','^'))
for j in range(4):
 src=(P/f'c2a5_q_dd_chart{j}.sing').read_text().split('print("DIM")')[0];src+='ideal O=std(C+ideal(p,u+('+fmt(norm['r0_reduced'])+'),V+('+fmt(norm['L0_reduced'])+')));print("ORIGINAL_CENTRAL_FIBER_DIM");dim(O);print("DONE");quit;\n';name=f'c2a5_q_dd_original_fiber{j}.sing';(P/name).write_text(src);out=runsing(name);assert'ORIGINAL_CENTRAL_FIBER_DIM\n2\n'in out
RESULT['whole_original_q_fiber_dimension']=2
# Exact h local triple-center equality on U=8pt+25!=0.
fs=[S.sympify(x)for x in re.findall(r'^C\[\d+\]=(.*)$',(P/'c2a5_first_triple1.log').read_text(),re.M)];rr=S.solve(fs[1],r)[0];fbase=S.factor(fs[2].subs(r,rr))
for f in fs[3:]:
 quotient=S.cancel(f.subs(r,rr)/fbase);den=S.denom(quotient)
 while den.free_symbols:
  den_next,rem=S.div(den,8*p*t+25,p,t,s,r);assert rem==0;assert S.total_degree(den_next)<S.total_degree(den);den=den_next
 assert den!=0 # denominator is precisely a nonzero constant times a power of U
runpy('c2a5_h_triple_charts.py')
hrows=json.loads((P/'c2a5_h_triple_jacobian_points.json').read_text())
for row in[hrows[0],hrows[2]]:
 val=minor(row['chart'],row['rows'],row['columns'],kind='h');assert S.expand(val-S.sympify(row['determinant']))==0
RESULT['h_triple_boundary_minors']='PASS'
# Replay the full strict DD ideal on the h middle chart, then the finite jet argument.
runpy('build_h_last_center.py')
out=runsing('c2a5_h_R_dd.sing');assert'DIM\n2\n'in out
runpy('verify236_h_jet.py')
RESULT['h_last_germ']='PASS smooth conic plus nonzero pure B cubic'
z=subprocess.run(['gap','-q',str(P/'transfer234_237.g')],capture_output=True,text=True,timeout=None);assert z.returncode==0 and'TRANSFER_234_237_PASS'in z.stdout
RESULT['representation_transfer']='PASS all120 character values236and237';RESULT['status']='PASS_GEOMETRIC_YES_236_237'
(P/'certificate236_geometry.json').write_text(json.dumps(RESULT,indent=2)+'\n')
files=[f for f in P.iterdir()if f.is_file()and(f.name.startswith('c2a5_')or f.name in['PROOF236.md','validate236_geometry.py','verify236_h_jet.py','a5_discriminant_input.json','transfer234_237.g'])and f.suffix in['.py','.sing','.json','.md']and not f.name.startswith('c2a5_h_R_dd_chart')and not f.name.startswith('c2a5_h_R_dd_local_equality')]
(P/'SHA256_236_geometry.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in files},indent=2)+'\n');print(RESULT['status'],flush=True)
