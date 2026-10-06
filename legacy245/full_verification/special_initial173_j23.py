"""Full unsigned initial kernels for Case 173 juniors 2 and 3.

All supplied identities are checked against the literal input forms.  A
reversible linear coordinate change and an injective monomial embedding put
the normalized maps over QQ.  Seventeen monic graphs reduce to eight forms.
Three binary forms have a complete principal kernel (irreducibility and
Jacobian rank two).  Three equations solve three of the five mixed forms
after localization; the other two are algebraically independent over the
binary fraction field.  Full saturation is therefore exactly the kernel.

This returns ONLY the unsigned kernel.  The caller must still perform the
complete finite-character intersection and the Cox containment criterion.
"""
from pathlib import Path
import hashlib
import json
import time
from sage.all import QQ, ZZ, PolynomialRing, TermOrder, matrix


def compute_initial_kernel(forms, U, junior, degrees, emit=lambda *a, **k: None,
                           hint_path=None, return_transport=False):
    started = time.monotonic()
    if junior not in (2, 3) or len(forms) != 25 or U.ngens() != 25:
        raise ValueError('Expected Case 173 junior 2 or 3 with all 25 forms')
    X = forms[0].parent()
    K = X.base_ring()
    if (X.ngens() != 4 or not K.is_field() or not K.is_exact()
            or K.characteristic() != 0 or U.base_ring() != K):
        raise ValueError('Expected four physical variables and the same characteristic-zero field')
    if len(degrees) != 25 or any(d not in ZZ or d <= 0 for d in degrees):
        raise ValueError('Physical degrees must be positive integers')
    degrees = list(map(int, degrees))
    for f, d in zip(forms, degrees):
        if f.parent() != X or not f or any(sum(e) != d for e in f.exponents()):
            raise ValueError('A literal form has the wrong parent or physical degree')
    s = 2*K.gen()**4 - 1
    if s*s != -3:
        raise ValueError('The proposed quadratic coordinate scalar is invalid')
    Y = PolynomialRing(K, ['a', 'b', 'y', 'w'])
    a, b, y, w = Y.gens()
    x1, x2, x3, x4 = X.gens()
    if junior == 2:
        binary = (a+s*b, 2*s*b)
        fourth = s*w
        inverse = [x1-x2/2, x2/(2*s), x3**3, x3*x4/s]
        linear_det = 2*s
    else:
        binary = (a, s*b)
        fourth = w
        inverse = [x1, x2/s, x3**3, x3*x4]
        linear_det = s
    assert linear_det != 0
    exponent_matrix = matrix(ZZ, [[1,0,0,0], [0,1,0,0], [0,0,3,1], [0,0,0,1]])
    assert exponent_matrix.det() == 3
    back = Y.hom(inverse, X)
    Q = PolynomialRing(QQ, ['a', 'b', 'y', 'w'])
    normalized, scales = [], []
    physical_weights = (1, 1, 3, 2)
    for f, degree in zip(forms, degrees):
        transformed = Y.zero()
        for e, c in f.dict().items():
            difference = e[2]-e[3]
            if difference < 0 or difference % 3:
                raise ValueError('A physical monomial is outside the injective compression')
            compressed = (e[0], e[1], difference//3, e[3])
            assert tuple(exponent_matrix*matrix(ZZ, 4, 1, compressed).column(0)) == tuple(e)
            transformed += c*binary[0]**e[0]*binary[1]**e[1]*y**compressed[2]*fourth**e[3]
        assert back(transformed) == f
        if any(sum(v*t for v, t in zip(e, physical_weights)) != degree
               for e in transformed.exponents()):
            raise ValueError('Compression lost the original physical grading')
        scale = transformed.leading_coefficient()
        assert scale != 0
        g = transformed/scale
        if any(c not in QQ for c in g.coefficients()):
            raise ValueError('The normalized transformed map is not rational')
        scales.append(scale)
        normalized.append(Q(g))
    path = Path(hint_path) if hint_path else Path(__file__).with_name('173_initial23_localization_hints.json')
    payload = json.loads(path.read_text())['juniors'][str(junior)]
    V = PolynomialRing(QQ, ['u'+str(i+1) for i in range(25)])
    evaluate = V.hom(normalized, Q)
    live = set(range(25))
    extensions = []
    for record in payload['graphs']:
        target = int(record['target'])-1
        g = V(record['relation'])
        if target not in live or g.derivative(V.gen(target)) != 1:
            raise ValueError('A graph is not monic linear in a live variable')
        if any(e[j] for e in g.exponents() for j in range(25) if j not in live):
            raise ValueError('A graph uses an already removed variable')
        if evaluate(g) != 0:
            raise ValueError('A graph has nonzero physical image')
        extensions.append(g)
        live.remove(target)
    ids = list(map(int, payload['core_indices']))
    assert len(ids) == len(set(ids)) == 8
    assert live == {j-1 for j in ids} and len(extensions) == 17
    A = PolynomialRing(QQ, ['u'+str(j) for j in ids],
                       order=TermOrder('wdegrevlex', [degrees[j-1] for j in ids]))
    lookup = {j: A.gen(i) for i, j in enumerate(ids)}
    physical = {j: normalized[j-1] for j in ids}
    phi = A.hom([physical[j] for j in ids], Q)
    pure = list(map(int, payload['pure_indices']))
    free = list(map(int, payload['free_indices']))
    solved = list(map(int, payload['solved_indices']))
    assert len(pure) == 3 and len(free) == 2 and len(solved) == 3
    assert set(pure+free+solved) == set(ids) and len(set(pure+free+solved)) == 8
    pure_variables = {lookup[j] for j in pure}
    for j in pure:
        assert all(e[2]+e[3] == 0 for e in physical[j].exponents())
    for j in free+solved:
        assert all(e[2]+e[3] == 1 for e in physical[j].exponents())
    q = A(payload['binary_relation'])
    assert set(q.variables()) <= pure_variables and phi(q) == 0
    factors = list(q.factor())
    assert len(factors) == 1 and factors[0][1] == 1 and not q.is_constant()
    binary_jacobian = matrix(Q, [[physical[j].derivative(Q.gen(k)) for k in (0, 1)]
                                for j in pure[:2]])
    assert binary_jacobian.det() != 0
    # The prime physical binary kernel has height one and contains q.
    # Irreducibility implies that its complete kernel is exactly (q).
    linear = [A(f) for f in payload['linear_relations']]
    assert len(linear) == 3 and all(phi(f) == 0 for f in linear)
    coefficients = matrix(A, [[f.derivative(lookup[j]) for j in solved] for f in linear])
    assert all(set(c.variables()) <= pure_variables for c in coefficients.list())
    allowed_residual = pure_variables | {lookup[j] for j in free}
    for f, row in zip(linear, coefficients.rows()):
        residual = f-sum(c*lookup[j] for c, j in zip(row, solved))
        assert set(residual.variables()) <= allowed_residual
    determinant = coefficients.det()
    h = A(payload['localizer'])
    assert set(h.variables()) <= pure_variables
    assert A.ideal(q).reduce(determinant-h) == 0
    assert phi(h) != 0
    physical_free = matrix(Q, [[physical[j].derivative(Q.gen(k)) for k in (2, 3)] for j in free])
    assert physical_free.det() != 0
    hints = [A(f) for f in payload['accelerators']]
    assert all(phi(f) == 0 for f in hints)
    emit('INITIAL173_RATIONAL_LOCALIZATION_PROVED', junior=junior,
         full_forms=25, core_indices=ids, graph_count=17,
         physical_weights=list(physical_weights), monomial_determinant=3,
         binary_kernel=str(q), localizer=str(h), free_indices=free,
         finite_character_intersection_required=True)
    # After inverting h, J is a polynomial algebra in the two free variables
    # over the embedded binary algebra.  Hence J:h^infinity is the full kernel.
    J = A.ideal([q]+linear+hints)
    complete = J.saturation(A.ideal(h))[0]
    kernel = list(complete.groebner_basis())
    assert all(phi(f) == 0 for f in kernel)
    assert complete.dimension() == 4
    to_U = A.hom([U.gen(j-1)/scales[j-1] for j in ids], U)
    all_to_U = V.hom([U.gen(j)/scales[j] for j in range(25)], U)
    result = [to_U(f) for f in kernel]+[all_to_U(f) for f in extensions]
    actual = U.hom(forms, X)
    assert all(actual(f) == 0 for f in result)
    emit('INITIAL173_UNSIGNED_FULL_KERNEL_PROVED', junior=junior,
         core_generators=len(kernel), full_generators=len(result),
         localization_seconds=time.monotonic()-started,
         hint_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
         finite_character_intersection_required=True)
    ideal = U.ideal(result)
    if return_transport:
        return ideal, dict(normalized_forms=normalized, scales=scales)
    return ideal
