"""Construct the final h-chart center from the freshly generated Rees equations."""
from pathlib import Path
import json,re
import sympy as S
P=Path(__file__).resolve().parent
p,q,r,h,s,t,w=S.symbols('p q r h s t w')
d=json.loads((P/'a5_discriminant_input.json').read_text())
ks=[S.sympify(x['polynomial']) for x in d['strata'][1]['ideal_generators']]
def even(f):
    out=0
    for (iq,ih),coef in S.Poly(f,q,h).terms():
        assert (iq+ih)%2==0
        out+=coef*s**((iq+ih)//2)*t**iq
    return S.expand(out)
def fmt(f):return re.sub(r'\^(\d+)',r'^(\1)',str(f).replace('**','^'))
source=(P/'c2a5_h_triple_chart1.sing').read_text()
raw=source.split('ideal raw=',1)[1].split(';',1)[0]
generators=[w]+[even(f) for f in [ks[0],ks[2],ks[3],q*ks[1],h*ks[1]]]
code='LIB "elim.lib";option(noredefine);option(redSB);ring R=0,(p,r,s,t,w,y0,y2,v),dp;short=0;\nideal raw='+raw+';print("SAT_START");ideal C=std(sat(raw,ideal(v*(8*p*t+25))));\nideal rawDD=C+ideal('+','.join(map(fmt,generators))+');print("DD_START");ideal center=std(sat(rawDD,ideal(v*s*(8*p*t+25))));print("DD_CENTER_BEGIN");center;print("DD_CENTER_END");print("DIM");dim(center);print("DONE");quit;\n'
(P/'c2a5_h_R_dd.sing').write_text(code)
print('FINAL_H_CENTER_GENERATED_FROM_CURRENT_INPUTS',flush=True)
