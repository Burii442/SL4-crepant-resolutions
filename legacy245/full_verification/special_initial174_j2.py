"""Complete unsigned second initial kernel of case 174.

Five literal forms have a primitive quadratic relation of rank three over
QQ(u1,u2). A nonzero physical Jacobian of size four proves image dimension
four. The quadric is geometrically irreducible, so it is the entire kernel
on those five forms. Twenty freshly checked polynomial graphs restore all
25 variables, with no localization required. The graph for u4 is NOT finite
character homogeneous. The caller must subsequently compute the full finite
character intersection; this function proves only the unsigned kernel.
"""
from pathlib import Path
import json


def compute_initial_kernel(forms, U, emit=lambda *a,**k:None):
    from sage.all import QQ,PolynomialRing,matrix,gcd
    data=json.loads(Path(__file__).with_name('174_initial2_polynomial_graphs.json').read_text())
    assert data['case']==174 and data['junior']==2
    assert len(forms)==U.ngens()==25 and list(U.variable_names())==['u'+str(j) for j in range(1,26)]
    X=forms[0].parent();K=U.base_ring()
    assert X.ngens()==4 and all(f.parent() is X for f in forms)
    assert K.is_field() and K.is_exact() and K.characteristic()==0
    assert X.base_ring()==K
    assert all(f and len({sum(e) for e in f.dict()})==1 for f in forms)
    degrees=[f.total_degree() for f in forms]
    core=data['core_indices'];assert core==[1,2,5,6,7]
    C=PolynomialRing(QQ,['u'+str(j) for j in core]);u1,u2,u5,u6,u7=C.gens()
    relation=C(data['core_quadric']);assert relation
    core_map=C.hom([forms[j-1] for j in core],X)
    assert core_map(relation)==0, 'The complete-core candidate does not vanish on the literal forms'
    qvars=[u5,u6,u7]
    quadratic=matrix(C,[[relation.derivative(v).derivative(w)/2 for w in qvars] for v in qvars])
    assert relation==sum(quadratic[i,j]*qvars[i]*qvars[j] for i in range(3) for j in range(3))
    assert all(set(c.variables()).issubset({u1,u2}) for c in quadratic.list())
    assert quadratic.det()!=0 and gcd(quadratic.list())==1, 'Primitive rank-three quadric is required'
    jacobian=matrix(K,[[forms[j-1].derivative(v)(1,2,3,5) for v in X.gens()] for j in [1,2,6,7]])
    assert jacobian.det()!=0, 'Four independent literal physical forms are required'
    lift=C.hom([U.gen(j-1) for j in core],U);physical=U.hom(forms,X)
    relations=[lift(relation)];seen=[]
    for row in data['recoveries']:
        j=row['index'];assert j not in core and j not in seen and 1<=j<=25
        polynomial=C(row['polynomial']);f=U.gen(j-1)-lift(polynomial)
        assert physical(f)==0, ('Polynomial recovery does not hold',j)
        relations.append(f);seen.append(j)
    assert sorted(seen)==[j for j in range(1,26) if j not in core]
    assert all(len({sum(e[j]*degrees[j] for j in range(25)) for e in f.dict()})==1 for f in relations)
    # Record the exact finite-grading boundary. The caller's normal character
    # intersection remains essential and is deliberately not bypassed here.
    assert data['finite_orders']==[2]
    tags=data['finite_degree_matrix'];assert tags==[[int(j in [4,5]) for j in range(1,26)]]
    homogeneous=[len({sum(int(e[j])*tags[0][j] for j in range(25))%2 for e in f.dict()})==1 for f in relations]
    assert homogeneous[0] is True
    assert [seen[k-1] for k,value in enumerate(homogeneous) if not value]==[4]
    emit('174_INITIAL2_FULL_UNSIGNED_QUADRATIC_GRAPH_KERNEL',
         core_indices=core,primitive_quadric_rank=3,physical_jacobian_rank=4,
         polynomial_graphs=len(seen),complete_unsigned_generators=len(relations),
         finite_character_homogeneous_relations=sum(homogeneous),
         finite_character_nonhomogeneous_graphs=[4],requires_full_character_intersection=True)
    return U.ideal(relations)
