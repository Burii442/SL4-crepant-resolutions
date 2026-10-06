#!/usr/bin/env python3
"""Exact public Part VI witnesses. Python standard library only.
Read catalogue.json beside this script and close the original matrix groups; check their
matrix groups anew, check every stabilizer element and every matrix in each
positive conjugated group. Does not read prior PASS outputs or group closures.
Usage: python3 verify_compact_cases.py [--output result.json]
"""
from __future__ import annotations
import argparse,json,hashlib
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parent
CATALOGUE=ROOT/'catalogue.json'
CASES={d['index']:d for d in json.loads(CATALOGUE.read_text())}
ID=tuple(int(i==j) for i in range(4) for j in range(4))

def flat(a):return tuple(x for row in a for x in row)
def rows(a):return [list(a[4*i:4*i+4]) for i in range(4)]
def mm(a,b):return tuple(sum(a[4*i+k]*b[4*k+j]for k in range(4))for i in range(4)for j in range(4))
def rank(a):
 a=[[Fraction(x)for x in row]for row in a];nr=len(a);nc=len(a[0]);r=0
 for c in range(nc):
  p=next((i for i in range(r,nr)if a[i][c]),None)
  if p is None:continue
  a[r],a[p]=a[p],a[r];v=a[r][c];a[r]=[x/v for x in a[r]]
  for i in range(nr):
   if i!=r:
    v=a[i][c];a[i]=[x-v*y for x,y in zip(a[i],a[r])]
  r+=1
 return r

def det(a):
 from itertools import permutations
 out=0
 for p in permutations(range(4)):
  sign=(-1)**sum(p[i]>p[j]for i in range(4)for j in range(i+1,4));term=sign
  for i in range(4):term*=a[4*i+p[i]]
  out+=term
 return out

def inverse(a):
 b=[[Fraction(a[4*i+j])for j in range(4)]+[Fraction(i==j)for j in range(4)]for i in range(4)]
 for c in range(4):
  p=next(i for i in range(c,4)if b[i][c]);b[c],b[p]=b[p],b[c]
  v=b[c][c];b[c]=[x/v for x in b[c]]
  for i in range(4):
   if i!=c:
    v=b[i][c];b[i]=[x-v*y for x,y in zip(b[i],b[c])]
 out=tuple(b[i][j]for i in range(4)for j in range(4,8))
 assert all(x.denominator==1 for x in out)
 return tuple(int(x)for x in out)

def closure(gens):
 todo=[ID];seen={ID}
 for a in todo:
  for b in gens:
   p=mm(a,b)
   if p not in seen:
    assert len(seen)<10000,"unexpected non-finite or oversized input"
    seen.add(p);todo.append(p)
 return seen

def group(i):
 p=CATALOGUE;data=CASES[i]
 assert data['index']==i
 es=closure([flat(a)for a in data['actual_generators']]);assert len(es)==data['order']
 return es,hashlib.sha256(p.read_bytes()).hexdigest()

WITNESSES=[(41,3,[0,1,1,0],3,1),(42,3,[0,0,0,1],3,1),
 (60,2,[0,1,0,1],2,1),(62,2,[0,1,0,0],2,1),
 (118,2,[0,0,0,1],6,3),(119,2,[0,0,1,0],4,1),
 (120,2,[0,0,1,0],2,1),(149,4,[1,0,1,2],4,2),
 (200,3,[1,2,1,0],6,2),(201,3,[1,2,2,0],3,1)]
POSITIVE=[
 (43,0,[[1,0,0,0],[0,-2,1,-1],[0,1,0,-1],[0,1,-1,1]]),
 (61,2,[[1,0,-1,0],[0,1,0,-1],[0,0,0,1],[0,0,1,0]]),
 (150,4,[[1,0,-1,0],[0,0,1,0],[0,1,-1,0],[0,0,-1,-1]]),
 (199,3,[[1,0,0,0],[0,1,0,0],[0,0,-1,1],[0,0,0,1]]),
 (226,6,[[1,0,0,0],[0,1,0,0],[0,0,-1,0],[0,0,-1,1]])]
A={2:[[-1,0],[0,-1]],3:[[-1,1],[-1,0]],4:[[0,-1],[1,0]],6:[[0,1],[-1,1]]}
SWAP=flat([[0,0,1,0],[0,0,0,1],[1,0,0,0],[0,1,0,0]])

