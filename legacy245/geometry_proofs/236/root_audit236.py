"""Independent algebraic binding and whole-fiber covering for candidate236/237."""
from pathlib import Path
import sympy as S,json,re,subprocess
P=Path(__file__).resolve().parent;R=P
p,q,r,h,s,t,w,L,a,b,u,V,v=S.symbols('p q r h s t w L a b u V v'); y=S.symbols('y0:4')
def readj(name):return json.loads((R/name).read_text())
def parse(name,prefix='C'):return [S.sympify(x) for x in re.findall(r'^'+prefix+r'\[\d+\]=(.*)$',(R/name).read_text(),re.M)]
def fmt(f):return re.sub(r'\^(\d+)',r'^(\1)',str(S.expand(f)).replace('**','^'))
def sing(name,variables,code):
 source='LIB "elim.lib";option(noredefine);ring R=0,('+','.join(map(str,variables))+'),dp;\n'+code+'\nprint("AUDIT_PASS");quit;\n';path=R/(name+'.sing');path.write_text(source)
 z=subprocess.run(['Singular','-q',str(path)],capture_output=True,text=True,timeout=None);(R/(name+'.log')).write_text(z.stdout+z.stderr);assert z.returncode==0 and '?' not in z.stdout and 'AUDIT_PASS' in z.stdout,(name,z.stdout[-2000:])
def equality(name,vars,A,B,tail=''):
 code='ideal A='+','.join(map(fmt,A))+';ideal B='+','.join(map(fmt,B))+';ideal AA=std(A);ideal BB=std(B);if(size(reduce(AA,BB))!=0 || size(reduce(BB,AA))!=0){ERROR("UNEQUAL_IDEALS");}\n'+tail
 sing(name,vars,code)
D=S.sympify(readj('a5_discriminant_input.json')['central_extension_C2xA5']['two_charts'][0]['D']).subs(S.Symbol('v'),t)
m=readj('c2a5_q_first_model.json');s0=S.sympify(m['s0']);K=S.sympify(m['K']);DL=S.expand(D.subs(s,s0+L));assert S.expand(DL-S.sympify(m['D_in_L']))==0
assert all(S.expand(DL.coeff(L,int(k))-S.sympify(f))==0 for k,f in m['coefficients'].items())
equality('root_q_first_center',[p,r,s,t,w],parse('c2a5_first_triple0.log'),[w,s-s0,K])
H=parse('c2a5_first_triple1.log');lam=S.Symbol('lam');U=8*p*t+25
equality('root_h_first_center_local',[lam,p,r,s,t,w],H+[lam*U-1],H[:3]+[lam*U-1])
F=[S.sympify(f) for f in readj('c2a5_q_triple_charts.json')['charts'][0]['equations']]
co={int(k):S.sympify(f) for k,f in m['coefficients'].items()};a0=S.cancel(co[0]/K**2);c1=S.cancel(co[1]/K);a2=co[2]
assert S.expand(F[0]-(K-L*b))==0 and S.expand(F[1]-(a*a-a0*b*b-c1*b-a2-108*t*L))==0
# Explicitly confirm the proposed complete intersection is saturated in the pivot.
sing('root_q_L_Rees_saturation',[p,r,t,L,a,b],'ideal A='+','.join(map(fmt,F))+';ideal B=std(sat(A,ideal(L)));ideal AA=std(A);if(size(reduce(B,AA))!=0 || size(reduce(AA,B))!=0){ERROR("NOT_REES");}')
cen=readj('c2a5_q_L_dd_reduced.json');J=S.sympify(cen['J']);r0=S.sympify(cen['substitutions']['r']);L0=S.sympify(cen['substitutions']['L'])
equality('root_q_last_center',[p,r,t,L,a,b],parse('c2a5_q_L_dd.log','center'),[a,r-r0,L-L0,J])
normal=readj('c2a5_q_dd_normal_input.json');rred=S.sympify(normal['r0_reduced']);Lred=S.sympify(normal['L0_reduced']);GB=S.groebner([J],b,p,t)
assert GB.reduce(rred-r0)[1]==0 and GB.reduce(Lred-L0)[1]==0
FF=[S.expand(f.subs({r:u+rred,L:V+Lred},simultaneous=True)) for f in F]
assert all(S.expand(x-S.sympify(z))==0 for x,z in zip(FF,normal['equations']))
for j in range(4):
 source=(R/f'c2a5_q_dd_chart{j}.sing').read_text();text=source.split('ideal raw=',1)[1].split(';',1)[0]
 raw=[S.sympify(x) for x in text.split(',')];expected=FF+[z-v*(1 if i==j else y[i]) for i,z in enumerate([a,u,J,V])]
 assert len(raw)==len(expected) and all(S.expand(x-z)==0 for x,z in zip(raw,expected))
