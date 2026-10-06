"""Exact homogeneous polynomial images using injective Kronecker encoding.

For an image homogeneous of degree d in s variables, setting the last
variable to one is injective on that homogeneous component. Encode the other
variables by T, T^(d+1), ..., T^((d+1)^(s-2)). Every remaining exponent is
at most d, so mixed-radix uniqueness proves injectivity on that component.
All arithmetic below is in QQ[T]; no numerical evaluation or modular test
is used. Kernel completeness remains a separate premise of the caller.
"""
def verify_zero_images(polynomials,images,emit=lambda *a,**k:None):
    from sage.all import QQ,PolynomialRing,prod
    polynomials=list(polynomials);images=list(images)
    assert polynomials and images,'Nonempty typed inputs are required'
    U=polynomials[0].parent();X=images[0].parent()
    assert U.ngens()==len(images) and X.ngens()>=2
    assert all(f.parent() is U for f in polynomials)
    assert all(f.parent() is X for f in images)
    for R in [U,X]:
        K=R.base_ring()
        assert K.is_field() and K.is_exact() and K.characteristic()==0
    assert all(c in QQ for f in polynomials+images for c in f.coefficients()),'Rational coefficients are required'
    assert all(f and f.is_homogeneous() for f in images),'Every image must be nonzero and homogeneous'
    def exponents(e):return tuple(e) if hasattr(e,'__iter__') else (int(e),)
    forms=[{exponents(e):QQ(c) for e,c in f.dict().items()} for f in images]
    degrees=[int(f.total_degree()) for f in images]
    inputs=[{exponents(e):QQ(c) for e,c in f.dict().items()} for f in polynomials]
    weighted_degrees=[]
    for f in inputs:
        ds={sum(e[j]*degrees[j] for j in range(len(images))) for e in f}
        assert len(ds)<=1,'Kronecker dehomogenization requires a homogeneous image degree'
        weighted_degrees.append(next(iter(ds),0))
    R=PolynomialRing(QQ,'kronecker_variable')
    emit('EXACT_KRONECKER_IMAGES_START',count=len(inputs),characteristic=0,physical_variables=X.ngens(),maximum_homogeneous_degree=max(weighted_degrees))
    for index,(f,d) in enumerate(zip(inputs,weighted_degrees),1):
        if not f:
            emit('EXACT_KRONECKER_IMAGE_ZERO',index=index,homogeneous_degree=d,zero_input=True)
            continue
        base=int(d)+1
        radices=[base**j for j in range(X.ngens()-1)]
        maxima=[max(e[j] for e in f) for j in range(len(images))]
        powers=[]
        for j,form in enumerate(forms):
            values=[R(1)]
            if maxima[j]:
                assert degrees[j]<=d
                assert all(all(e[k]<=d for k in range(X.ngens()-1)) for e in form)
                # All exponents of the omitted variable are determined by
                # the fixed degree of this homogeneous generator. Check the
                # encoded support is injective even before multiplying.
                coded={sum(e[k]*radices[k] for k in range(X.ngens()-1)):c for e,c in form.items()}
                assert len(coded)==len(form),'A generator support collided under Kronecker encoding'
                q=R(coded)
                for k in range(1,int(maxima[j])+1):values.append(values[-1]*q)
            powers.append(values)
        result=R(0)
        for e,c in f.items():
            factors=[powers[j][int(e[j])] for j in range(len(images)) if e[j]]
            factors.sort(key=lambda q:q.degree())
            result+=c*prod(factors)
        assert result==0, f'Nonzero exact physical image at input {index}'
        emit('EXACT_KRONECKER_IMAGE_ZERO',index=index,homogeneous_degree=d,radix=base,univariate_degree_bound=int(d)*radices[-1])
    emit('EXACT_KRONECKER_IMAGES_COMPLETE',count=len(inputs),characteristic=0)
    return {'all_zero':True,'checked':len(inputs),'characteristic':0,'coefficient_field':'QQ','method':'injective homogeneous Kronecker encoding in QQ[T]'}
