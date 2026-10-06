#!/usr/bin/env python3
"""Portable exact Sieve E checks. Run with sage -python; see README.md."""
from pathlib import Path
import csv
import sys
from common import main


def verify(context):
    from sage.all import QQ, PolynomialRing, matrix, vector
    PUB = context.legacy
    inputs = context.inputs
    bind, read = context.bind, context.read

    catalogue = {r['index']: r for r in read(PUB/'catalogue.json')}
    matrix_binding = context.example_matrices('E', 100, 236,
                                              catalogue[236]['actual_generators'])
    incidence = list(csv.DictReader(bind(PUB/'criteria_incidence.csv').open()))
    positive = sorted(int(r['index']) for r in incidence if r['test'] == 'E' and r['outcome'] == 'YES')
    assert positive == list(range(72,78))+list(range(85,89))+list(range(132,138))+list(range(234,238))
    assert all(catalogue[i]['decision'] == 'YES' for i in positive)
    groups = {}

    def immutable(M):
        M.set_immutable()
        return M

    def group(i):
        if i not in groups:
            generators = [matrix(QQ,g) for g in catalogue[i]['actual_generators']]
            seen = {immutable(matrix.identity(QQ,4))}
            todo = list(seen)
            while todo:
                g = todo.pop()
                for h in generators:
                    k = immutable(g*h)
                    if k not in seen:
                        seen.add(k)
                        todo.append(k)
            assert len(seen) == catalogue[i]['order']
            groups[i] = seen
        return groups[i]

    witnesses = {r['index']: r for r in read(PUB/'representative_conjugacies.json')['witnesses']}
    transfers = []
    for i in positive:
        j = catalogue[i]['representative']
        assert j in [72,85,132,234,236]
        if i != j:
            w = witnesses[i]
            assert w['representative'] == j
            P = matrix(QQ,w['P'])
            assert P.det() != 0
            Pi = P.inverse()
            assert {immutable(P*g*Pi) for g in group(j)} == group(i)
        else:
            group(i)
        transfers.append({'index':i,'representative':j,'order':len(groups[i])})
    print('E: all twenty matrix groups and representative transfers verified',flush=True)

    ring_reports = []
    for i in [72,85]:
        folder = PUB/str(i)/'invariant_ring'
        d = read(folder/'ring_certificate.json')
        matrices = read(folder/'input_matrices.json')
        assert matrices == catalogue[i]['actual_generators']
        R = PolynomialRing(QQ,names=['x1','x2','x3','x4'])
        xs = R.gens()
        fs = [R(f) for f in d['generators']]
        assert [f.degree() for f in fs] == d['weights']
        for g in matrices:
            image = list(matrix(QQ,g)*vector(xs))
            assert all(f(*image) == f for f in fs)
        T = PolynomialRing(QQ,names=['x1','x2','x3','x4']+[f'u{k}' for k in range(1,7)],order='lex')
        x,u = T.gens()[:4],T.gens()[4:]
        graph = T.ideal([u[k]-T(str(fs[k])) for k in range(6)])
        eliminated = [f for f in graph.groebner_basis() if not any(f.degree(z) for z in x)]
        relations = T.ideal([T(f) for f in d['minimal_relations']])
        assert T.ideal(eliminated) == relations
        assert relations.dimension() == 8  # four unused x coordinates plus dimension four
        assert relations.gens()[0].gcd(relations.gens()[1]) == 1
        if i == 72:
            a,b,c,f,e,dvar = u
            displayed = [2*dvar**2-c*(a*a-f),e*e-b*(2*f-a*a)]
        else:
            a,b,c,f,dvar,e = u
            displayed = [3*dvar**2-c*(f-2*a**3),e*e-b*(22*a**3-9*f)]
        assert T.ideal(displayed) == relations
        A = PolynomialRing(QQ,'z'); z = A.gen(); K = A.fraction_field()
        molien = sum(K(1)/(matrix.identity(A,4)-z*matrix(A,g)).det() for g in group(i))/len(group(i))
        hilbert = K(1)
        for deg in d['relation_degrees']: hilbert *= 1-z**deg
        for deg in d['weights']: hilbert /= 1-z**deg
        assert molien == hilbert
        ring_reports.append({'index':i,'invariance':True,'full_kernel':True,'regular_sequence':True,'molien_hilbert':True,'displayed_equations':True})
        print(f'E{i}: full invariant ring verified',flush=True)

    # Check every affine chart of the three blow-ups for 72 and 85.
    R = PolynomialRing(QQ,names='a,b,c,d,e,f,v,t,s,A,T,S')
    a,b,c,d,e,f,v,t,s,A,T,S = R.gens()

    def sat(equations,exceptional):
        return R.ideal(equations).saturation(R.ideal(exceptional))[0]

    def smooth_hypersurface(H):
        assert R.ideal([H]+[H.derivative(z) for z in R.gens()]).is_one()

    def centre_order(H,coordinates):
        positions = [R.gens().index(z) for z in coordinates]
        return min(sum(exponents[k] for k in positions) for exponents in H.dict())

    chart_reports = []
    for i in [72,85]:
        first = 2*d*d-c*(a*a-f) if i == 72 else 3*d*d-c*(f-2*a**3)
        L = 2*f-a*a if i == 72 else 22*a**3-9*f
        second = e*e-b*L
        d_equation = 2*d-v*(a*a-f) if i == 72 else 3*d-v*(f-2*a**3)
        c_equation = 2*c*t*t-a*a+f if i == 72 else 3*c*t*t-f+2*a**3
        assert sat([first.subs(c=d*v),second],d) == R.ideal([d_equation,second])
        assert sat([first.subs(d=c*t),second],c) == R.ideal([c_equation,second])
        Lc = a*a-4*c*t*t if i == 72 else 4*a**3-27*c*t*t
        fvalue = a*a-2*c*t*t if i == 72 else 2*a**3+3*c*t*t
        assert L.subs(f=fvalue) == Lc
        for Lchart in [L,Lc]:
            H = e*e-b*Lchart
            factors = list(H.factor())
            assert len(factors) == 1 and factors[0][1] == 1
            assert sat([H.subs(e=b*s)],b) == R.ideal(b*s*s-Lchart)
            assert sat([H.subs(b=e*s)],e) == R.ideal(e-s*Lchart)
            smooth_hypersurface(e-s*Lchart)
        smooth_hypersurface(b*s*s-L)
        H = Lc-b*s*s
        assert R.ideal([H]+[H.derivative(z) for z in R.gens()]).radical() == R.ideal(a,t,s)
        final = [1-4*c*T*T-b*S*S,A*A-4*c-b*S*S,A*A-4*c*T*T-b] if i == 72 else [4*a-27*c*T*T-b*S*S,4*t*A**3-27*c-b*S*S,4*s*A**3-27*c*T*T-b]
        substitutions = [{t:a*T,s:a*S},{a:t*A,s:t*S},{a:s*A,t:s*T}]
        for exceptional,sub,Hfinal in zip([a,t,s],substitutions,final):
            total = H.subs(sub)
            assert total == exceptional**2*Hfinal
            assert sat([total],exceptional) == R.ideal(Hfinal)
            smooth_hypersurface(Hfinal)
        discrepancies = [2-1-centre_order(first,[c,d])-centre_order(second,[c,d]),
                         2-1-centre_order(e*e-b*Lc,[b,e]),
                         3-1-centre_order(H,[a,t,s])]
        assert discrepancies == [0,0,0]
        chart_reports.append({'index':i,'all_chart_saturations':True,'singular_plane':True,'smooth_final_charts':6,'discrepancies':discrepancies})
        print(f'E{i}: saturated blow-up charts and smoothness verified',flush=True)

    # Detailed geometric jobs are fresh unless explicitly supplied with --geometry-runs.
    geometry_runs = context.run_geometry()

    # The compact formula for the example is checked against the full discriminant
    # and the actual centre parametrizations used by the geometry certificates.
    data = read(PUB/'geometry_proofs/236/a5_discriminant_input.json')
    R = PolynomialRing(QQ,names='p,q,r,h,a,b,Q,H,K')
    p,q,r,h,a,b,Q,H,K = R.gens()
    RT = PolynomialRing(R,'T'); T = RT.gen()
    F = T**5+p*T**3+q*T*T+r*T+h
    D = F.discriminant()
    assert D == R(data['discriminant'])
    assert D.subs(q=-q,h=-h) == D
    barD = R(data['central_extension_C2xA5']['presentation'][1].split('=',1)[1])
    assert barD.subs(Q=q*q,H=q*h,K=h*h) == D
    for polynomial,stratum in zip([(T-a)**3*(T*T+3*a*T+b),(T*T-a*T+b)**2*(T+2*a)],data['strata']):
        assert polynomial[4] == 0
        assert [polynomial[k] for k in [3,2,1,0]] == [R(stratum['parametrization'][name]) for name in ['p','q','r','h']]
        assert polynomial.discriminant() == 0
    bind(Path(__file__).resolve())
    result = {'status':'PASS','positive':positive,'negative':[],
              'representatives':[72,85,132,234,236],'all_matrix_transfers':transfers,
              'invariant_rings':ring_reports,'explicit_chart_checks':chart_reports,
              'geometry_runs':geometry_runs,
              'example_236':{**matrix_binding,'order':120,'discriminant_verified':True,
                             'central_quotient_equation':True,'stratum_parametrizations':True,
                             'geometry_evidence':geometry_runs[-1]['report']},
              'input_sha256':inputs,
              'scope':'Group, ring and explicit 72/85 charts are recomputed in this invocation. Detailed 132/234/236 evidence has the mode recorded per run; supplied prior reports are hash-bound, not rerun. Crepancy also uses the adjunction and fibre arguments in the paper.'}
    return result


if __name__ == '__main__':
    sys.exit(main('E', verify, Path(__file__)))
