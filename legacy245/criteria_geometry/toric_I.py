"""Exact smooth coherent equivariant fan and fixed-stratum checks for criterion I."""
from sage.all import *
from itertools import combinations
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent
rays=[vector(QQ,v) for v in identity_matrix(QQ,4).rows()]
for i,j in combinations(range(4),2):rays.append((rays[i]+rays[j])/2)
# 1-based e1..e4,p12,p13,p14,p23,p24,p34
maxcones=[[1,5,6,7],[2,5,8,9],[3,6,8,10],[4,7,9,10],[6,9,5,7],[6,9,7,10],[6,9,10,8],[6,9,8,5]]
maxcones=[tuple(sorted(i-1 for i in c)) for c in maxcones]
height=[0]*4+[-10,-11,-10,-10,-11,-10]
T=matrix(QQ,[[0,1,0,0],[1,0,0,0],[0,0,0,1],[0,0,1,0]])
perm=[rays.index(T*r) for r in rays]
cert=[]
for c in maxcones:
 B=matrix(QQ,[rays[i] for i in c]).transpose()
 assert abs(B.det())==QQ(1)/8
 m=B.transpose().solve_right(vector(QQ,[height[i] for i in c]))
 slacks=[QQ(height[j])-m*rays[j] for j in range(10)]
 assert all(slacks[j]>0 for j in range(10) if j not in c),slacks
 assert tuple(sorted(perm[i] for i in c)) in maxcones
 cert.append(dict(rays=[i+1 for i in c],determinant=str(B.det()),supporting_linear_form=list(map(str,m)),strict_height_slacks=list(map(str,slacks))))
# Exact pairwise simplex intersections, not merely summed volume.
P=[Polyhedron(vertices=[rays[i] for i in c],base_ring=QQ) for c in maxcones]
for i in range(8):
 for j in range(i):
  common=sorted(set(maxcones[i])&set(maxcones[j]))
  assert P[i].intersection(P[j])==Polyhedron(vertices=[rays[k] for k in common],base_ring=QQ)
assert sum(abs(matrix(QQ,[rays[i] for i in c]).det()) for c in maxcones)==1
faces={tuple()}
for c in maxcones:
 for k in range(1,5):faces.update(combinations(c,k))
stable=[]
for f in sorted(faces,key=lambda f:(len(f),f)):
 if tuple(sorted(perm[i] for i in f))!=f:continue
 moved=[i for i in f if perm[i]!=i]
 if moved:
  reason='permuted pair of ray-normal lines gives one +1 tangent eigenvalue at every fixed point'
 else:
  assert len(f)<=1
  reason='orbit tangent has +1-eigenspace of dimension at least 2-dim(cone) >=1'
 stable.append(dict(rays=[i+1 for i in f],positive_tangent_reason=reason))
# Relabeling coordinates 2 and3 sends the good triangulation to the bad
# diagonal p12--p34. Its coherence, smoothness, and tau-invariance are checked.
R=matrix(QQ,[[1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]])
rperm=[rays.index(R*r) for r in rays]
badcones=[tuple(sorted(rperm[i] for i in c)) for c in maxcones]
badheight=[0]*10
for i in range(10):badheight[rperm[i]]=height[i]
for c in badcones:
 B=matrix(QQ,[rays[i] for i in c]).transpose()
 assert abs(B.det())==QQ(1)/8
 m=B.transpose().solve_right(vector(QQ,[badheight[i] for i in c]))
 assert all(badheight[j]-m*rays[j]>0 for j in range(10) if j not in c)
 assert tuple(sorted(perm[i] for i in c)) in badcones

# Bad alternative: diagonal p12--p34 yields two isolated fixed points.
B=matrix(QQ,[rays[i] for i in [4,9,5,6]]).transpose()
A=B.inverse()*T*B
assert A==matrix(QQ,[[1,0,1,1],[0,1,1,1],[0,0,-1,0],[0,0,0,-1]])
x=PolynomialRing(QQ,['a','b','c','d']).gens()
R0=x[0].parent(); FF=R0.fraction_field(); aa,bb,cc,dd=map(FF,x)
action=[aa*cc*dd,bb*cc*dd,1/cc,1/dd]
for point in [[0,0,1,-1],[0,0,-1,1]]:
 assert [f(*point) for f in action]==point
 assert matrix(QQ,[[f.derivative(y)(*point) for y in x] for f in action])==-identity_matrix(QQ,4)
rec=dict(result='FULL_COHERENT_UNIMODULAR_EQUIVARIANT_FAN_AND_NO_ISOLATED_FIXED_POINTS_PASS',rays=[list(map(str,r)) for r in rays],lattice='N=Z^4+sum_{i<j} Z*(e_i+e_j)/2; index [N:Z^4]=8',lattice_index=8,heights=height,maximal_cones=cert,all_pairwise_simplex_intersections_exact=True,normalized_volume_sum=8,fan_support_is_standard_simplex=True,permutation=[i+1 for i in perm],invariant_cones=stable,bad_alternative=dict(heights=badheight,maximal_cones=[[i+1 for i in c] for c in badcones],coherent_smooth_and_tau_invariant=True,chart_basis_ray_indices=[5,10,6,7],lattice_action=[[int(x) for x in row] for row in A.rows()],action='(u1,u2,u3,u4)->(u1*u3*u4,u2*u3*u4,1/u3,1/u4)',isolated_fixed_points=[[0,0,1,-1],[0,0,-1,1]],tangent_action='-I4'),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
(H/'toric_I_certificate.json').write_text(json.dumps(rec,indent=2)+'\n')
print(rec['result'],len(stable),'stable cones',flush=True)