# Whole q fiber cover: charts2/3, then chart0, then the residual chart1 direction.
zero={z:0 for z in [p,t,b,u,V,a,v]}
minors=readj('c2a5_q_dd_jacobian.json');special=readj('c2a5_q_dd_jacobian_special.json');alt=readj('c2a5_q_dd_cover.json')
assert S.sympify(minors[3]['determinant'])==-229582512
assert S.expand(S.sympify(minors[2]['determinant'])+34992*(9*y[1]-16))==0
f=S.sympify(minors[0]['determinant']).subs({y[2]:0,y[3]:0});assert S.expand(f-5832*(27*y[1]**2+1)**3)==0
assert S.rem(S.sympify(alt[0]['determinant']),27*y[1]**2+1,y[1])==-663552
# Recompute the intermediate minor, not just its saved polynomial.
rows=special[1]['rows'];cols=special[1]['columns'];fs=parse('c2a5_q_dd_chart2.log');vars=[S.Symbol(z) for z in cols]
M=S.Matrix([[S.diff(fs[i-1],z).subs(zero).subs({y[1]:S.Rational(16,9),y[3]:0}) for z in vars] for i in rows]);det=S.factor(M.det());assert S.expand(det-11664*(3*y[0]**2-2048))==0
assert S.rem(S.sympify(alt[1]['determinant']),3*y[0]**2-2048,y[0])==450953216
# chart1 boundary not already in2/3, at y0=0, has a constant nonzero minor.
rest=S.sympify(minors[1]['determinant']).subs({y[0]:0,y[2]:0,y[3]:0});assert rest!=0
# All nonzero h fiber points are smooth by exact 4x4 minors.
hchecks=[]
for j,ratio,expected in [(0,y[2],9375000*y[2]),(2,y[0],421875000*y[0])]:
 fs=parse(f'c2a5_h_triple_chart{j}.log');base={z:0 for z in [p,r,s,t,w,v]};M=S.Matrix([[S.diff(fs[i-1],z).subs(base) for z in [w,r,s,ratio]] for i in [1,2,3,7]])
 det=S.expand(M.det());assert det==expected
 cf=[S.expand(z.subs(base)) for z in parse(f'c2a5_h_triple_chart{j}.log','CF')];ys=[y[i] for i in range(3) if i!=j]
 assert S.groebner(cf+[det],*ys).contains(S.Integer(1))
 hchecks.append(dict(chart=j,minor=str(det),nonvanishing_on_entire_fiber=True))
res=dict(status='PASS_INDEPENDENT_236_INPUT_CENTERS_REES_AND_COVER',discriminant_substitution=True,first_centers_exact=True,q_L_is_full_Rees_chart=True,last_q_center_exact=True,four_q_Rees_inputs_bound=True,whole_q_fiber_cover=True,whole_h_fiber_outside_intersection=hchecks,last_h_germ='certificate236_h_jet.json')
(P/'root_audit236_certificate.json').write_text(json.dumps(res,indent=2)+'\n');print(res['status'])
