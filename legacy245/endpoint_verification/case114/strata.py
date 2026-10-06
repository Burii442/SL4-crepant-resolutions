"""Exact full ambient Jacobians and finite point decompositions for Case 114."""
from sage.all import PolynomialRing,matrix,prod

def point_values_and_jacobian(polynomials,point):
    K=polynomials[0].base_ring();n=len(point)
    largest=max(max(e) for f in polynomials for e in f.exponents())
    powers=[[K(1)]+[x**k for k in range(1,largest+1)] for x in point]
    values=[];rows=[]
    for f in polynomials:
        value=K(0);row=[K(0)]*n
        for exponent,coefficient in f.dict().items():
            value+=coefficient*prod(powers[j][int(exponent[j])] for j in range(n))
            for j in range(n):
                if not exponent[j]:continue
                row[j]+=coefficient*exponent[j]*prod(powers[k][int(exponent[k])-(k==j)] for k in range(n))
        values.append(value);rows.append(row)
    return values,matrix(K,rows)

def finite_stratum(polynomials,support,gauge,required_rank):
    """Prove the ENTIRE localized stratum is a reduced union of smooth points."""
    K=polynomials[0].base_ring();n=polynomials[0].parent().ngens()
    free=[j for j in support if j not in gauge]
    R=PolynomialRing(K,[f'z{j+1}' for j in free]+['inv']);xs=R.gens()
    off=set(range(n))-set(support)
    def specialize(f):
        terms={}
        for e,c in f.dict().items():
            if any(e[j] for j in off):continue
            exponent=tuple(e[j] for j in free)+(0,)
            terms[exponent]=terms.get(exponent,K(0))+c
        return R(terms)
    I=R.ideal([specialize(f) for f in polynomials]+[xs[-1]*prod(xs[:-1])-1])
    if I.is_one():return {'status':'EMPTY','method':'exact localized unit ideal'}
    assert I.dimension()==0,'Residual stratum is not finite'
    points=I.variety(ring=K);assert points,'No complete rational point decomposition'
    union=R.ideal(1);records=[]
    for point in points:
        union=union.intersection(R.ideal([x-point[x] for x in xs]))
        full_point=[K(0)]*n
        for j in gauge:full_point[j]=K(1)
        for j,x in zip(free,xs):full_point[j]=point[x]
        assert all(full_point[j]!=0 for j in support),'Point escaped its exact support'
        values,J=point_values_and_jacobian(polynomials,full_point)
        assert not any(values),'Point fails full ambient equations'
        rank=J.rank();assert rank==required_rank,'Full ambient Jacobian rank'
        records.append({'coordinates':list(map(str,full_point)),'full_ambient_jacobian_rank':int(rank)})
    assert I==union,'Finite stratum is not the entire reduced point union'
    return {'status':'SMOOTH','method':'complete reduced point union and full ambient Jacobians',
            'points':records,'stratum_groebner_basis':list(map(str,I.groebner_basis()))}
