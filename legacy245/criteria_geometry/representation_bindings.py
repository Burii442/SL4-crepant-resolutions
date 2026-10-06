"""Recompute 25 complete representation intertwiners and reflection prerequisites."""
from sage.all import *
from pathlib import Path
from itertools import product
import ast,json,hashlib,time
H=Path(__file__).resolve().parent
rawpath=H/'catalogue.json'
records=json.loads(rawpath.read_text()); assert [r['index'] for r in records]==list(range(1,246))
raw=[r['actual_generators'] for r in records]
K=CyclotomicField(12);z=K.gen();ii=z**3;w=z**4
models={}
models['I']=([diagonal_matrix(K,[-1,1,1,-1]),diagonal_matrix(K,[1,-1,1,-1]),diagonal_matrix(K,[1,1,-1,-1]),matrix(K,[[0,1,0,0],[1,0,0,0],[0,0,0,1],[0,0,1,0]])],list(range(100,105)))
models['H']=([matrix(K,g) for g in raw[153]],list(range(154,159)))
def cot(g):return block_diagonal_matrix(g,g.inverse().transpose())
models['D_A2']=([cot(matrix(K,[[0,-1],[1,-1]])),cot(matrix(K,[[0,1],[1,0]]))],[41,42,43])
for m,ids in [(2,[60,61,62]),(3,[199,200,201]),(4,[149,150]),(6,[226])]:
 models['D_G_%s_1_2'%m]=([cot(diagonal_matrix(K,[z**(12//m),1])),cot(matrix(K,[[0,1],[1,0]]))],ids)
models['D_G4']=([cot(diagonal_matrix(K,[ii,-ii])),cot(matrix(K,[[0,1],[-1,0]])),cot(w*matrix(K,[[-1+ii,1+ii],[-1+ii,-1-ii]])/2)],[118,119,120])
def data(A):return [[str(x) for x in r] for r in A.rows()]
def binding(sgens,tgens):
 S=MatrixGroup(sgens);T=MatrixGroup(tgens);sg=S.gap();tg=T.gap();iso=sg.IsomorphismGroups(tg)
 assert str(iso)!='fail'
 reps=[C.Representative() for C in sg.ConjugacyClasses()]
 tr=[matrix(K,e.sage()).trace() for e in reps]
 mapped=[iso.Image(e) for e in reps]
 valid=None;examined=0
 for autom in tg.AutomorphismGroup().Elements():
  examined+=1
  if all(matrix(K,autom.Image(e).sage()).trace()==c for e,c in zip(mapped,tr)):
   valid=autom;break
 assert valid is not None
 images=[matrix(K,valid.Image(iso.Image(g)).sage()) for g in sg.GeneratorsOfGroup()]
 equations=[]
 for A,B in zip(sgens,images):
  for i,j in product(range(4),repeat=2):
   row=[K.zero()]*16
   for k in range(4):row[4*k+j]+=A[i,k];row[4*i+k]-=B[k,j]
   equations.append(row)
 base=matrix(K,equations).right_kernel().basis()
 P=None
 for co in product(range(5),repeat=len(base)):
  q=matrix(K,4,4,sum((a*b for a,b in zip(co,base)),vector(K,[0]*16)))
  if q.det():P=q;break
 assert P is not None
 assert all(A*P==P*B for A,B in zip(sgens,images))
 assert all(P.inverse()*g*P in T for g in sgens)
 assert S.order()==T.order()
 return dict(group_order=int(S.order()),source_generators=[data(A) for A in sgens],target_generators=[data(A) for A in tgens],images_of_source_generators=[data(A) for A in images],intertwiner_source_P_equals_P_target=data(P),intertwiner_determinant=str(P.det()),character_class_count=len(reps),automorphisms_examined=examined,all_intertwining_identities_zero=True,equal_generated_groups_after_conjugation=True)
records=[]
for name,(sgens,ids) in models.items():
 for idx in ids:
  t=time.time();print('START',name,idx,flush=True)
  b=binding(sgens,[matrix(K,g) for g in raw[idx-1]])
  b.update(family=name,index=idx,seconds=float(time.time()-t));records.append(b)
  (H/'representation_bindings_partial.json').write_text(json.dumps(records,indent=2)+'\n')
  print('PASS',name,idx,flush=True)
# H's actual rational block is a faithful real reflection representation.
gens=[matrix(QQ,g) for g in raw[153]];G=MatrixGroup(gens)
assert all(g[0,j]==0 and g[j,0]==0 for g in gens for j in range(1,4))
U=[g[1:,1:] for g in gens];W=MatrixGroup(U)
assert all(g[0,0]==g[1:,1:].det() for g in gens)
refs=[g.matrix() for g in W if (g.matrix()-1).rank()==1]
assert MatrixGroup(refs).order()==W.order()==G.order()==48
hrec=dict(actual_index=154,block_decomposition='det(U) direct_sum U',real_rational_matrices=True,faithful_U=True,order=48,reflection_count=len(refs),reflections_generate_full_W=True,U_generators=[data(A) for A in U])
rec=dict(result='ACTUAL_REPRESENTATION_BINDINGS_I_H_D_POSITIVE_PASS',field='Q(zeta12)',input_sha256=hashlib.sha256(rawpath.read_bytes()).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),bindings=records,H_prerequisites=hrec)
(H/'representation_bindings_certificate.json').write_text(json.dumps(rec,indent=2)+'\n')
print(rec['result'],flush=True)
