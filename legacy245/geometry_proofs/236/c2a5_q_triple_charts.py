from pathlib import Path
import sympy as S,json,subprocess,re,concurrent.futures
P=Path(__file__).resolve().parent;d=json.loads((P/'a5_discriminant_input.json').read_text());m=json.loads((P/'c2a5_q_first_model.json').read_text());p,q,r,h,s,t,w,L,a,b=S.symbols('p q r h s t w L a b');s0=S.sympify(m['s0']);K=S.sympify(m['K']);co={int(i):S.sympify(x) for i,x in m['coefficients'].items()};a0=S.cancel(co[0]/K**2);c1=S.cancel(co[1]/K);a2=co[2]
def ss(f):return re.sub(r'\^(\d+)',r'^(\1)',str(S.expand(f)).replace('**','^'))
def even(f):
 out=0
 for (iq,ih),coef in S.Poly(f,q,h).terms():
  assert(iq+ih)%2==0
  out+=coef*s**((iq+ih)//2)*t**ih
 return S.expand(out)
ks=[S.sympify(x['polynomial']) for x in d['strata'][1]['ideal_generators']];dd=[even(f).subs(s,s0+L) for f in [ks[0],ks[2],ks[3],q*ks[1],h*ks[1]]]
# The L chart has K=L*b and w=L*a.
F1=K-L*b;F2=a*a-a0*b*b-c1*b-a2-108*t*L
code='LIB "elim.lib";option(noredefine);option(redSB);ring R=0,(p,r,t,L,a,b),dp;short=0;\npoly F1='+ss(F1)+';poly F2='+ss(F2)+';poly s='+ss(s0+L)+';\nideal raw=F1,F2,L*a,'+','.join(map(ss,dd))+';\nprint("SAT_START");ideal center=std(sat(raw,ideal(L*s)));print("DD_CENTER_BEGIN");center;print("DD_CENTER_END");print("CENTER_DIM");dim(center);print("DONE");quit;\n'
(P/'c2a5_q_L_dd.sing').write_text(code)
fibers=[]
for name,vars,FF,zero in [('L',[p,r,t,L,a,b],[F1,F2],{p:0,r:0,L:0}),('K',[p,r,t,a,b],[a*a-a0-c1*b-a2*b*b-108*t*K*b**3],{p:0,r:0}),('w',[p,r,t,w,a,b],[K-w*b,1-a0*b*b-c1*a*b-a2*a*a-108*t*w*a**3],{p:0,r:0,w:0})]:
 fs=[S.factor(x.subs(zero)) for x in FF];print(name,fs,flush=True);fibers.append({'chart':name,'vars':list(map(str,vars)),'equations':list(map(str,FF)),'central_fiber':list(map(str,fs))})
(P/'c2a5_q_triple_charts.json').write_text(json.dumps({'charts':fibers,'a0':str(a0),'c1':str(c1),'a2':str(a2)},indent=2)+'\n')
z=subprocess.run(['Singular','-q',str(P/'c2a5_q_L_dd.sing')],capture_output=True,text=True,timeout=None);(P/'c2a5_q_L_dd.log').write_text(z.stdout);print(z.stdout,flush=True)
