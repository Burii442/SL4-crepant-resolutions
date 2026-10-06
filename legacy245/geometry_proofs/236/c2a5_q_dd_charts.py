from pathlib import Path
import sympy as S,json,re,subprocess,concurrent.futures,time
P=Path(__file__).resolve().parent;p,r,t,L,a,b=S.symbols('p r t L a b');u,V=S.symbols('u V');d=json.loads((P/'c2a5_q_triple_charts.json').read_text());m=json.loads((P/'c2a5_q_L_dd_reduced.json').read_text());J=S.sympify(m['J']);r0=S.sympify(m['substitutions']['r']);L0=S.sympify(m['substitutions']['L']);F=[S.sympify(z) for z in d['charts'][0]['equations']]
# Coordinates u=r-r0,V=L-L0 are polynomial automorphisms; J depends only p,t,b.
FF=[S.expand(f.subs({r:u+r0,L:V+L0},simultaneous=True)) for f in F];B=S.groebner([J],b,p,t);rred=B.reduce(r0)[1];Lred=B.reduce(L0)[1]
# Replace representatives modulo J to reduce coefficient size without changing ideal.
FF=[S.expand(f.subs({r:u+rred,L:V+Lred},simultaneous=True)) for f in F];gens=[a,u,J,V];y=S.symbols('y0:4');v=S.symbols('v')
def ss(f):return re.sub(r'\^(\d+)',r'^(\1)',str(S.expand(f)).replace('**','^'))
result={'J':str(J),'r0_reduced':str(rred),'L0_reduced':str(Lred),'equations':list(map(str,FF))};(P/'c2a5_q_dd_normal_input.json').write_text(json.dumps(result,indent=2)+'\n')
for j in range(4):
 vs=[p,t,b,u,V,a]+[y[i] for i in range(4) if i!=j]+[v];raw=FF+[g-v*(1 if i==j else y[i]) for i,g in enumerate(gens)]
 code='LIB "elim.lib";option(noredefine);option(redSB);ring R=0,('+','.join(map(str,vs))+'),dp;short=0;\nideal raw='+','.join(map(ss,raw))+';print("SAT_START");ideal C=std(sat(raw,ideal(v)));print("DIM");dim(C);print("RELS_BEGIN");C;print("RELS_END");\nideal CF=std(C+ideal(p,t,b,u,V,a,v));print("FIBER_DIM");dim(CF);print("FIBER_BEGIN");CF;print("FIBER_END");print("DONE");quit;\n'
 (P/f'c2a5_q_dd_chart{j}.sing').write_text(code)
def run(j):
 start=time.time();f=P/f'c2a5_q_dd_chart{j}.sing'
 try:
  z=subprocess.run(['Singular','-q',str(f)],capture_output=True,text=True,timeout=None);(P/f'c2a5_q_dd_chart{j}.log').write_text(z.stdout);row=dict(chart=j,seconds=round(time.time()-start,3),status='PASS' if '?' not in z.stdout and 'DONE'in z.stdout else'ERROR')
 except subprocess.TimeoutExpired as e:
  out=e.stdout or b'';(P/f'c2a5_q_dd_chart{j}.log').write_bytes(out);row=dict(chart=j,status='TIMEOUT_150S')
 print(row,flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:result['runs']=list(ex.map(run,range(4)))
(P/'c2a5_q_dd_charts_results.json').write_text(json.dumps(result,indent=2)+'\n')

assert all(row["status"]=="PASS" for row in result['runs']), "At least one full chart calculation failed"
