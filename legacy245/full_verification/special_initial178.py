"""Complete tagged first initial kernel for case 178, from literal maps."""
from sage.all import *
from rational_tags import recovered_tag_kernel
from exact_algebra import saturation_basis

def compute_tagged_kernel(forms,U,tags,orders,degrees,emit):
    K=U.base_ring();X=forms[0].parent();u=list(U.gens());n=len(u)
    assert n==18
    A=PolynomialRing(K,[str(v) for v in u[:10]],order=TermOrder('wdegrevlex',degrees[:10]))
    v=list(A.gens());a,b=v[0],v[3];p,q,r=v[6:9]
    relations=[4*a*b+v[1],-a*a+v[2]+4*b,-b+v[4],-v[2]+v[5],p+16*q+16*r+v[9]]
    quadratic=64*a*a*q*q+64*a*a*q*r+64*a*a*r*r+b*p*p+16*b*p*q+16*b*p*r+256*b*q*r
    relations.append(quadratic)
    evaluate=A.hom(forms[:10],X)
    assert all(evaluate(f)==0 for f in relations)
    # Five monic graph equations leave a ternary quadratic over K[a,b].
    # A rank-three quadratic is geometrically irreducible. Primitivity and
    # Gauss's lemma give a prime hypersurface in K[a,b,p,q,r].
    matrix_q=matrix(A,[[b,8*b,8*b],[8*b,64*a*a,32*a*a+128*b],[8*b,32*a*a+128*b,64*a*a]])
    assert matrix_q.det()!=0
    assert gcd(matrix_q.list())==1
    witness=None
    jac=matrix(X,[[forms[j].derivative(x) for x in X.gens()] for j in [0,3,6,7]])
    for point in [(1,2,3,5),(2,3,5,7)]:
        if matrix(K,[[f(*point) for f in row] for row in jac.rows()]).det()!=0:witness=list(point);break
    assert witness is not None
    emit('INITIAL178_PRIME_QUADRATIC_FULL_ORDINARY_KERNEL',jacobian_witness=witness,ordinary_relations=6)
    tagged=recovered_tag_kernel(A.ideal(relations),forms[:10],A,[row[:10] for row in tags],orders,[(5,2),(4,3)],degrees[:10],emit)
    lift=A.hom(u[:10],U)
    numerators=[u[3]*u[7]-u[4]*u[8],-u[2]*u[6]+u[5]*u[9],u[4]*u[6]-4*u[5]*u[7],u[3]*u[6]-4*u[5]*u[8],-4*u[2]*u[7]+u[4]*u[9],-4*u[2]*u[8]+u[3]*u[9],2*u[2]*u[6]-128*u[3]*u[7]-256*u[4]*u[8]+4*u[5]*u[9],-6*u[7]*u[8]+QQ(3)/128*u[6]*u[9]]
    extensions=[u[0]*u[j]-numerators[j-10] for j in range(10,18)]
    evaluation=U.hom(forms,X)
    assert forms[0]!=0 and all(evaluation(f)==0 for f in extensions)
    for f in extensions:
        assert len({tuple(sum(e[j]*tags[k][j] for j in range(n))%orders[k] for k in range(len(tags))) for e in f.exponents()})==1
    # Each extra generator is a proved graph after inverting u1, which is
    # nonzero in every finite character component. Saturation contracts it.
    I=U.ideal([lift(f) for f in tagged.gens()]+extensions)
    ids=list(range(1,n))+[0]
    R=PolynomialRing(K,[str(u[j]) for j in ids],order=TermOrder('wdegrevlex',[degrees[j] for j in ids]))
    incoming=[R({tuple(e[j] for j in ids):c for e,c in f.dict().items()}) for f in I.gens()]
    emit('INITIAL178_LOCALIZED_GRAPH_CONTRACTION_START',inputs=len(incoming))
    gb=saturation_basis(R.ideal(incoming),R.gen(n-1),emit,keep_rational=True)
    result=[];inverse=[ids.index(j) for j in range(n)]
    for f in gb:
        low=min(e[n-1] for e in f.exponents())
        assert f.leading_monomial().exponents()[0][n-1]==low
        result.append(U({tuple(e[inverse[j]]-(low if j==0 else 0) for j in range(n)):c for e,c in f.dict().items()}))
    emit('INITIAL178_COMPLETE_TAGGED_KERNEL',generators=len(result))
    return U.ideal(result)
