"""Exact parameter saturation from full characteristic-zero Hilbert series.

For a positively graded quotient A and a homogeneous parameter e of degree d,
 the multiplication sequence gives H(A/e)=(1-z^d)H(A)+z^d H(Ann_A(e)).
 Thus equality of the full rational functions certifies injectivity of e.
 Positive weights make every graded piece finite dimensional. The proof uses
 complete freshly computed Groebner bases, never truncated series.

Generatorwise scalar normalization descends to QQ, and parameter powers
 e_k=t_k**r_k descend to independent variables. The field extension and the
 parameter-power extension are faithfully flat; injectivity by e_k implies
 injectivity by t_k. Every input polynomial is checked for weighted
 homogeneity AFTER that exact descent. No caller-side grading assumption is
 used. A leading-monomial shortcut is valid when the entire fresh complete
 basis has no leading monomial involving the selected parameter.
"""


def verify_parameter_saturations(ideal, nu, orders, degrees,
                                 emit=lambda *a, **k: None,
                                 variable_order=None):
    """Check all parameters of a typed Sage ideal using a shared fresh QQ basis.

    The input ring has n ordinary variables followed by r parameters. The
    supplied permutation is zero based; reported variable and parameter
    indices are one based. PASS certifies every full parameter saturation.
    PARAMETER_TORSION records a proved characteristic-zero failure, including
    the full nonzero annihilator Hilbert series, rather than an unfinished run.
    Errors and interruptions propagate and cannot yield a certificate.
    """
    from sage.all import QQ, ZZ, PolynomialRing, TermOrder
    from sage.matrix.matrix0 import Matrix
    from sage.rings.polynomial.multi_polynomial_ideal import MPolynomialIdeal
    import hashlib, json, time
    started = time.monotonic()
    assert isinstance(ideal, MPolynomialIdeal), 'A typed Sage multivariate polynomial ideal is required'
    assert isinstance(nu, Matrix), 'A typed Sage valuation matrix is required'
    P = ideal.ring()
    K = P.base_ring()
    assert K.is_field() and K.is_exact() and K.characteristic() == 0, 'An exact characteristic-zero field is required'
    assert all(v in ZZ for v in list(orders) + list(degrees) + list(nu.list())), 'Integer numerical data are required'
    orders, degrees = list(map(int, orders)), list(map(int, degrees))
    n, r = len(degrees), len(orders)
    assert n > 0 and r > 0 and P.ngens() == n + r, 'Ring dimensions do not match degrees and orders'
    assert nu.nrows() == r and nu.ncols() == n, 'Valuation matrix dimensions do not match'
    assert all(v > 0 for v in orders + degrees), 'Orders and ordinary degrees must be positive'
    if variable_order is None:
        ids = list(range(n - 1, -1, -1)) + list(range(n, n + r))
    else:
        assert all(v in ZZ for v in variable_order), 'Variable positions must be integers'
        ids = list(map(int, variable_order))
        assert len(ids) == n + r and set(ids) == set(range(n + r)), 'Variable order must be a complete zero-based permutation'
    factor = max([1] + [(sum(int(nu[k, j]) for k in range(r)) + 1) // degrees[j] + 1 for j in range(n)])
    weights = [factor * degrees[j] - sum(int(nu[k, j]) for k in range(r)) for j in range(n)] + orders
    assert all(w > 0 for w in weights), 'The actual Hilbert grading must be positive'
    ordered_weights = [weights[j] for j in ids]
    names = ['q' + str(j + 1) for j in ids]
    Q = PolynomialRing(QQ, n + r, names=names, order=TermOrder('wdegrevlex', ordered_weights))
    divisors = [1] * n + orders

    def homogeneous(f, actual_weights):
        return len({sum(int(e[j]) * actual_weights[j] for j in range(len(actual_weights)))
                    for e in f.dict()}) <= 1

    def descend(f):
        if not f:
            return Q.zero()
        scale = f.leading_coefficient()
        data = {}
        for exponent, coefficient in f.dict().items():
            coefficient /= scale
            assert coefficient in QQ, 'Every nonzero generator must have rational monic coefficients'
            assert all(int(exponent[j]) % divisors[j] == 0 for j in range(n + r)), 'Every parameter exponent must descend exactly'
            data[tuple(int(exponent[j]) // divisors[j] for j in ids)] = QQ(coefficient)
        g = Q(data)
        assert homogeneous(g, ordered_weights), 'Every descended input generator must be homogeneous for the actual positive weights'
        return g

    def polynomial_hash(polynomials):
        return hashlib.sha256(json.dumps(list(map(str, polynomials)), separators=(',', ':')).encode()).hexdigest()

    def full_series(h):
        return dict(numerator=list(map(str, h.numerator().list())),
                    denominator=list(map(str, h.denominator().list())),
                    coefficient_order='ascending', full_rational_function=str(h))

    def full_basis(polynomials, ring, actual_weights):
        # The ideal and its basis are constructed afresh from the supplied
        # polynomials. No caller-provided cache or stored basis is consumed.
        basis = ring.ideal(polynomials).groebner_basis(algorithm='libsingular:std')
        basis = [g / g.leading_coefficient() for g in basis if g]
        assert all(homogeneous(g, actual_weights) for g in basis), 'Computed basis lost the checked grading'
        return basis

    def hilbert_from_complete_basis(basis, ring, actual_weights):
        # All leading monomials of the full fresh basis generate the full
        # initial ideal. Using that monomial ideal also avoids recomputing the
        # nonmonomial basis under a different Sage groebner_basis cache key.
        return ring.ideal([g.lm() for g in basis]).hilbert_series(grading=actual_weights)

    source = [descend(f) for f in ideal.gens()]
    emit('HILBERT_REGULARITY_INPUTS_CHECKED', parameters=r, source_generators=len(source),
         checked_input_terms=sum(len(f.dict()) for f in source),
         positive_weights=ordered_weights, weighted_homogeneity_checked=True)
    emit('HILBERT_REGULARITY_FULL_QQ_BASIS_START')
    G = full_basis(source, Q, ordered_weights)
    emit('HILBERT_REGULARITY_FULL_QQ_BASIS_COMPLETE', generators=len(G))
    Hbase = hilbert_from_complete_basis(G, Q, ordered_weights)
    emit('HILBERT_REGULARITY_FULL_BASE_SERIES_COMPLETE', **full_series(Hbase))
    result = dict(characteristic=0, coefficient_field='QQ', source_coefficient_field=str(K),
                  parameters=list(range(1, r + 1)), parameter_orders=orders,
                  variable_order=[j + 1 for j in ids], ordered_positive_weights=ordered_weights,
                  positive_weight_factor=factor, weighted_homogeneity_checked=True,
                  homogeneous_input_generators_checked=len(source),
                  checked_input_terms=sum(len(f.dict()) for f in source),
                  exact_rational_coefficient_descent=True, exact_parameter_power_descent=True,
                  source_generators=len(source), source_polynomials_sha256=polynomial_hash(source),
                  complete_standard_basis_generators=len(G),
                  complete_standard_basis_sha256=polynomial_hash(G),
                  complete_basis_homogeneity_checked=True,
                  full_base_hilbert_series=full_series(Hbase), parameter_results=[])
    leading_exponents = [tuple(map(int, g.lm().exponents()[0])) for g in G]
    z = Hbase.parent().gen()
    for k in range(r):
        position = ids.index(n + k)
        degree = ordered_weights[position]
        assert degree == orders[k] and degree > 0
        emit('HILBERT_REGULARITY_PARAMETER_START', parameter=k + 1, degree=degree)
        if all(e[position] == 0 for e in leading_exponents):
            item = dict(parameter=k + 1, degree=degree,
                        method='every leading monomial of the full QQ basis omits the parameter',
                        complete_basis_leading_monomials_checked=len(G),
                        characteristic_zero_injectivity=True, full_parameter_saturation_equal=True)
        else:
            keep = [j for j in range(n + r) if j != position]
            quotient_weights = [ordered_weights[j] for j in keep]
            W = PolynomialRing(QQ, len(keep), names=[names[j] for j in keep],
                               order=TermOrder('wdegrevlex', quotient_weights))
            projected = []
            # Images of the entire generating basis generate I+(e)/(e).
            # Terms divisible by the removed parameter vanish; all other
            # exponent vectors project injectively to the remaining variables.
            for g in G:
                h = W({tuple(int(e[j]) for j in keep): c
                       for e, c in g.dict().items() if int(e[position]) == 0})
                assert homogeneous(h, quotient_weights)
                if h:
                    projected.append(h)
            emit('HILBERT_REGULARITY_FULL_QUOTIENT_BASIS_START', parameter=k + 1,
                 source_basis_generators_projected=len(G), nonzero_projected_generators=len(projected))
            B = full_basis(projected, W, quotient_weights)
            emit('HILBERT_REGULARITY_FULL_QUOTIENT_BASIS_COMPLETE', parameter=k + 1, generators=len(B))
            Hquot = Hbase.parent()(hilbert_from_complete_basis(B, W, quotient_weights))
            expected = (1 - z**degree) * Hbase
            difference = Hquot - expected
            cross_product = Hquot.numerator() * expected.denominator() - expected.numerator() * Hquot.denominator()
            equal = bool(difference == 0)
            assert equal == bool(cross_product == 0), 'Full rational-function and cross-product comparisons disagree'
            item = dict(parameter=k + 1, degree=degree,
                        method='full weighted Hilbert identity from two complete QQ Groebner bases',
                        source_basis_generators_projected=len(G),
                        projected_nonzero_generators=len(projected),
                        quotient_variable_count=len(keep), quotient_variables=[j + 1 for j in ids if j != n + k],
                        quotient_positive_weights=quotient_weights,
                        complete_quotient_basis_generators=len(B),
                        complete_quotient_basis_sha256=polynomial_hash(B),
                        full_quotient_hilbert_series=full_series(Hquot),
                        expected_quotient_hilbert_series=full_series(expected),
                        full_rational_functions_equal=equal, exact_cross_product_zero=bool(cross_product == 0),
                        cross_product_coefficients=list(map(str, cross_product.list())),
                        characteristic_zero_injectivity=equal, full_parameter_saturation_equal=equal)
            if not equal:
                item['full_annihilator_hilbert_series'] = full_series(difference / z**degree)
        result['parameter_results'].append(item)
        emit('HILBERT_REGULARITY_PARAMETER_COMPLETE', **item)
    assert [v['parameter'] for v in result['parameter_results']] == list(range(1, r + 1))
    complete = all(v['full_parameter_saturation_equal'] for v in result['parameter_results'])
    result.update(status='PASS' if complete else 'PARAMETER_TORSION',
                  all_parameters_checked=True, all_parameter_colons_equal=complete,
                  all_parameter_saturations_equal=complete,
                  parameter_torsion=[v['parameter'] for v in result['parameter_results'] if not v['characteristic_zero_injectivity']])
    emit('HILBERT_REGULARITY_COMPLETE', hilbert_elapsed_seconds=time.monotonic() - started, **result)
    return result