def invariant_forms(gens):
 from itertools import combinations
 pairs=list(combinations(range(4),2));basis=[]
 for i,j in pairs:
  b=[[0]*4 for _ in range(4)];b[i][j]=1;b[j][i]=-1;basis.append(flat(b))
 equations=[]
 for g in gens:
  gt=tuple(g[4*j+i]for i in range(4)for j in range(4))
  columns=[tuple(x-y for x,y in zip(mm(mm(gt,b),g),b))for b in basis]
  equations.extend([[Fraction(col[k])for col in columns]for k in range(16)])
 pivots=[];r=0
 for c in range(6):
  p=next((i for i in range(r,len(equations))if equations[i][c]),None)
  if p is None:continue
  equations[r],equations[p]=equations[p],equations[r]
  v=equations[r][c];equations[r]=[x/v for x in equations[r]]
  for i in range(len(equations)):
   if i!=r:
    v=equations[i][c];equations[i]=[x-v*y for x,y in zip(equations[i],equations[r])]
  pivots.append(c);r+=1
 kernel=[]
 for f in set(range(6))-set(pivots):
  b=[Fraction(0)]*6;b[f]=1
  for j,p in enumerate(pivots):b[p]=-equations[j][f]
  kernel.append(b)
 def pf(a):return a[0]*a[5]-a[1]*a[4]+a[2]*a[3]
 nondegenerate=any(pf(x) for x in kernel)
 nondegenerate|=any(pf([a+b for a,b in zip(x,y)])for x,y in combinations(kernel,2))
 return len(kernel),bool(nondegenerate)

def run():
 negative=[];positive=[]
 form_records=[];candidates=[]
 for i in range(1,246):
  data=CASES[i]
  dim,sympl=invariant_forms([flat(g)for g in data['actual_generators']])
  form_records.append(dict(index=i,invariant_two_form_dimension=dim,nondegenerate_invariant_form=sympl))
  if sympl and dim==1:candidates.append(i)
 fail_reflection=[112,113,115,116,121,139,153,208,209,213]
 fail_affine=[89,90,98,99,159,164,172,202,203,211,212]
 assert set(candidates)==set(fail_reflection+fail_affine+[w[0]for w in WITNESSES]+[p[0]for p in POSITIVE])
 for i in fail_reflection:
  es,_=group(i)
  refl=[g for g in es if rank(rows(tuple(x-y for x,y in zip(g,ID))))==2]
  assert len(closure(refl))<len(es)
 for i,n,a,st_expected,r_expected in WITNESSES:
  es,sha=group(i)
  st={g for g in es if all((sum(g[4*j+k]*a[k]for k in range(4))-a[j])%n==0 for j in range(4))}
  refl=[g for g in st if rank(rows(tuple(x-y for x,y in zip(g,ID))))==2]
  reflgroup=closure(refl)
  assert reflgroup<=st and len(st)==st_expected and len(reflgroup)==r_expected<len(st)
  negative.append(dict(index=i,denominator=n,numerator=a,group_order=len(es),
   full_stabilizer_order=len(st),reflection_subgroup_order=len(reflgroup),
   full_stabilizer=[rows(g)for g in sorted(st)],reflections=[rows(g)for g in sorted(refl)],
   reflection_subgroup=[rows(g)for g in sorted(reflgroup)],input_sha256=sha))
 for i,m,p in POSITIVE:
  es,sha=group(i);p=flat(p);assert abs(det(p))==1;pi=inverse(p)
  if m==0:model=flat([[-1,0,-1,0],[0,-1,0,-1],[0,0,1,0],[0,0,0,1]])
  else:
   a=A[m];model=flat([[a[0][0],a[0][1],0,0],[a[1][0],a[1][1],0,0],[0,0,1,0],[0,0,0,1]])
  gs=closure([model,SWAP]);conjugated={mm(mm(pi,g),p)for g in es};assert gs==conjugated
  positive.append(dict(index=i,group_order=len(es),P=rows(p),determinant=det(p),
   model=('A2_root_lattice'if m==0 else f'C{m}_wreath_S2'),
   model_generators=[rows(model),rows(SWAP)],input_sha256=sha))
 return dict(result='ALL_TEN_FULL_STABILIZERS_AND_FIVE_INTEGRAL_MODELS_VERIFIED',
  all_245_invariant_forms=form_records,candidates=candidates,fail_reflection=fail_reflection,
  affine_cotangent_exclusions=fail_affine,negative=negative,positive=positive,
  method='fresh invariant alternating forms and Pfaffian polynomial; exact matrix closure; rational Gaussian ranks; determinant and complete conjugated-set equality')

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
 result=run();s=json.dumps(result,indent=2)
 if args.output:args.output.write_text(s+'\n')
 print(result['result'])
 for r in result['negative']:print('NO',r['index'],r['full_stabilizer_order'],r['reflection_subgroup_order'])
 for r in result['positive']:print('YES',r['index'],r['model'],r['determinant'])
