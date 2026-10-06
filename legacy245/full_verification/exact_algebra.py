"""Exact field descent for polynomial ideal computations.

If every monic input has rational coefficients, the ideal is obtained from
its rational ideal by a faithfully flat field extension. Groebner bases and
finite intersections commute with that extension. This is an optimization,
not a reduction modulo a prime and not a completeness assumption.
"""
from sage.all import QQ,PolynomialRing,NumberField,gcd

def power_subfield_models(ideals):
    """Descend exactly when coefficients use a proper power of the field root.

    This is a characteristic-zero field embedding, never a modular test.
    Every translated coefficient is checked under the explicit embedding.
    The common model is needed for ideal intersections.
    """
    R=ideals[0].ring();K=R.base_ring()
    assert all(I.ring() is R for I in ideals)
    if K is QQ or K.characteristic()!=0 or K.degree()<=1:return None
    normalized=[[f/f.leading_coefficient() for f in I.gens() if f] for I in ideals]
    coefficients=[c for fs in normalized for f in fs for c in f.coefficients()]
    representations=[c.polynomial().dict() for c in coefficients]
    if not all(a in QQ for d in representations for a in d.values()):return None
    exponents=[int(e) for d in representations for e,a in d.items() if e and a]
    if not exponents:return None
    power=int(gcd(exponents))
    if power<=1:return None
    alpha=K.gen()**power;minimal=alpha.minpoly()
    if minimal.degree()>=K.degree():return None
    L=NumberField(minimal,'descent_root');embedding=L.hom([alpha],K)
    def descend(c):
        value=L(0)
        for e,a in c.polynomial().dict().items():
            assert int(e)%power==0
            value+=QQ(a)*L.gen()**(int(e)//power)
        assert embedding(value)==c,'Incorrect coefficient-field descent'
        return value
    S=PolynomialRing(L,R.variable_names(),order=R.term_order())
    models=[S.ideal([S({tuple(e):descend(c) for e,c in f.dict().items()}) for f in fs]) for fs in normalized]
    return models,embedding

def rational_model(ideal):
    R=ideal.ring()
    inputs=[f/f.leading_coefficient() for f in ideal.gens() if f]
    if R.base_ring()==QQ:return R.ideal(inputs)
    if not all(c in QQ for f in inputs for c in f.coefficients()):return None
    Q=PolynomialRing(QQ,R.variable_names(),order=R.term_order())
    return Q.ideal([Q({tuple(e):QQ(c) for e,c in f.dict().items()}) for f in inputs])

def lift_polynomial(f,R):
    return R({tuple(e):c for e,c in f.dict().items()})

def groebner_basis(ideal):
    rational=rational_model(ideal)
    if rational is None:return ideal.groebner_basis()
    basis=rational.groebner_basis()
    return [lift_polynomial(f,ideal.ring()) for f in basis]

def saturation_basis(ideal,variable,emit=None,keep_rational=False):
    """Standard basis of I <= J <= I:(product of specified variables)^infty.

    Singular's satstd performs Buchberger operations and may divide by the
    specified variable during the computation.  It does NOT by itself claim
    complete saturation for an arbitrary weighted order.  Callers obtain the
    full saturation by the homogeneous Bayer last-variable stripping step.
    We also check I <= J by reducing every original input by the returned
    standard basis.  Rational descent is a faithfully flat field extension.
    """
    from sage.libs.singular.function import lib
    from sage.libs.singular.function_factory import singular_function
    rational=rational_model(ideal)
    source=ideal if rational is None else rational
    R=source.ring()
    variables=list(variable) if isinstance(variable,(tuple,list)) else [variable]
    positions=[list(ideal.ring().gens()).index(v) for v in variables]
    lib('customstd.lib')
    basis=list(singular_function('satstd')(source,R.ideal([R.gen(q) for q in positions])))
    if emit:emit('PARTIAL_SATURATION_STANDARD_BASIS_COMPLETE',generators=len(basis))
    assert all(f.reduce(basis)==0 for f in source.gens()),'satstd lost an input relation'
    if emit:emit('PARTIAL_SATURATION_INPUT_INCLUSION_VERIFIED',generators=len(source.gens()))
    # Bayer callers consume coefficient dictionaries and lift only once,
    # after stripping; avoid an unnecessary intermediate number-field copy.
    if keep_rational and rational is not None:return basis
    return [lift_polynomial(f,ideal.ring()) for f in basis]

def saturation(ideal,variable):
    """Complete ideal saturation, with exact rational field descent."""
    rational=rational_model(ideal)
    source=ideal if rational is None else rational
    position=list(ideal.ring().gens()).index(variable)
    result=source.saturation(source.ring().ideal(source.ring().gen(position)))[0]
    return ideal.ring().ideal([lift_polynomial(f,ideal.ring()) for f in result.gens()])

def intersection(first,second):
    qfirst=rational_model(first);qsecond=rational_model(second)
    if qfirst is None or qsecond is None:
        descended=power_subfield_models([first,second])
        if descended is None:return first.intersection(second)
        models,embedding=descended
        result=models[0].intersection(models[1]);R=first.ring()
        return R.ideal([R({tuple(e):embedding(c) for e,c in f.dict().items()}) for f in result.gens()])
    result=qfirst.intersection(qsecond)
    return first.ring().ideal([lift_polynomial(f,first.ring()) for f in result.gens()])
