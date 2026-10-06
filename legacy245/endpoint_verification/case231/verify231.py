#!/usr/bin/env sage-python
"""Case 231: all six one-junior charts, bound to the public full Cox ideal."""
from pathlib import Path
import sys,json,re,subprocess,hashlib,time,argparse,itertools
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from common import *
from executables import singular_executable
def run(out):
    start=time.time();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True);d,A,F,Q,D=load_model(231)
    assert list(Q[0])==[0,0,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,2] and Q==D
    chi=vector(ZZ,[-1]);opens=[j for j in range(15) if Q[0,j]<0];assert opens==[3,5,7,9,11,13]
    assert all(Q[0,j]==-1 for j in opens);adm=admissibility(231,F,D,chi)
    data=json.loads((SUPPLEMENT/'231/invariants.json').read_text());Y=PolynomialRing(QQ,names=data['polynomial_coordinate_order']);inv=list(map(Y,data['generator_polynomials']));y=Y.gens();nu=data['valuation_matrix'][0]
    target=None
    for p in itertools.permutations(range(4)):
        images=[f(*[y[j] for j in p]) for f in inv];mapping=[]
        for f in images:
            candidates=[(j,sign) for j,g in enumerate(inv) for sign in [1,-1] if f==sign*g]
            if len(candidates)!=1:break
            mapping.append(candidates[0])
        if len(mapping)==14 and len({j for j,sign in mapping})==14 and all(nu[i]==nu[j] for i,(j,sign) in enumerate(mapping)) and all(mapping[a][0]==b for a,b in [(3,5),(7,9),(11,13)]):target=(p,mapping);break
    assert target is not None,'explicit normalizer exchanging the three chart pairs'
    p,mapping=target;images=[str(sign)+'*t'+str(j+1) for j,sign in mapping]+['e']
    inverse=['']*15
    for i,(j,sign) in enumerate(mapping):inverse[j]=str(sign)+'*t'+str(i+1)
    inverse[-1]='e'
    def rename(s):return re.sub(r'\bu(\d+)\b',lambda m:'t'+m.group(1),s).replace('e1','e')
    source='LIB "primdec.lib";LIB "presolve.lib";LIB "sing.lib";option(noredefine);\nring PullRing=0,('+','.join('t'+str(j) for j in range(1,15))+',e),dp;\nideal IX='+','.join(rename(s) for s in d['equations'])+';\nIX=std(IX);\n'
    source+='map normalizer=PullRing,'+','.join(images)+';\nmap inverseNormalizer=PullRing,'+','.join(inverse)+';\n"NORMALIZER_FORWARD";size(simplify(reduce(normalizer(IX),IX),2));\n"NORMALIZER_REVERSE";size(simplify(reduce(inverseNormalizer(IX),IX),2));\n'
    source+='ideal chartI=std(IX+ideal(t4-1));\n'
    source+=(Path(__file__).resolve().parent/'chart_proof.sing').read_text();script=out/'proof.sing';script.write_text(source)
    binary=singular_executable();log=out/'proof.log'
    with log.open('w') as f:proc=subprocess.run([str(binary),'-q',str(script)],stdout=f,stderr=subprocess.STDOUT)
    text=log.read_text();assert proc.returncode==0 and not re.search(r'^\s*\?',text,re.M) and 'ENDPOINT231_DONE' in text,text[-6000:]
    expected={'NORMALIZER_FORWARD':0,'NORMALIZER_REVERSE':0,'CHART4_ALL15_INVERSE_COORDINATES':0,'selected minors certify the whole t4 chart over Q':1,'CHART8_ELIMINATION_FORWARD':0,'CHART8_ELIMINATION_REVERSE':0,'CHART8_RETRACTION':0,'CHART8_DIMENSION':4,'CHART12_ELIMINATION_FORWARD':0,'CHART12_ELIMINATION_REVERSE':0,'CHART12_RETRACTION':0,'CHART12_DIMENSION':4,'CHART12_POLYNOMIAL':0,'CHART8_WHOLE_SMOOTH':1}
    for marker,value in expected.items():assert re.findall(r'^'+re.escape(marker)+r'\n(-?\d+)\s*$',text,re.M)==[str(value)],marker
    result={'case':231,'status':'PASS','complete':True,'semistable_coordinate_opens':[j+1 for j in opens],'full_cover_by_negative_weight_coordinates':True,'normalizer_coordinate_permutation':[j+1 for j in p],'normalizer_invariant_signed_permutation':[[j+1,sign] for j,sign in mapping],'normalizer_preserves_full_public_ideal_both_directions':True,'admissibility':adm,'checks':expected,'seconds':time.time()-start}
    (out/'certificate.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);args=p.parse_args();run(args.output_dir)
