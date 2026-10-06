"""Full C2 kernel of Case 173 juniors 2/3 by exact character recovery.

Diagonal normalization commutes with the sign action. The full intersection
can therefore be computed over QQ and transported back to K24. Exactly
checked C2-homogeneous monic graphs reduce the intermediate ring; every
component is retained by recovering its sign after localization and taking
the complete contraction. The denominator is nonzero in both components.
"""
from pathlib import Path
import hashlib
import json
import time
from sage.all import QQ, ZZ, PolynomialRing, TermOrder
from sage.libs.singular.function_factory import singular_function
from special_initial173_j23 import compute_initial_kernel


def compute_tagged_kernel(forms, U, junior, degrees, tags, finite_orders,
                          emit=lambda *a, **k: None, graph_path=None, recovery_path=None):
    started = time.monotonic()
    if list(finite_orders) != [2] or len(tags) != 1 or len(tags[0]) != 25:
        raise ValueError('Expected the full C2 character on all 25 variables')
    if any(t not in ZZ for t in tags[0]):
        raise ValueError('Finite character degrees must be integers')
    character = [int(t) % 2 for t in tags[0]]
    ordinary, transport = compute_initial_kernel(
        forms, U, junior, degrees, emit, return_transport=True)
    normalized = transport['normalized_forms']
    scales = transport['scales']
    Q = normalized[0].parent()
    V = PolynomialRing(QQ, ['u'+str(j+1) for j in range(25)])
    to_original_ring = U.hom([U.gen(j)*scales[j] for j in range(25)], U)
    rational_relations = []
    for f in ordinary.gens():
        g = to_original_ring(f)
        if g:
            g /= g.leading_coefficient()
            if any(c not in QQ for c in g.coefficients()):
                raise ValueError('Unsigned ideal did not descend under diagonal normalization')
            rational_relations.append(V({tuple(e): QQ(c) for e, c in g.dict().items()}))
    evaluate = V.hom(normalized, Q)
    assert all(evaluate(g) == 0 for g in rational_relations)

    def homogeneous(g, indices):
        return len({sum(e[q]*character[j] for q, j in enumerate(indices)) % 2
                    for e in g.exponents()}) <= 1

    path = Path(graph_path) if graph_path else Path(__file__).with_name('173_initial23_character_graphs.json')
    record = json.loads(path.read_text())[str(junior)]
    live = set(range(25))
    projection = list(V.gens())
    extensions = []
    for row in record['graphs']:
        target = int(row['target'])-1
        f = V(row['relation'])
        assert target in live and f.derivative(V.gen(target)) == 1
        assert all(not e[j] for e in f.exponents() for j in range(25) if j not in live)
        assert evaluate(f) == 0 and homogeneous(f, list(range(25)))
        replacement = V.gen(target)-f
        substitution = V.hom([replacement if j == target else V.gen(j) for j in range(25)], V)
        projection = [substitution(g) for g in projection]
        extensions.append(f)
        live.remove(target)
    core = [int(j)-1 for j in record['core_indices']]
    assert len(core) == len(set(core)) == 12 and live == set(core) and len(extensions) == 13
    project = V.hom(projection, V)
    A = PolynomialRing(QQ, ['u'+str(j+1) for j in core],
                       order=TermOrder('wdegrevlex', [int(degrees[j]) for j in core]))
    reduced = []
    for f in rational_relations:
        g = project(f)
        assert all(not e[j] for e in g.exponents() for j in range(25) if j not in live)
        if g:
            reduced.append(A({tuple(e[j] for j in core): c for e, c in g.dict().items()}))
    ordinary_core = A.ideal(reduced)
    recovery_file = Path(recovery_path) if recovery_path else Path(__file__).with_name('173_initial23_sign_recovery.json')
    recovery = json.loads(recovery_file.read_text())[str(junior)]
    def compress(f):
        f = project(V(f))
        assert all(not e[j] for e in f.exponents() for j in range(25) if j not in live)
        return A({tuple(e[j] for j in core): c for e, c in f.dict().items()})
    even = compress(recovery['even'])
    odd = -compress(recovery['odd'])
    p, q = [core.index(int(j)-1) for j in recovery['coordinate_indices']]
    assert p != q and character[core[p]] == 0 and character[core[q]] == 1
    variables = list(A.gens())
    cp = even.derivative(variables[p]); cq = odd.derivative(variables[q])
    assert cp.is_constant() and cp != 0 and cq.is_constant() and cq != 0
    assert even.derivative(variables[q]) == 0 and odd.derivative(variables[p]) == 0
    changed = list(variables); changed[p] = even; changed[q] = odd
    inverse = list(variables)
    inverse[p] = (variables[p]-(even-cp*variables[p]))/cp
    inverse[q] = (variables[q]-(odd-cq*variables[q]))/cq
    theta = A.hom(changed, A); back = A.hom(inverse, A)
    assert all(theta(back(v)) == v == back(theta(v)) for v in variables)
    core_degrees = [int(degrees[j]) for j in core]
    core_character = [character[j] for j in core]
    for j, f in enumerate(changed):
        assert {sum(e[k]*core_degrees[k] for k in range(12)) for e in f.exponents()} == {core_degrees[j]}
        assert {sum(e[k]*core_character[k] for k in range(12)) % 2 for e in f.exponents()} == {core_character[j]}
    core_evaluate = A.hom([normalized[j] for j in core], Q)
    changed_forms = [core_evaluate(f) for f in changed]
    assert changed_forms[p] == changed_forms[q] != 0
    changed_ordinary = A.ideal([back(f) for f in ordinary_core.gens()])
    changed_evaluate = A.hom(changed_forms, Q)
    assert all(changed_evaluate(f) == 0 for f in changed_ordinary.gens())
    emit('INITIAL173_GRADED_SIGN_COORDINATES_PROVED', junior=junior,
         coordinate_indices=[core[p]+1, core[q]+1], both_compositions_identity=True,
         same_nonzero_physical_image=True, full_character_order=2,
         recovery_sha256=hashlib.sha256(recovery_file.read_bytes()).hexdigest())
    from rational_tags import recovered_tag_kernel
    changed_kernel = recovered_tag_kernel(changed_ordinary, changed_forms, A,
        [core_character], [2], [(p,q)], core_degrees, emit)
    # The checked equivariant automorphism transports the full contraction,
    # which is exactly the intersection of the two character components.
    intersection = A.ideal([theta(f) for f in changed_kernel.gens()])
    # Exact homogeneous minimal generation keeps the same complete ideal.
    minimal = list(singular_function('minbase')(intersection))
    minimal_ideal = A.ideal(minimal)
    full_gb = intersection.groebner_basis()
    minimal_gb = minimal_ideal.groebner_basis()
    assert all(f.reduce(full_gb) == 0 for f in minimal)
    assert all(f.reduce(minimal_gb) == 0 for f in intersection.gens())
    assert all(homogeneous(f, core) for f in minimal)
    core_evaluate = A.hom([normalized[j] for j in core], Q)
    assert all(core_evaluate(f) == 0 for f in minimal)
    restore = A.hom([U.gen(j)/scales[j] for j in core], U)
    restore_graph = V.hom([U.gen(j)/scales[j] for j in range(25)], U)
    result = [restore(f) for f in minimal]+[restore_graph(f) for f in extensions]
    actual = U.hom(forms, forms[0].parent())
    assert all(actual(f) == 0 and homogeneous(f, list(range(25))) for f in result)
    emit('INITIAL173_FULL_TAGGED_KERNEL_PROVED', junior=junior,
         complete_components=2, finite_order=2, core_generators=len(minimal),
         generators=len(result), minimal_ideal_both_inclusions=True,
         graph_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
         character_seconds=time.monotonic()-started)
    return U.ideal(result)
