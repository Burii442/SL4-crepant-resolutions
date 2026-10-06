"""Exact membership in I+(t_k), via all parameter residue classes.

If I descends under e_j=t_j^r_j, first set t_k=0. The remaining polynomial
extension from QQ[u,e_{j != k}] to QQ[u,t_{j != k}] is finite free, with basis
the monomials t^a, 0<=a_j<r_j. A candidate belongs to the extended target iff
EVERY residue component belongs to I(e_k=0). We recompute its complete QQ
Groebner basis, project every source basis generator, and reduce all components.
"""
from pathlib import Path
import hashlib
import json
import time


def verify_target_containment(ideal, candidates, nu, orders, degrees, parameter,
                              emit=lambda *a, **kw: None, variable_order=None,
                              evidence_directory=None):
    """Typed exact inputs; parameter and variable_order use zero-based positions.

    Every source generator and every complete candidate must have rational
    monic coefficients after one common nonzero scalar normalization. This
    includes candidate terms killed by setting the selected parameter to zero;
    arbitrary mixtures of nonrational coefficients are outside this backend.
    The source parameter powers must descend exactly. Candidates may contain
    arbitrary parameter exponents; they
    are decomposed into all classes, never rounded or dropped. PASS establishes
    precisely containment of the supplied candidates in ideal+(t_parameter).
    It makes no separate claim that the candidate list is a complete kernel.
    """
    from sage.all import QQ, ZZ, PolynomialRing, TermOrder
    from sage.matrix.matrix0 import Matrix
    from sage.rings.polynomial.multi_polynomial_ideal import MPolynomialIdeal
    started=time.monotonic()
    assert isinstance(ideal,MPolynomialIdeal) and isinstance(nu,Matrix)
    P=ideal.ring();K=P.base_ring();candidates=list(candidates)
    assert K.is_field() and K.is_exact() and K.characteristic()==0
    assert all(f.parent() is P for f in candidates)
    assert all(v in ZZ for v in list(orders)+list(degrees)+list(nu.list()))
    orders=list(map(int,orders));degrees=list(map(int,degrees));n=len(degrees);r=len(orders)
    assert n>0 and r>0 and P.ngens()==n+r and nu.nrows()==r and nu.ncols()==n
    assert all(v>0 for v in orders+degrees)
    assert parameter in ZZ and 0<=parameter<r
    parameter=int(parameter)
    ids=list(range(n-1,-1,-1))+list(range(n,n+r)) if variable_order is None else list(variable_order)
    assert all(v in ZZ for v in ids)
    ids=list(map(int,ids));assert len(ids)==n+r and set(ids)==set(range(n+r))
    factor=max([1]+[(sum(int(nu[k,j]) for k in range(r))+1)//degrees[j]+1 for j in range(n)])
    weights=[factor*degrees[j]-sum(int(nu[k,j]) for k in range(r)) for j in range(n)]+orders
    assert all(w>0 for w in weights)
    ordered_weights=[weights[j] for j in ids]
    names=['q'+str(j+1) for j in ids]
    Q=PolynomialRing(QQ,n+r,names=names,order=TermOrder('wdegrevlex',ordered_weights))
    divisors=[1]*n+orders
    def homogeneous(f,w):
        return len({sum(int(e[j])*w[j] for j in range(len(w))) for e in f.dict()})<=1
    def descend(f):
        if not f:return Q.zero()
        scale=f.leading_coefficient();data={}
        for e,c in f.dict().items():
            c=c/scale
            assert c in QQ,'Source monic coefficients must be rational'
            assert all(int(e[j])%divisors[j]==0 for j in range(n+r)),'Source powers must descend exactly'
            target=tuple(int(e[j])//divisors[j] for j in ids)
            assert target not in data
            data[target]=QQ(c)
        result=Q(data)
        assert homogeneous(result,ordered_weights),'Source must have the actual positive weighted grading'
        return result
    source=[descend(f) for f in ideal.gens()]
    def basis(forms,ring,w):
        answer=ring.ideal(forms).groebner_basis(algorithm='libsingular:std')
        answer=[g/g.leading_coefficient() for g in answer if g]
        assert all(homogeneous(g,w) for g in answer)
        return answer
    def digest_polynomials(forms):
        return hashlib.sha256(json.dumps(list(map(str,forms)),separators=(',',':')).encode()).hexdigest()
    folder=Path(evidence_directory).resolve() if evidence_directory else None
    if folder:
        folder.mkdir(parents=True,exist_ok=True)
        assert not list(folder.iterdir()),'Use a fresh evidence directory'
    emit('TARGET_RESIDUE_INPUTS_CHECKED',source_generators=len(source),candidates=len(candidates),parameter=parameter+1,positive_weights=ordered_weights)
    emit('TARGET_RESIDUE_FULL_QQ_BASIS_START')
    G=basis(source,Q,ordered_weights)
    emit('TARGET_RESIDUE_FULL_QQ_BASIS_COMPLETE',generators=len(G))
    removed=ids.index(n+parameter);keep=[j for j in range(n+r) if j!=removed]
    kept_ids=[ids[j] for j in keep]
    quotient_weights=[ordered_weights[j] for j in keep]
    W=PolynomialRing(QQ,len(keep),names=[names[j] for j in keep],order=TermOrder('wdegrevlex',quotient_weights))
    projected=[]
    for g in G:
        h=W({tuple(int(e[j]) for j in keep):c for e,c in g.dict().items() if int(e[removed])==0})
        if h:projected.append(h)
    emit('TARGET_RESIDUE_FULL_QUOTIENT_BASIS_START',projected_source_generators=len(G),nonzero_projected_generators=len(projected))
    B=basis(projected,W,quotient_weights)
    emit('TARGET_RESIDUE_FULL_QUOTIENT_BASIS_COMPLETE',generators=len(B))
    if folder:
        (folder/'complete_QQ_basis.txt').write_text('\n'.join(map(str,G))+'\n')
        (folder/'complete_target_quotient_basis.txt').write_text('\n'.join(map(str,B))+'\n')
    report=dict(characteristic=0,parameter=parameter+1,parameter_orders=orders,
        variable_order=[i+1 for i in ids],quotient_variable_order=[i+1 for i in kept_ids],
        ordered_positive_weights=ordered_weights,source_generators=len(source),
        source_polynomials_sha256=digest_polynomials(source),
        complete_source_basis_generators=len(G),complete_source_basis_sha256=digest_polynomials(G),
        full_source_basis_projected=True,projected_nonzero_generators=len(projected),
        complete_target_basis_generators=len(B),complete_target_basis_sha256=digest_polynomials(B),
        source_parameter_power_descent_verified=True,source_positive_homogeneity_verified=True,
        candidate_count=len(candidates),candidate_results=[])
    total_components=0;nonzero_components=0
    for index,f in enumerate(candidates,1):
        scale=f.leading_coefficient() if f else K.one()
        components={};projected_data={}
        for exponent,coefficient in f.dict().items():
            coefficient=coefficient/scale
            assert coefficient in QQ,'Candidate monic coefficients must be rational'
            if int(exponent[n+parameter])!=0:continue
            exponent=tuple(map(int,exponent));coefficient=QQ(coefficient)
            projected_data[exponent]=coefficient
            residue=tuple(exponent[n+j]%orders[j] if j!=parameter else 0 for j in range(r))
            target=tuple(exponent[j]//divisors[j] for j in kept_ids)
            component=components.setdefault(residue,{})
            assert target not in component,'Residue decomposition must be injective term by term'
            component[target]=coefficient
        reconstructed={}
        for residue,component in components.items():
            assert len(residue)==r and residue[parameter]==0 and all(0<=residue[j]<orders[j] for j in range(r))
            for exponent,coefficient in component.items():
                original=[0]*(n+r)
                for position,j in enumerate(kept_ids):
                    original[j]=int(exponent[position])*divisors[j]+(residue[j-n] if j>=n else 0)
                original=tuple(original)
                assert original not in reconstructed
                reconstructed[original]=coefficient
        assert reconstructed==projected_data,'All projected candidate terms must be reconstructed exactly'
        result=dict(index=index,input_terms=len(f.dict()),projected_terms=len(projected_data),
                    residue_components=len(components),exact_reconstruction=True,components=[])
        for residue,component in sorted(components.items()):
            q=W(component);remainder=q.reduce(B) if B else q
            zero=bool(remainder==0)
            item=dict(residue=list(residue),terms=len(component),zero_normal_form=zero)
            if not zero:item['nonzero_normal_form']=str(remainder);nonzero_components+=1
            result['components'].append(item);total_components+=1
        result['contained']=all(v['zero_normal_form'] for v in result['components'])
        report['candidate_results'].append(result)
        emit('TARGET_RESIDUE_CANDIDATE_COMPLETE',**result)
    assert [v['index'] for v in report['candidate_results']]==list(range(1,len(candidates)+1))
    contained=all(v['contained'] for v in report['candidate_results'])
    report.update(status='PASS' if contained else 'NOT_CONTAINED',all_contained=contained,
        all_candidates_checked=True,all_residue_components_checked=True,
        candidate_reconstruction_verified=True,checked=len(candidates),
        checked_residue_components=total_components,nonzero_residue_components=nonzero_components,
        residue_elapsed_seconds=time.monotonic()-started)
    if folder:(folder/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    emit('TARGET_RESIDUE_MEMBERSHIP_COMPLETE',**{key:value for key,value in report.items() if key!='candidate_results'})
    return report
