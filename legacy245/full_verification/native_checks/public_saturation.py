"""Identify a full multihomogenized kernel from the public presentation.

This module accepts an already proved complete ordinary polynomial-map kernel.
It never accepts a saved assertion of kernel completeness. All ideal operations
in this module are performed again on the actual polynomials supplied by caller.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from exact_algebra import groebner_basis,rational_model,lift_polynomial

def public_presentation_fullness(model, base_kernel, U, P, nu, orders,
                                 degrees, saturate_step, emit, cache=None,
                                 ordinary_forms=None, image_work_directory=None):
    """Return the full multihomogenization, or raise an assertion.

    `saturate_step(I,k)` must compute the exact ideal I:t_k^infinity. The
    caller may supply a live cache wrapper for its own newly computed stages.
    All variables and rows retain the order of the public mathematical input.
    """
    from sage.all import PolynomialRing,QQ
    n=U.ngens(); r=len(orders)
    assert P.ngens()==n+r and nu.nrows()==r and nu.ncols()==n
    assert len(degrees)==n
    K=P.base_ring(); ts=list(P.gens()[n:])
    emit('PUBLIC_POLYNOMIAL_PARSING_START',relations=len(model['equations']))
    input_field=QQ if all('zeta' not in s for s in model['equations']) else K
    MP=PolynomialRing(input_field,model['coordinate_order'])
    # This is the literal monomial map e_k -> t_k^r_k. Constructing the
    # coefficient dictionary avoids an unnecessary symbolic substitution.
    public=P.ideal([P({tuple(e[:n])+tuple(int(e[n+k])*orders[k] for k in range(r)):c
                         for e,c in MP(s).dict().items()}) for s in model['equations']])
    emit('PUBLIC_MULTIGRADING_CHECK_START')
    for f in public.gens():
        support=list(f.dict())
        assert len({sum(int(e[j])*degrees[j] for j in range(n)) for e in support})<=1, 'Public relation mixes ordinary degrees'
        for k in range(r):
            assert len({int(e[n+k])-sum(int(nu[k,j])*int(e[j]) for j in range(n)) for e in support})<=1, 'Public relation mixes valuation degrees'
    emit('PUBLIC_MULTIGRADING_CHECK_COMPLETE',relations=len(public.gens()))
    def dehom(f):
        coefficients={}
        for e,c in f.dict().items():
            key=tuple(e[:n]);coefficients[key]=coefficients.get(key,K(0))+c
        return U(coefficients)
    specialized=[dehom(f) for f in public.gens()]
    ordinary_rational=all(c in QQ for f in list(base_kernel.gens())+specialized for c in f.coefficients())
    reduction_ring=PolynomialRing(QQ,U.variable_names(),order=U.term_order()) if ordinary_rational else U
    def ordinary_convert(f):
        return reduction_ring({tuple(e):QQ(c) if ordinary_rational else c for e,c in f.dict().items()})
    reduction_kernel=reduction_ring.ideal([ordinary_convert(f) for f in base_kernel.gens()])
    reduction_specialized=[ordinary_convert(f) for f in specialized]
    emit('PUBLIC_DEHOMOGENIZATION_EQUALITY_START')
    emit('ORDINARY_MEMBERSHIP_COEFFICIENT_FIELD',field=str(reduction_ring.base_ring()))
    emit('FULL_ORDINARY_REDUCTION_BASIS_START')
    full_gb=groebner_basis(reduction_kernel)
    emit('FULL_ORDINARY_REDUCTION_BASIS_COMPLETE',generators=len(full_gb))
    # In case 233 the coordinate images are small binomials, while reduction
    # of the largest public equations in the fourteen-variable quotient is
    # needlessly expensive. The caller has already proved that base_kernel
    # is the complete kernel of this very map; exact substitution therefore
    # checks precisely the same ideal membership, over characteristic zero.
    core_specs={178:(18,12),179:(31,25)}
    case=int(model.get('case',0))
    use_core=case in core_specs
    use_native_images=case in [171,173,177]
    if use_native_images:assert ordinary_forms is not None and len(ordinary_forms)==n, 'Every actual ordinary coordinate image is required'
    use_images=ordinary_forms is not None and int(model.get('case',0))==233
    if use_images:
        assert len(ordinary_forms)==n
        evaluate=U.hom(ordinary_forms,ordinary_forms[0].parent())
        emit('PUBLIC_ORDINARY_RELATIONS_EXACT_IMAGES')
    if use_core:
        from native_checks.triangular_quotient import triangular_quotient_map
        expected_variables,expected_definitions=core_specs[case]
        assert n==expected_variables and ordinary_rational
        core_evaluate,core_metadata=triangular_quotient_map(reduction_kernel,list(range(6)),emit)
        assert core_metadata['monic_definitions']==expected_definitions
        checked=core_evaluate.verify_zero_batch(reduction_specialized,emit)
        assert checked==len(specialized)
        emit('PUBLIC_ORDINARY_RELATIONS_CORE_QUOTIENT_ZERO',count=checked,**core_metadata)
    elif use_native_images:
        image_options={}
        if case==173:
            from native_checks.parallel_kronecker import verify_zero_images
            image_options['workers']=4
            if image_work_directory is not None:
                import tempfile
                evidence_root=Path(image_work_directory).resolve()
                evidence_root.mkdir(parents=True,exist_ok=True)
                # Preserve previous attempts when the main verifier resumes.
                image_options['work_directory']=Path(tempfile.mkdtemp(prefix='run-',dir=evidence_root))
        else:
            from native_checks.exact_images import verify_zero_images
        report=verify_zero_images(specialized,ordinary_forms,emit,**image_options)
        assert report['all_zero'] is True and report['characteristic']==0 and report['checked']==len(specialized)
        emit('PUBLIC_ORDINARY_RELATIONS_NATIVE_EXACT_IMAGES_ZERO',count=report['checked'])
    else:
        for count,(f,reduced_f) in enumerate(zip(specialized,reduction_specialized),1):
            remainder=evaluate(f) if use_images else reduced_f.reduce(full_gb)
            assert remainder==0, 'Public dehomogenization has excess ordinary relations'
            if count%200==0:emit('PUBLIC_ORDINARY_RELATIONS_REDUCED',count=count,total=len(specialized))
    # A homogeneous generator of degree greater than every required ordinary
    # kernel generator cannot contribute to their expressions. Retaining only
    # smaller generators is therefore sufficient for the reverse inclusion.
    # The inclusion already checked still covers ALL public equations.
    def homogeneous_degree(f):
        ds={sum(int(e[j])*degrees[j] for j in range(n)) for e in f.dict()}
        assert len(ds)<=1, 'Ordinary kernel or dehomogenization mixes degrees'
        return next(iter(ds),0)
    maximum=max((homogeneous_degree(f) for f in base_kernel.gens()),default=0)
    reduced_inputs=sorted({f/f.leading_coefficient() for f in reduction_specialized if f and homogeneous_degree(f)<=maximum},key=lambda f:(homogeneous_degree(f),len(f.dict()),str(f)))
    specialization=reduction_ring.ideal(reduced_inputs)
    emit('PUBLIC_DEHOMOGENIZATION_RELEVANT_INPUTS',retained=len(reduced_inputs),original=len(specialized),maximum_required_degree=maximum)
    given_gb=groebner_basis(specialization)
    assert all(f.reduce(given_gb)==0 for f in reduction_kernel.gens()), 'Public dehomogenization misses complete ordinary relations'
    emit('PUBLIC_DEHOMOGENIZATION_EQUALS_FULL_KERNEL')
    if case==179:
        from native_checks.hilbert_regularity import verify_parameter_saturations
        saturation_report=verify_parameter_saturations(public,nu,orders,degrees,emit,
            variable_order=list(range(1,n))+[0]+list(range(n+1,n+r))+[n])
        assert saturation_report['status']=='PASS' and saturation_report['all_parameter_saturations_equal'] is True and saturation_report['characteristic']==0
        assert saturation_report['all_parameters_checked'] is True and saturation_report['weighted_homogeneity_checked'] is True
        assert saturation_report['parameters']==list(range(1,r+1))
        emit('PUBLIC_PRESENTATION_EQUALS_FULL_KERNEL',method='multigrading, exact dehomogenization and full characteristic-zero Hilbert parameter regularity')
        return public
    if case==174:
        from native_checks.native_colons import verify_parameter_colons
        colon_report=verify_parameter_colons(public,nu,orders,degrees,0,emit)
        assert colon_report['all_parameter_saturations_equal'] is True and colon_report['characteristic']==0
        assert colon_report['parameters']==list(range(1,r+1))
        emit('PUBLIC_PRESENTATION_EQUALS_FULL_KERNEL',method='multigrading, exact dehomogenization and complete first-colon equalities')
        return public
    emit('PUBLIC_GROEBNER_BASIS_START',relations=len(public.gens()))
    public_rational=rational_model(public)
    public_reduction_ring=P if public_rational is None else public_rational.ring()
    public_gb=(public if public_rational is None else public_rational).groebner_basis()
    emit('PUBLIC_GROEBNER_BASIS_COMPLETE',generators=len(public_gb))
    lifted_public_gb=None
    def in_public_ideal(f):
        nonlocal lifted_public_gb
        if not f:return True
        normalized=f/f.leading_coefficient()
        if public_rational is not None and all(c in QQ for c in normalized.coefficients()):
            q=public_reduction_ring({tuple(e):QQ(c) for e,c in normalized.dict().items()})
            return q.reduce(public_gb)==0
        if lifted_public_gb is None:lifted_public_gb=[lift_polynomial(g,P) for g in public_gb]
        return f.reduce(lifted_public_gb)==0
    for k in range(r):
        emit('PUBLIC_SATURATION_EQUALITY_START',parameter=k+1)
        calculate=lambda k=k:saturate_step(public,k)
        saturated=cache(f'public_saturated_t{k+1}',P,calculate) if cache else calculate()
        # I is contained in I:t^infinity by definition. This checks the other
        # inclusion, so equality here proves absence of all t-power torsion.
        assert all(in_public_ideal(f) for f in saturated.gens()), f'Public ideal is not saturated at t{k+1}'
        emit('PUBLIC_SATURATION_EQUALITY_COMPLETE',parameter=k+1,generators=len(saturated.gens()))
    emit('PUBLIC_PRESENTATION_EQUALS_FULL_KERNEL',method='multigrading, exact dehomogenization and separate saturations')
    return public
