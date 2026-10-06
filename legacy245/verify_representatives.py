#!/usr/bin/env sage -python
"""Verify every nonidentity affine representative transfer by full group equality.

Run: sage -python verify_representatives.py --output verification/representatives.json
The rational matrices in representative_conjugacies.json are witnesses, not
precomputed truth values: both matrix groups and all conjugates are rebuilt.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
from sage.all import QQ, matrix
from verify_catalogue import closure, immutable, require
HERE=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=HERE/'verification/representatives.json')
    args=p.parse_args();start=time.time()
    catalogue=json.loads((HERE/'catalogue.json').read_text())
    entries={r['index']:r for r in catalogue}
    data=json.loads((HERE/'representative_conjugacies.json').read_text())['witnesses']
    expected={r['index']:r['representative'] for r in catalogue if r['index']!=r['representative']}
    require(len(data)==len(expected) and {r['index']:r['representative'] for r in data}==expected,'Conjugacy witnesses must cover every nonidentity catalogue transfer exactly once')
    groups={}
    def group(i):
        if i not in groups:
            r=entries[i]
            groups[i]=closure([immutable(matrix(QQ,g)) for g in r['actual_generators']],r['order'])
            require(len(groups[i])==r['order'],f'{i}: group order')
        return groups[i]
    verified=[]
    for witness in data:
        i,j=witness['index'],witness['representative']
        P=matrix(QQ,witness['P']);require(P.nrows()==P.ncols()==4 and P.det()!=0,f'{i}: singular intertwiner')
        Pi=P.inverse();images={immutable(P*g*Pi) for g in group(j)}
        require(images==group(i),f'{i}: full conjugacy with {j} failed')
        verified.append({'index':i,'representative':j,'order':len(images),'determinant':str(P.det()),'all_group_elements_compared':len(images)})
    result={'status':'PASS','transfers':len(verified),'element_comparisons':sum(r['order'] for r in verified),
        'catalogue_sha256':hashlib.sha256((HERE/'catalogue.json').read_bytes()).hexdigest(),
        'witnesses_sha256':hashlib.sha256((HERE/'representative_conjugacies.json').read_bytes()).hexdigest(),
        'scope':'Exact rational conjugacy of whole matrix groups; affine quotients only.',
        'seconds':round(time.time()-start,3),'records':verified}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':main()
