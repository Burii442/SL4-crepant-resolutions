"""Recompute complete and initial generator maps from literal junior matrices.

load_maps(case, target_ring=None) returns Sage polynomials, eigenbases and
integer weights. The separate group-binding verifier checks that these
matrices represent every junior class of the actual catalogue group.
"""
from pathlib import Path
import json
from sage.all import QQ, CyclotomicField, PolynomialRing, matrix, vector, identity_matrix, sage_eval, cyclotomic_polynomial
ROOT=Path(__file__).resolve().parent.parent

def load_maps(case,target_ring=None):
    case=int(case);a=json.loads((ROOT/str(case)/'invariants.json').read_text())
    witness_file=ROOT/'binding_verification'/('special_groups.json' if case in [114,138,231,233] else 'standard_groups.json')
    w=json.loads(witness_file.read_text())[str(case)];order=w['cyclotomic_order'];K=CyclotomicField(order,'zeta');zeta=K.gen()
    initial_bases_path=ROOT/'binding_verification'/f'{case}_initial_bases.json'
    initial_bases=json.loads(initial_bases_path.read_text()) if initial_bases_path.exists() else None
    T=PolynomialRing(QQ,'zeta');mini=a.get('cyclotomic_minpoly');input_order=next(n for n in range(1,97) if T(cyclotomic_polynomial(n))==T(mini)) if mini else 1
    assert order%input_order==0;oldzeta=zeta**(order//input_order)
    def mat(rows,root):return matrix(K,[[K(sage_eval(str(s),locals={'zeta':root})) for s in row] for row in rows])
    raw=a.get('canonical_juniors',a.get('junior_representatives_in_coordinates'))
    juniors=[mat(m,oldzeta) for m in raw] if raw is not None else [mat(m,zeta) for m in w['junior_matrices']]
    R=PolynomialRing(K,a['polynomial_coordinate_order']);xx=R.gens();loc=dict(zip(a['polynomial_coordinate_order'],xx));loc['zeta']=oldzeta
    F=[R(sage_eval(s,locals=loc)) for s in a['generator_polynomials']];Id=identity_matrix(K,4)
    full=[];initial=[];eigenbases=[];weight_rows=[]
    for k,(junior,r) in enumerate(zip(juniors,a['junior_orders'])):
        root=K(-1) if r==2 else zeta**(order//r)
        assert r==2 or order%r==0
        if initial_bases is not None or 'junior_eigenbases' in a:
            if initial_bases is not None:
                assert initial_bases['case']==case and initial_bases['cyclotomic_order']==order
                B=mat(initial_bases['junior_eigenbases'][k],zeta)
            else:B=mat(a['junior_eigenbases'][k],oldzeta)
            diag=B.inverse()*junior*B
            assert diag.is_diagonal()
            weights=[next(e for e in range(r) if root**e==diag[j,j]) for j in range(4)]
        else:
            basis=[];weights=[]
            for e in range(r):
                b=(junior-root**e*Id).right_kernel().basis();basis.extend(b);weights.extend([e]*len(b))
            B=matrix(K,basis).transpose()
        assert B.det()!=0 and sum(weights)==r
        images=list(B*vector(R,xx));fs=[f(*images) for f in F];initial_row=[]
        for j,f in enumerate(fs):
            vals={e:sum(c*w for c,w in zip(e,weights)) for e in f.dict()};nu=min(vals.values())
            assert nu==a['valuation_matrix'][k][j]
            assert all((v-nu)%r==0 for v in vals.values())
            initial_row.append(R({e:c for e,c in f.dict().items() if vals[e]==nu}))
        full.append(fs);initial.append(initial_row);eigenbases.append(B);weight_rows.append(weights)
    if target_ring is not None:
        L=target_ring.base_ring()
        if L==QQ:
            def coefficient(c):return QQ(c)
        else:
            assert L.defining_polynomial()(oldzeta)==0
            basis=matrix(QQ,[(oldzeta**j).list()+[QQ(0)]*(K.degree()-len((oldzeta**j).list())) for j in range(L.degree())]).transpose()
            converted={}
            def coefficient(c):
                if c not in converted:
                    coords=basis.solve_right(vector(QQ,K(c).list()+[QQ(0)]*(K.degree()-len(K(c).list()))))
                    converted[c]=sum(v*L.gen()**j for j,v in enumerate(coords))
                return converted[c]
        def convert(f):return target_ring({tuple(e):coefficient(c) for e,c in f.dict().items()})
        F=[convert(f) for f in F];full=[[convert(f) for f in row] for row in full];initial=[[convert(f) for f in row] for row in initial]
    return {'generators':F,'junior_full_generators':full,'junior_initial_generators':initial,'junior_eigenbases':eigenbases,'junior_weights':weight_rows,'juniors':juniors,'valuation_matrix':a['valuation_matrix'],'junior_orders':a['junior_orders'],'finite_degree_matrix':a.get('finite_degree_matrix',a['valuation_matrix']),'finite_degree_orders':a.get('finite_degree_orders',a['junior_orders'])}
