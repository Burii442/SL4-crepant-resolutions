from pathlib import Path
import sympy as S,json,subprocess,re
P=Path(__file__).resolve().parent; data=json.loads((P/'a5_discriminant_input.json').read_text());p,q,r,h,s,t,w=S.symbols('p q r h s t w'); gs=[S.sympify(x['polynomial']) for x in data['strata'][0]['ideal_generators']]
def even(f,chart):
 out=0
 for (iq,ih),coef in S.Poly(f,q,h).terms():
  assert (iq+ih)%2==0
  out+=coef*s**((iq+ih)//2)*t**(ih if chart==0 else iq)
 return S.expand(out)
def ss(f):return re.sub(r'\^(\d+)',r'^(\1)',str(f).replace('**','^'))
for chart in[0,1]:
 D=S.sympify(data['central_extension_C2xA5']['two_charts'][chart]['D']).subs(S.Symbol('v'),t)
 pol=[gs[0],gs[2],gs[3],q*gs[1],h*gs[1]];isub=[even(f,chart) for f in pol]
 code='LIB "elim.lib";option(noredefine);option(redSB);short=0;ring R=0,(p,r,s,t,w),dp;short=0;\npoly F=w^2-('+ss(D)+');\nideal raw=F,w,'+','.join(map(ss,isub))+';\nideal C=std(sat(raw,ideal(s)));print("STRICT_TRIPLE_BEGIN");C;print("STRICT_TRIPLE_END");print("DIM");dim(C);print("DONE");quit;\n'
 f=P/f'c2a5_first_triple{chart}.sing';f.write_text(code);z=subprocess.run(['Singular','-q',str(f)],capture_output=True,text=True,timeout=None);(P/f'c2a5_first_triple{chart}.log').write_text(z.stdout);assert '?' not in z.stdout and'DONE'in z.stdout;print(chart,z.stdout,flush=True)
