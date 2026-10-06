#!/usr/bin/env sage -python
"""Supplementary exact CE02/03/05/06/10/12 checks for the SL4 catalogue.

Run with Sage's Python: --repo SNAPSHOT --output-dir NEW [--paper EXTERNAL.tex].
Geometric YES/NO conclusions are inputs established by the main verifier and
the cited theorems. This program does not reconstruct resolutions or Cox rings.
"""
import argparse
from collections import Counter
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, type=Path)
    parser.add_argument('--paper', type=Path, help='Optional external manuscript to hash')
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    repo, out = args.repo.resolve(), args.output_dir.resolve()
    paper = args.paper.resolve() if args.paper is not None else None
    source = repo/'manuscript106/catalogue/catalogue.json'
    if not source.is_file() or (paper is not None and not paper.is_file()):
        parser.error('The catalogue and any supplied paper must exist')
    if out == repo or repo in out.parents or out in repo.parents:
        parser.error('Output must be outside the input repository and cannot contain it')
    if paper is not None and (out == paper or out in paper.parents):
        parser.error('Output cannot contain the input paper')
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        parser.error('Output directory must be new or empty')
    out.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    report = {
        'status': 'RUNNING', 'complete': False, 'checks': {},
        'scope': 'Fresh target matrix closures, full rational Molien sums, '
                 'abstract-group identifications and isomorphisms, and exact '
                 'elementary obstructions. CE10 transforms accepted all106 '
                 'age-class counts; the main catalogue verifier must establish '
                 'those counts. Geometric YES/NO conclusions are not reproved here.',
        'input_sha256': {'catalogue': digest(source), 'program': digest(Path(__file__))},
        'input_paths': {'repo': str(repo), 'catalogue': str(source)},
        'paper_binding': {'status': 'not_requested'},
    }
    if paper is not None:
        report['input_sha256']['paper'] = digest(paper)
        report['input_paths']['paper'] = str(paper)
        report['paper_binding'] = {
            'status': 'hashed',
            'scope': 'The complete supplied paper is hashed; this is not a TeX semantic parser.'}

    def save():
        temporary = out/'report.json.tmp'
        temporary.write_text(json.dumps(report, indent=2)+'\n')
        temporary.replace(out/'report.json')

    save()
    try:
        from sage.all import QQ, ZZ, PolynomialRing, identity_matrix, matrix, vector
        from sage.libs.gap.libgap import libgap
        from sage.env import SAGE_VERSION
        report['runtime'] = {'python': sys.version, 'sage': SAGE_VERSION}
        rows = json.loads(source.read_text())
        require([r['index'] for r in rows] == list(range(1, 107)), 'Catalogue indices')
        records = {r['index']: r for r in rows}
        require(Counter(r['decision'] for r in rows) == {'YES': 61, 'NO': 45},
                'Unexpected accepted decision labels')
        one = identity_matrix(QQ, 4)
        one.set_immutable()
        groups, generators, gap_groups = {}, {}, {}
        P = PolynomialRing(QQ, 't')
        t = P.gen()
        K = P.fraction_field()

        def freeze(a):
            a.set_immutable()
            return a

        def close(gens, bound):
            found, queue = {one}, [one]
            for a in queue:
                for g in gens:
                    b = freeze(a*g)
                    if b not in found:
                        found.add(b)
                        queue.append(b)
                        require(len(queue) <= bound, 'Closure exceeds asserted order')
            return found

        def group(i):
            if i not in groups:
                gens = [freeze(matrix(QQ, g)) for g in records[i]['actual_generators']]
                require(all(g.nrows() == g.ncols() == 4 and g.det() == 1 and
                            all(x in ZZ for x in g.list()) for g in gens), 'Integral SL4 input')
                groups[i] = close(gens, records[i]['order'])
                generators[i] = gens
                require(len(groups[i]) == records[i]['order'], 'Wrong target group order')
            return groups[i]

        def junior_generated(i):
            g = group(i)
            juniors = [a for a in g if (a-one).rank() == 2]
            return close(juniors, len(g)) == g

        def gap_group(i):
            group(i)
            if i not in gap_groups:
                gap_groups[i] = libgap.Group([libgap(g) for g in generators[i]])
                require(int(gap_groups[i].Size()) == len(groups[i]), 'GAP group order')
            return gap_groups[i]

        def molien(i):
            # The characteristic distribution is freshly reconstructed here,
            # independently of the distribution saved in the catalogue.
            distribution = Counter(tuple((matrix(P, one)-t*matrix(P, a)).det().list())
                                   for a in group(i))
            answer = sum(K(n)/P(list(poly)) for poly, n in distribution.items())/len(group(i))
            return answer, [{'det_I_minus_tg': list(map(str, poly)), 'multiplicity': n}
                            for poly, n in sorted(distribution.items())]

        def series_data(f):
            return {'rational_function': str(f),
                    'numerator_ascending': list(map(str, f.numerator().list())),
                    'denominator_ascending': list(map(str, f.denominator().list()))}

        # CE02: literal target group and its maximal scalar cyclic subgroup.
        g7 = group(7)
        a = freeze(matrix.diagonal(QQ, [-1, -1, 1, 1]))
        b = freeze(matrix.diagonal(QQ, [1, 1, -1, -1]))
        minus = freeze(-one)
        require(g7 == close([a, b], 4) and len(g7) == 4, 'Case7 diagonal model')
        require(all(g*g == one for g in g7) and a*b == b*a, 'Case7 is C2 x C2')
        scalar = {one, minus}
        require(scalar < g7, 'Scalar subgroup inclusion')
        cyclic_orders = []
        for g in g7:
            cyclic = close([g], 4)
            cyclic_orders.append(len(cyclic))
            require(not (scalar < cyclic), 'Scalar subgroup is not maximal cyclic')
        require(int((minus-one).rank())//2 == 2, 'Scalar involution age')
        half = QQ(1)/2
        junior_lattice_points = [v for v in product([QQ(0), half, QQ(1)], repeat=4)
                                if sum(v) == 1 and
                                len({x-x.floor() for x in v}) == 1]
        require(set(junior_lattice_points) == {tuple(v) for v in one.rows()},
                'Scalar subgroup lattice junior simplex')
        fractional = vector(QQ, [half]*4)
        require(any(x not in ZZ for x in fractional) and all(x in ZZ for x in 2*fractional),
                'Scalar lattice has index2 over Z4')
        require(fractional == vector(QQ, [half, half, 0, 0]) +
                vector(QQ, [0, 0, half, half]), 'Whole-group fractional decomposition')
        report['checks']['CE02'] = {
            'status': 'PASS', 'case': 7, 'group_order': 4, 'abstract_group': 'C2 x C2',
            'element_generated_cyclic_orders': sorted(cyclic_orders),
            'scalar_subgroup_maximal_cyclic': True, 'nonidentity_scalar_age': 2,
            'scalar_junior_simplex_points': [list(map(str, v)) for v in junior_lattice_points],
            'own_lattice_fractional_point_not_in_junior_semigroup': True,
            'geometry': 'The product of two A1 resolutions is a mathematical argument; '
                        'the main toric verification separately checks existence.'}
        print('CE02_PASS', flush=True)
        save()

        # CE06: equality in QQ(t), not agreement of a finite Taylor truncation.
        m, distributions = {}, {}
        for i in [38, 83, 45, 92, 93]:
            m[i], distributions[i] = molien(i)
        expected = K((1-t**12)**2)/((1-t**2)**2*(1-t**6)**4)
        require(m[83] == m[45] == expected, 'First full Molien collision')
        require(m[92] == m[93], 'Second full Molien collision')
        require(junior_generated(83) and junior_generated(45), 'First collision junior generation')
        for yes, no in [(83, 45), (92, 93)]:
            require(records[yes]['decision'] == 'YES' and records[no]['decision'] == 'NO',
                    'Unexpected collision geometry labels')
        report['checks']['CE06'] = {
            'status': 'PASS', 'method': 'Fresh exact matrix closures and rational-function equality in QQ(t)',
            'pairs': [[83, 45], [92, 93]], 'first_pair_junior_generated': True,
            'series': {str(i): series_data(m[i]) for i in [83, 45, 92, 93]},
            'fresh_characteristic_distributions': {str(i): distributions[i] for i in [83, 45, 92, 93]},
            'geometric_decisions': 'Reused from separately established geometry'}
        print('CE06_PASS', flush=True)

        # CE05: the reduced numerator has roots off the unit circle.
        F = t**12+2*t**8+2*t**6+2*t**4+1
        Q = PolynomialRing(QQ, 'z')
        z = Q.gen()
        cubic = z**3-z+2
        require(m[38].numerator() == F and F.gcd(m[38].denominator()) == 1,
                'Binary-tetrahedral reduced Molien numerator')
        require(K(F) == t**6*((K(t)**2+K(t)**(-2))**3-(K(t)**2+K(t)**(-2))+2),
                'Numerator cubic substitution')
        require(cubic.discriminant() == -104, 'Cubic discriminant')
        report['checks']['CE05'] = {
            'status': 'PASS', 'case': 38, 'molien': series_data(m[38]),
            'fresh_characteristic_distribution': distributions[38],
            'cubic': str(cubic), 'cubic_discriminant': -104,
            'numerator_denominator_coprime': True,
            'deduction': 'A real cubic of negative discriminant has nonreal roots. '
                         'For |t|=1, t^2+t^-2 is real. Each nonreal cubic root has '
                         'a nonzero preimage under that substitution, so the reduced '
                         'numerator has a root off the unit circle. A complete-intersection '
                         'Hilbert series has only roots of unity as zeros or poles.',
            'geometric_existence': 'Established separately by SieveD and cited theorems'}
        print('CE05_PASS', flush=True)
        save()

        # CE12: identify each actual matrix group and verify an isomorphism.
        pairs = []
        for yes, no, expected_id in [(87, 45, [36, 13]), (104, 105, [24, 6])]:
            ids = [list(map(int, gap_group(i).IdGroup().sage())) for i in [yes, no]]
            require(ids == [expected_id, expected_id], 'Wrong SmallGroups identification')
            iso = libgap.IsomorphismGroups(gap_group(yes), gap_group(no))
            require(iso != libgap.fail and bool(iso.IsBijective()), 'No verified group isomorphism')
            forms = []
            for i in [yes, no]:
                require(junior_generated(i), 'CE12 group not junior-generated')
                positions = list(combinations(range(4), 2))
                basis = []
                for u, v in positions:
                    B = matrix(QQ, 4, 4)
                    B[u, v], B[v, u] = 1, -1
                    basis.append(B)
                equations = []
                for g in generators[i]:
                    differences = [g.transpose()*B*g-B for B in basis]
                    equations.extend([[D[u, v] for D in differences] for u, v in positions])
                kernel = matrix(QQ, equations).right_kernel()
                kb = list(kernel.basis())
                pf = lambda v: v[0]*v[5]-v[1]*v[4]+v[2]*v[3]
                # The generic Pfaffian is a homogeneous quadratic. Values at
                # basis vectors and pairwise sums determine every coefficient.
                require(all(pf(v) == 0 for v in kb+[a+b for a, b in combinations(kb, 2)]),
                        'CE12 representation preserves a symplectic form')
                forms.append({'case': i, 'invariant_alternating_form_dimension': int(kernel.dimension()),
                              'nondegenerate_invariant_form': False})
            require(records[yes]['decision'] == 'YES' and records[no]['decision'] == 'NO',
                    'CE12 accepted geometry labels')
            pairs.append({'cases': [yes, no], 'small_group_id': expected_id,
                          'actual_gap_isomorphism_bijective': True,
                          'junior_generated': True, 'alternating_forms': forms})
        report['checks']['CE12'] = {'status': 'PASS', 'pairs': pairs,
                                   'geometric_decisions': 'Reused from separately established geometry'}
        print('CE12_PASS', flush=True)
        save()

        # CE10 is a bookkeeping check on accepted all106 class counts.
        # It deliberately does not claim to re-enumerate all conjugacy classes.
        all106 = []
        for row in rows:
            ages = [1, row['junior_classes'], row['age2_classes']]
            require(all(isinstance(n, int) and n >= 0 for n in ages), 'Nonintegral age counts')
            A = sum(P(n)*t**j for j, n in enumerate(ages))
            E = sum(P(n)*t**(4-j) for j, n in enumerate(ages))
            require(K(E) == t**4*K(A)(1/t) and E(1) == sum(ages), 'Stringy polynomial transform')
            all106.append({'case': row['index'], 'age_class_counts': ages,
                           'compact_support_stringy_polynomial': str(E),
                           'stringy_euler_from_accepted_class_count': int(E(1))})
        scalar_group = group(2)
        require(scalar_group == {one, minus}, 'Case2 scalar matrix group')
        require(records[2]['junior_classes'] == 0 and records[2]['age2_classes'] == 1,
                'Scalar conjugacy class counts')
        report['checks']['CE10'] = {
            'status': 'PASS', 'catalogue_entries': len(all106),
            'all106_conjugacy_counts_recomputed_here': False,
            'identity': 'E_st,c(t)=t^4 A_G(t^-1); E_st,c(1)=number of conjugacy classes',
            'hard_lefschetz': 'The proof uses real finite-order SL4 matrices: '
                              'nonreal eigenvalues occur in conjugate pairs, so '
                              'age(g)=age(g^-1)=rank(g-I)/2 for every g. '
                              'The main catalogue verifier checks the finite groups.',
            'scalar_case2_matrix_group_freshly_checked': True,
            'scalar_stringy_polynomial': 't^4+t^2', 'cases': all106,
            'manual_theorems': 'Batyrev identifies the formal polynomial with the '
                               'compact-support stringy E-function; the numerical '
                               'identity alone does not prove existence of a resolution.'}
        print('CE10_PASS', flush=True)
        # This selects the complete list rather than checking only named examples.
        # Fresh group counts/forms for these examples run in the separate CE03/07 task.
        deficits = []
        for row in rows:
            b2, b4 = row['junior_classes'], row['age2_classes']
            symmetric_square = b2*(b2+1)//2
            if row['decision'] == 'YES' and b4 > symmetric_square:
                deficits.append({'case': row['index'], 'b2': b2, 'b4': b4,
                                 'symmetric_square_dimension': symmetric_square,
                                 'deficit': b4-symmetric_square})
        require([(r['case'], r['b2'], r['b4']) for r in deficits] ==
                [(35, 2, 4), (38, 2, 4), (55, 2, 5), (64, 4, 12),
                 (97, 1, 2), (98, 2, 5)], 'Complete CE03 deficit table')
        report['checks']['CE03_table_selection'] = {
            'status': 'PASS', 'catalogue_entries_scanned': len(rows), 'cases': deficits,
            'scope': 'Exact complete-table selection from accepted age counts and '
                     'geometric decisions; neither is recomputed by this selection.'}
        print('CE03_TABLE_SELECTION_PASS', flush=True)
        expected_checks = {'CE02', 'CE05', 'CE06', 'CE10', 'CE12', 'CE03_table_selection'}
        require(set(report['checks']) == expected_checks and
                all(c['status'] == 'PASS' for c in report['checks'].values()), 'Incomplete checks')
        report.update(status='PASS', complete=True,
                      fresh_matrix_group_cases=sorted(groups),
                      seconds=round(time.monotonic()-started, 3))
        save()
        print('ALL_PAPER_CLAIM_CHECKS_PASS', flush=True)
    except BaseException as error:
        report.update(status='FAILED', complete=False, error=repr(error),
                      seconds=round(time.monotonic()-started, 3))
        save()
        raise


if __name__ == '__main__':
    main()
