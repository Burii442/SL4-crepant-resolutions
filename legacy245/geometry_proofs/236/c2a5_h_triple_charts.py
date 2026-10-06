from pathlib import Path
import sympy as S,json,re,subprocess,concurrent.futures,time
P=Path(__file__).resolve().parent;p,r,s,t,w=S.symbols('p r s t w');d=json.loads((P/'a5_discriminant_input.json').read_text());D=S.sympify(d['central_extension_C2xA5']['two_charts'][1]['D']).subs(S.Symbol('v'),t);C=[S.sympify(x) for x in re.findall(r'^C\[\d+\]=(.*)$',(P/'c2a5_first_triple1.log').read_text(),re.M)];gens=C[:3];y=S.symbols('y0:3');v=S.symbols('v')
def ss(f):return re.sub(r'\^(\d+)',r'^(\1)',str(S.expand(f)).replace('**','^'))
for j in range(3):
 vs=[p,r,s,t,w]+[y[i] for i in range(3) if i!=j]+[v];raw=[w*w-D]+[g-v*(1 if i==j else y[i])for i,g in enumerate(gens)]
 code='LIB "elim.lib";option(noredefine);option(redSB);ring R=0,('+','.join(map(str,vs))+'),dp;short=0;\nideal raw='+','.join(map(ss,raw))+';print("SAT_START");ideal C=std(sat(raw,ideal(v*(8*p*t+25))));print("DIM");dim(C);print("RELS_BEGIN");C;print("RELS_END");ideal CF=std(C+ideal(p,r,s,t,w,v));print("FIBER_DIM");dim(CF);print("FIBER_BEGIN");CF;print("FIBER_END");print("DONE");quit;\n';(P/f'c2a5_h_triple_chart{j}.sing').write_text(code)
def run(j):
 start=time.time()
 try:
  z=subprocess.run(['Singular','-q',str(P/f'c2a5_h_triple_chart{j}.sing')],capture_output=True,text=True,timeout=None);(P/f'c2a5_h_triple_chart{j}.log').write_text(z.stdout);row=dict(chart=j,status='PASS'if'?'not in z.stdout and'DONE'in z.stdout else'ERROR',seconds=round(time.time()-start,3))
 except subprocess.TimeoutExpired as e:
  (P/f'c2a5_h_triple_chart{j}.log').write_bytes(e.stdout or b'');row=dict(chart=j,status='TIMEOUT100')
 print(row,flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:rows=list(ex.map(run,range(3)))
(P/'c2a5_h_triple_results.json').write_text(json.dumps(rows,indent=2)+'\n')

assert all(row["status"]=="PASS" for row in rows), "At least one full chart calculation failed"
