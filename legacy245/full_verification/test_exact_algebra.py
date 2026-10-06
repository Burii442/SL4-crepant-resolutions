"""Small independent checks of saturation and rational-character recovery.

Run with sage -python full_verification/test_exact_algebra.py.
"""
from sage.all import *
from exact_algebra import saturation_basis,saturation,intersection,power_subfield_models
from rational_tags import recovered_tag_kernel
from finite_ordinary_graph import tagged_kernel

def equal_ideals(I,J):
    a=list(I.groebner_basis());b=list(J.groebner_basis())
    assert all(f.reduce(b)==0 for f in I.gens())
    assert all(f.reduce(a)==0 for f in J.gens())

K=CyclotomicField(8)
R=PolynomialRing(K,['x','y','t'],order=TermOrder('wdegrevlex',[2,3,1]))
x,y,t=R.gens();I=R.ideal([t*t*(y*y-x*x*x),t*t*t*x*y])
B=saturation_basis(I,t,keep_rational=True)
assert B[0].parent().base_ring()==QQ
stripped=[]
for f in B:
    low=min(e[2] for e in f.exponents())
    stripped.append(R({(e[0],e[1],e[2]-low):c for e,c in f.dict().items()}))
equal_ideals(R.ideal(stripped),saturation(I,t))
X=PolynomialRing(QQ,['x','y']);x,y=X.gens()
U=PolynomialRing(QQ,['u1','u2','u3','u4'],order='degrevlex');u=U.gens()
ordinary=U.ideal([u[1]-u[0],u[3]-u[2]])
forms=[x,x,y,y];tags=[[0,1,0,0],[0,0,0,1]]
result=recovered_tag_kernel(ordinary,forms,U,tags,[3,3],[(1,0),(3,2)],[1]*4,lambda *a,**k:None)
equal_ideals(result,U.ideal([u[1]**3-u[0]**3,u[3]**3-u[2]**3]))
# A fifth power exercises reduction of recovered-character exponents
# modulo three. Compare with the entire independently eliminated tagged
# graph, including the finite parameter equation.
V=PolynomialRing(QQ,['v1','v2','v3'],order=TermOrder('wdegrevlex',[1,1,5]));v=V.gens()
ordinary5=V.ideal([v[1]-v[0],v[2]-v[1]**5])
result5=recovered_tag_kernel(ordinary5,[x,x,x**5],V,[[0,1,2]],[3],[(1,0)],[1,1,5],lambda *a,**k:None)
G=PolynomialRing(QQ,['x','c','v1','v2','v3'],order='lex');gx,gc,g1,g2,g3=G.gens()
full5=G.ideal([gc**3-1,g1-gx,g2-gx*gc,g3-gx**5*gc**2]).elimination_ideal([gx,gc])
equal_ideals(result5,V.ideal([V(str(f)) for f in full5.gens()]))
equal_ideals(tagged_kernel(ordinary5,[[0,1,2]],[3]),V.ideal([V(str(f)) for f in full5.gens()]))
equal_ideals(tagged_kernel(ordinary,tags,[3,3]),result)
for invalid_tags,invalid_orders in [([[0,1,QQ(1)/2]],[3]),([[0,1,2]],[QQ(3)/2])]:
    try:tagged_kernel(ordinary5,invalid_tags,invalid_orders)
    except AssertionError:pass
    else:raise AssertionError('Nonintegral finite grading was silently accepted')
for invalid_field in [ZZ,RDF,GF(101)]:
    invalid_ring=PolynomialRing(invalid_field,['z1','z2'])
    try:tagged_kernel(invalid_ring.ideal(invalid_ring.gen(0)-invalid_ring.gen(1)),[[0,1]],[2])
    except AssertionError:pass
    else:raise AssertionError('Unsupported coefficient field was accepted')
K24=CyclotomicField(24);eta=K24.gen()**4
T=PolynomialRing(K24,['a','b'],order='degrevlex');a,b=T.gens()
left=T.ideal(a+eta*b);right=T.ideal(a-eta*b)
descent=power_subfield_models([left,right]);assert descent is not None
assert descent[0][0].ring().base_ring().degree()==2
equal_ideals(intersection(left,right),left.intersection(right))
equal_ideals(intersection(left,right),T.ideal(a*a-eta*eta*b*b))
assert power_subfield_models([T.ideal(a+(K24.gen()+eta)*b),right]) is None
for bad_forms,bad_pairs in [([x,y,y,y],[(1,0),(3,2)]),(forms,[(1,0),(1,0)]),([X(0),X(0),y,y],[(1,0),(3,2)])]:
    try:recovered_tag_kernel(ordinary,bad_forms,U,tags,[3,3],bad_pairs,[1]*4,lambda *a,**k:None)
    except AssertionError:pass
    else:raise AssertionError('Invalid character-recovery hypothesis was accepted')
print('EXACT_ALGEBRA_SATURATION_AND_CHARACTER_RECOVERY_PASS')
