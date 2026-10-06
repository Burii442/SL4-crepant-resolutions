#!/usr/bin/env sage-python
"""Check the public Cox coordinate bindings and multigradings.

Run: sage -python check_cox_models.sage.py [case ...]
These checks do not replace the full-kernel and MUVAK certificates in the
case source manifests. Modular evaluations are explicitly consistency checks,
not characteristic-zero identity proofs. --symbolic additionally substitutes
the ordered F_j into every displayed relation over its exact number field.
"""
from sage.all import QQ, GF, PolynomialRing, NumberField, matrix, vector, prod
from pathlib import Path
import json, sys, hashlib, time
ROOT = Path(__file__).resolve().parent
symbolic = '--symbolic' in sys.argv
cases = [x for x in sys.argv[1:] if x != '--symbolic'] or sorted(p.parent.name for p in ROOT.glob('[0-9]*/model.json'))
results = []
for case in cases:
    started = time.time()
    m = json.loads((ROOT/case/'model.json').read_text())
    a = json.loads((ROOT/case/'invariants.json').read_text())
    n, r = m['invariant_generator_count'], m['junior_count']
    D = matrix(QQ, m['valuation_grading']); Q = matrix(QQ, m['primitive_grading'])
    nu = matrix(QQ, a['valuation_matrix'])
    assert D.nrows()==r and D.ncols()==n+r and Q.dimensions()==D.dimensions()
    assert D[:,:n] == -nu
    assert D[:,n:] == matrix.diagonal(QQ,a['junior_orders'])
    assert D.row_space() == Q.row_space()
    assert Q.rank() == r and all(x in QQ and x.denominator()==1 for x in Q.list())
    # Surjectivity of the column lattice: Smith elementary divisors are all 1.
    from sage.all import ZZ
    assert matrix(ZZ,Q).elementary_divisors() == [1]*r
    names=m['coordinate_order']; assert len(names)==n+r
    mini=a.get('cyclotomic_minpoly')
    coeffs=QQ
    if any('zeta' in f for f in m['equations']+a['generator_polynomials']):
        Z=PolynomialRing(QQ,'zeta'); coeffs=NumberField(Z(mini),'zeta')
    U=PolynomialRing(coeffs,names); us=U.gens(); equations=[U(s) for s in m['equations']]
    assert len(equations)==m['relation_count'] and all(f for f in equations)
    for f in equations:
        weights={tuple(Q*vector(QQ,e)) for e in f.exponents()}
        assert len(weights)==1, ('inhomogeneous relation',case)
    # Choose a split finite field and a nonzero evaluation of every t_l.
    p=1009; K=GF(p); Z=PolynomialRing(K,'zeta')
    z=Z(mini).roots()[0][0] if mini else K(0)
    coeffmap=(lambda c: sum(K(v)*z**j for j,v in enumerate(c.list()))) if coeffs is not QQ else (lambda x:K(x))
    X=PolynomialRing(K,a['polynomial_coordinate_order'])
    X0=PolynomialRing(coeffs,a['polynomial_coordinate_order'])
    phi=[X({e:coeffmap(c) for e,c in X0(f).dict().items()}) for f in a['generator_polynomials']]
    trials=0
    for shift in (0,7,19):
        xs=[K(2+shift),K(3+shift),K(5+shift),K(11+shift)]
        ts=[K(13+shift+2*j) for j in range(r)]
        image=[phi[j](*xs)*prod(ts[l]**(-ZZ(nu[l,j])) for l in range(r)) for j in range(n)]
        image += [ts[l]**a['junior_orders'][l] for l in range(r)]
        UK=PolynomialRing(K,names)
        for f in equations:
            fk=UK({e:coeffmap(c) for e,c in f.dict().items()})
            assert fk(*image)==0, ('modular image mismatch',case,str(f)[:100])
        trials+=1
    if symbolic:
        F=coeffs
        if mini and coeffs is QQ and any('zeta' in f for f in a['generator_polynomials']):
            Z=PolynomialRing(QQ,'zeta'); F=NumberField(Z(mini),'zeta')
        PX=PolynomialRing(F,a['polynomial_coordinate_order'])
        fs=[PX(s) for s in a['generator_polynomials']]+[PX(1)]*r
        for j,f in enumerate(equations):
            assert f(*fs)==0, ('exact image mismatch',case,j+1)
    result={'case':int(case),'relations':len(equations),'coordinates':n+r,
       'raw_valuation_binding':'PASS','primitive_grading_and_homogeneity':'PASS',
       'modular_image_consistency':{'prime':p,'evaluation_points':trials,'result':'PASS'},
       'exact_relation_images':'PASS' if symbolic else 'not requested',
       'elapsed_seconds':round(time.time()-started,3)}
    results.append(result);print(json.dumps(result),flush=True)
(ROOT/'cox_model_checks.json').write_text(json.dumps(results,indent=2)+'\n')
