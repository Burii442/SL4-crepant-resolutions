"""Small exact characteristic-zero kernel certificates for difficult graphs."""

def base178(forms,U,relations,degrees,emit=lambda *args,**kw:None):
    """A complete-intersection domain certificate for the six-generator core.

    Localizing u1 solves the first relation linearly for u2. The resulting
    cubic in u4 has unit leading coefficient over K[u1^+-1,u3,u5,u6] and an
    irreducible rational specialization. Its degree is coprime to [K:Q], so
    it remains irreducible over K. The u1=0 section has codimension one in
    the complete intersection, proving u1 is a nonzerodivisor. Therefore
    the entire core quotient is a domain of dimension four.
    """
    from sage.all import QQ,PolynomialRing,matrix,gcd,prod
    X=forms[0].parent();K=X.base_ring();n=U.ngens();u=list(U.gens())
    assert n==18
    R=PolynomialRing(QQ,[f'v{i+1}' for i in range(6)]);v=list(R.gens())
    core=[]
    for rel in relations[:2]:
        assert all(all(e[j]==0 for j in range(6,n)) for e in rel.dict())
        core.append(R({tuple(e)[:6]:QQ(c) for e,c in rel.dict().items()}))
    f,q=core;s=v[0];y=v[1]
    coefficient=f.coefficient({y:1});assert coefficient==2*s
    constant=f-coefficient*y;assert constant.degree(y)==0
    assert gcd(coefficient,constant).is_unit()
    # After u1=0, the first relation is the irreducible 2x2 determinant.
    f0=f.subs({s:0});q0=q.subs({s:0})
    assert f0==16*v[3]*v[4]-v[2]*v[5]
    assert q0.coefficient({y:2})!=0 and q0.degree(y)==2
    assert gcd(f0,q0).is_unit()
    localized=q.subs({y:-constant/coefficient})
    cubic=R(localized*coefficient**2)
    assert cubic.degree(v[3])==3
    leading=cubic.coefficient({v[3]:3});assert leading!=0
    assert len(leading.dict())==1
    lead_exp=next(iter(leading.dict()));assert all(lead_exp[k]==0 for k in range(1,6))
    # All potential monic factors have Laurent-polynomial coefficients.
    # Specialization u1=1 cannot lower their degree in v4.
    Z=PolynomialRing(QQ,'z');z=Z.gen();witness=None
    for a in range(4):
      for b in range(4):
       for c in range(4):
        specialized=R.hom([Z(1),Z(0),Z(a),z,Z(b),Z(c)],Z)(cubic)
        if specialized.degree()==3 and specialized.is_irreducible():
            witness=[1,a,b,c];break
       if witness:break
      if witness:break
    assert witness is not None
    field_degree=1 if K is QQ else K.degree();assert gcd(3,field_degree)==1
    phi=U.hom(forms,X)
    for j,rel in enumerate(relations[:2],1):
        assert phi(rel)==0
        emit('CORE178_DEFINING_IDENTITY_ZERO',relation=j)
    jac=matrix(X,[[forms[j].derivative(x) for x in X.gens()] for j in range(6)])
    point=[1,2,3,5];numeric=matrix(K,[[f(*point) for f in row] for row in jac.rows()])
    assert numeric.rank()==4
    extensions=[]
    for j in range(6,n):
        candidates=[]
        for rel in relations:
            c=rel.monomial_coefficient(u[j]);
            if not c:continue
            rest=rel-c*u[j]
            if all(all(e[k]==0 for k in range(j,n)) for e in rest.dict()):candidates.append(rel/c)
        assert candidates,('No exact triangular definition supplied for generator',j+1)
        chosen=min(candidates,key=lambda f:len(f.dict()))
        assert phi(chosen)==0
        assert len({sum(e[k]*degrees[k] for k in range(n)) for e in chosen.dict()})==1
        extensions.append(chosen)
    emit('CORE178_FULL_KERNEL_PROVED',irreducible_cubic_specialization=witness,jacobian_point=point,triangular_extensions=len(extensions))
    T=PolynomialRing(QQ,'t');t=T.gen()
    hilbert=(1-t**8)*(1-t**12)/prod(1-t**d for d in degrees[:6])
    return U.ideal(relations[:2]+extensions),hilbert,dict(method='Localized irreducible cubic plus complete-intersection nonzerodivisor and exact graph extensions',cubic_specialization=witness,jacobian_point=point)

def quadratic_hypersurface(forms,U,hints,core,extensions,emit=lambda *args,**kw:None):
    """Prove a five-generator map kernel by a primitive irreducible quadratic.

    A constant leading coefficient and a nonsquare polynomial discriminant
    imply irreducibility over the other four-variable fraction field. Odd
    multiplicities in a rational polynomial factorization stay odd after any
    characteristic-zero constant-field extension. A nonzero Jacobian minor
    proves image dimension four; hence the prime hypersurface is the kernel.
    Return None when these sufficient conditions do not apply.
    """
    from sage.all import QQ,PolynomialRing,matrix
    if len(core)!=5:return None
    X=forms[0].parent();K=X.base_ring();n=U.ngens();u=list(U.gens())
    Q=PolynomialRing(QQ,[str(u[j]) for j in core])
    candidates=[]
    for f in hints:
        if not f or not all(all(e[j]==0 for j in range(n) if j not in core) for e in f.exponents()):continue
        normalized=f/f.leading_coefficient()
        if not all(c in QQ for c in normalized.coefficients()):continue
        q=Q({tuple(e[j] for j in core):QQ(c) for e,c in normalized.dict().items()})
        for j in range(5):
            if q.degree(Q.gen(j))!=2:continue
            a=q.coefficient({Q.gen(j):2})
            if not a.is_constant() or not a:continue
            b=q.coefficient({Q.gen(j):1});c=q.coefficient({Q.gen(j):0})
            discriminant=b*b-4*a*c
            if not discriminant:continue
            factorization=discriminant.factor()
            if any(exponent%2 and not factor.is_constant() for factor,exponent in factorization):
                candidates.append((len(q.dict()),f,str(factorization),core[j]+1));break
    if not candidates:return None
    _,relation,factorization,quadratic_variable=min(candidates,key=lambda v:v[0])
    assert U.hom(forms,X)(relation)==0,'Proposed hypersurface relation has nonzero image'
    jac=matrix(X,[[forms[j].derivative(x) for x in X.gens()] for j in core])
    witness=None
    for point in [(1,2,3,5),(2,3,5,7),(1,3,7,11)]:
        numerical=matrix(K,[[f(*point) for f in row] for row in jac.rows()])
        if numerical.rank()==4:witness=list(point);break
    assert witness is not None,'Hypersurface image has no verified rank-four Jacobian minor'
    emit('QUADRATIC_HYPERSURFACE_FULL_KERNEL_PROVED',core_indices=[j+1 for j in core],quadratic_variable=quadratic_variable,discriminant_factorization=factorization,jacobian_point=witness)
    return U.ideal([relation]+extensions)
